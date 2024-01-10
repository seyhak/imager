import os

from commons.models import StatusEnum
from django.core import mail
from django.test import SimpleTestCase, TestCase
from parameterized import parameterized
from PIL import Image
from satellite_images.tasks import (
    SatelliteImageProcessor,
    send_email_notification,
    set_satellite_image_status,
)
from tests.factories.satellite_image import SatelliteImageFactory


class TestSatelliteImageProcessor(SimpleTestCase):
    def test_success_jpg(self):
        image_path = os.path.join(os.path.dirname(__file__), "fixtures/pic.jpg")
        processor = SatelliteImageProcessor(
            image_path=image_path, remove_after_processing=False
        )
        result = processor.get_processed_satellite_image_data()
        self.assertEqual(
            result,
            {
                "width": 584,
                "height": 560,
                "format": "JPEG",
                "ResolutionUnit": "2",
                "ExifOffset": "202",
                "Make": "samsung",
                "Model": "SM-G930F",
                "Software": "G930FXXS4ESAH",
                "Orientation": "1",
                "DateTime": "2019:03:10 09:39:36",
                "YCbCrPositioning": "1",
                "XResolution": "72.0",
                "YResolution": "72.0",
            },
        )

    def test_success_png(self):
        image_path = os.path.join(os.path.dirname(__file__), "fixtures/img.png")
        processor = SatelliteImageProcessor(
            image_path=image_path, remove_after_processing=False
        )
        result = processor.get_processed_satellite_image_data()

        self.assertEqual(result, {"format": "PNG", "height": 636, "width": 720})

    def test_success_removing_after_processing(self):
        image_path = os.path.join(
            os.path.dirname(__file__), "fixtures/test_img_to_remove.png"
        )
        img = Image.new("RGB", (1, 1), color="white")
        img.save(image_path, "JPEG")

        self.assertTrue(os.path.exists(image_path))
        processor = SatelliteImageProcessor(image_path=image_path)

        processor.get_processed_satellite_image_data()

        self.assertFalse(os.path.exists(image_path))


class TestSendEmailNotification(SimpleTestCase):
    def test_send_successful_msg(self):
        result = send_email_notification(
            StatusEnum.COMPLETED.value, "recipient@example.com", "image_name"
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Task Completed")
        self.assertIn("happy", mail.outbox[0].body)
        self.assertIn("successfully", mail.outbox[0].body)

        self.assertEqual(result, StatusEnum.COMPLETED.value)

    def test_send_failed_msg(self):
        result = send_email_notification(
            StatusEnum.FAILED.value, "recipient@example.com", "image_name"
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Task Completed")
        self.assertIn("troubled", mail.outbox[0].body)
        self.assertIn("unsuccessfully", mail.outbox[0].body)

        self.assertEqual(result, StatusEnum.FAILED.value)


class TestSetSatelliteImageStatus(TestCase):
    @parameterized.expand([StatusEnum.COMPLETED.value, StatusEnum.FAILED.value])
    def test_success_(self, next_status):
        image = SatelliteImageFactory()

        self.assertEqual(StatusEnum.PENDING.value, image.status)
        set_satellite_image_status(next_status, str(image.id))

        image.refresh_from_db()
        self.assertEqual(next_status, image.status)
