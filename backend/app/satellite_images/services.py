import logging

from celery.exceptions import CeleryError
from commons.models import StatusEnum
from pymongo.errors import PyMongoError
from satellite_images import tasks

from celery import chain

logger = logging.getLogger(__name__)


class SatelliteImageService:
    """
    Service runs after adding SatelliteImage via Admin.
    It processes image, save data to mongo.
    Then send notification via email.
    Then sets status of SatelliteImage in PGSQL.
    """

    def __init__(self, satellite_image_id, image_path, image_name, uploader_email):
        self.satellite_image_id = satellite_image_id
        self.image_path = image_path
        self.image_name = image_name
        self.uploader_email = uploader_email

    def _handle_processing_satellite_image_service(
        self,
        satellite_image_id,
        image_path,
        image_name,
        uploader_email,
    ):
        try:
            handler = chain(
                tasks.process_satellite_image.s(image_path)
                | tasks.save_satellite_image_data_to_mongo.s(satellite_image_id)
                | tasks.send_email_notification.s(uploader_email, image_name)
                | tasks.set_satellite_image_status.s(satellite_image_id)
            )
            result = handler.apply_async()
            result.get()
        except (CeleryError, PyMongoError) as exc:
            logger.error(f"Error during task execution: {exc}")
            handler = chain(
                tasks.send_email_notification.s(
                    StatusEnum.FAILED.value, uploader_email, image_name
                )
                | tasks.set_satellite_image_status.s(satellite_image_id)
            )
            result = handler.apply_async()

    def handle_service(self):
        self._handle_processing_satellite_image_service(
            self.satellite_image_id,
            self.image_path,
            self.image_name,
            self.uploader_email,
        )
