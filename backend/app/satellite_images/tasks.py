import logging
import os

from celery.exceptions import CeleryError
from commons.models import StatusEnum
from commons.mongo import get_mongo_db_client
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from PIL import Image
from PIL.ExifTags import TAGS
from pymongo.errors import PyMongoError

from celery import chain, shared_task

from .models import SatelliteImage

logger = logging.getLogger(__name__)


class SatelliteImageProcessStatusNotificationStrategy:
    def send_notification(self, image_name, recipient_email):
        raise NotImplementedError("Method needs to be implemented!")


class StatusFailedStrategy(SatelliteImageProcessStatusNotificationStrategy):
    def send_notification(self, image_name, recipient_email):
        subject = "Task Completed"
        message = render_to_string(
            "emails/processing_image_result.html",
            {
                "mood": "troubled",
                "recipient": recipient_email,
                "image_name": image_name,
                "status": "unsuccessfully",
                "completed_at": timezone.now().strftime("%d/%m/%Y, %H:%M:%S"),
            },
        )
        from_email = "your_email@example.com"
        recipient_list = [recipient_email]

        send_mail(subject, message, from_email, recipient_list)


class StatusSuccessfulStrategy(SatelliteImageProcessStatusNotificationStrategy):
    def send_notification(self, image_name, recipient_email):
        subject = "Task Completed"
        message = render_to_string(
            "emails/processing_image_result.html",
            {
                "mood": "happy",
                "recipient": recipient_email,
                "image_name": image_name,
                "status": "successfully",
                "completed_at": timezone.now().strftime("%d/%m/%Y, %H:%M:%S"),
            },
        )
        from_email = "your_email@example.com"
        recipient_list = [recipient_email]

        send_mail(subject, message, from_email, recipient_list)


class SatelliteImageProcessStatusEmailSender:
    notification_strategy = None
    image_name = None
    recipient_email = None

    def __init__(
        self,
        notification_strategy: SatelliteImageProcessStatusNotificationStrategy,
        recipient_email,
        image_name,
    ):
        self.notification_strategy = notification_strategy
        self.recipient_email = recipient_email
        self.image_name = image_name

    def send_notification(self):
        self.notification_strategy.send_notification(
            self.image_name, self.recipient_email
        )


class SatelliteImageDataToMongoSaver:
    """
    Handle Saving SatelliteImageData details to mongodb.
    """

    def __init__(self, data):
        self.data = data
        self.client = None

    def _remove_documents_of_image_if_already_exist(self):
        """
        make sure only one document with id exists
        """
        dbname = self.client[SatelliteImage.MONGO_DB_NAME]
        satellite_images = dbname[SatelliteImage.MONGO_COLLECTION_NAME]

        satellite_images.delete_many(
            {"satellite_image_id": self.data["satellite_image_id"]}
        )

    def _put_data_into_mongo(self):
        dbname = self.client[SatelliteImage.MONGO_DB_NAME]
        satellite_images = dbname[SatelliteImage.MONGO_COLLECTION_NAME]
        satellite_images.insert_one(self.data)

    def save_satellite_image_data(self):
        self.client = get_mongo_db_client()
        self._remove_documents_of_image_if_already_exist()
        self._put_data_into_mongo()
        self.client.close()


class SatelliteImageProcessor:
    def __init__(self, image_path, remove_after_processing=True) -> None:
        self.image_path = image_path
        self.data = None
        self.remove_after_processing = remove_after_processing

    def _process_exifdata(self, exifdata):
        """
        Exif is ugly and not human readable. It needs to be processed
        """
        result = {}
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)

            data = exifdata.get(tag_id)
            # decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            result[tag] = str(data)
        return result

    def _process_satellite_image(self):
        image = Image.open(self.image_path)
        exif_data = self._process_exifdata(image.getexif())

        data = {
            "width": image.size[0],
            "height": image.size[1],
            "format": image.format,
            **exif_data,
        }
        return data

    def _remove_image(self):
        os.remove(self.image_path)

    def get_processed_satellite_image_data(self):
        if not self.data:
            self.data = self._process_satellite_image()
            if self.remove_after_processing:
                self._remove_image()
        return self.data


@shared_task
def send_email_notification(status, recipient_email, image_name):
    logger.info("Sending notification")
    strategy = (
        StatusSuccessfulStrategy()
        if status == StatusEnum.COMPLETED.value
        else StatusFailedStrategy()
    )
    sender = SatelliteImageProcessStatusEmailSender(
        strategy, recipient_email, image_name
    )
    sender.send_notification()
    return status


@shared_task
def process_satellite_image(image_path):
    logger.info("Processing image {image_path}")

    processor = SatelliteImageProcessor(image_path)
    return processor.get_processed_satellite_image_data()


@shared_task
def save_satellite_image_data_to_mongo(data, satellite_image_id):
    logger.info(f"Saving data to mongo {satellite_image_id}")

    data["satellite_image_id"] = str(satellite_image_id)
    saver = SatelliteImageDataToMongoSaver(data)
    saver.save_satellite_image_data()
    return StatusEnum.COMPLETED.value


@shared_task
def set_satellite_image_status(status, satellite_image_id):
    logger.info(f"Changing {satellite_image_id} status to {status}")

    obj = SatelliteImage.objects.get(id=satellite_image_id)
    obj.set_status(status)


@shared_task
def handle_processing_satellite_image_service(
    satellite_image_id,
    image_path,
    image_name,
    uploader_email,
):
    # return set_satellite_image_status.delay(
    #     StatusEnum.FAILED.value, satellite_image_id
    # )
    # return save_satellite_image_data_to_mongo({"abc": 123}, satellite_image_id)
    try:
        handler = chain(
            process_satellite_image.s(image_path)
            | save_satellite_image_data_to_mongo.s(satellite_image_id)
            | send_email_notification.s(uploader_email, image_name)
            | set_satellite_image_status.s(satellite_image_id)
        )
        handler()
    except (CeleryError, PyMongoError) as exc:
        logger.error(f"Error during task execution: {exc}")
        handler = chain(
            send_email_notification.s(
                StatusEnum.FAILED.value, uploader_email, image_name
            )
            | set_satellite_image_status.s(satellite_image_id)
        )
        handler()
