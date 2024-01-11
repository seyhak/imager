from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tests.factories.satellite_image import SatelliteImageFactory
from tests.factories.user import UserFactory


class TestSatelliteImageViewSet(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)

    @mock.patch("satellite_images.views.SatelliteImageViewSet._get_details")
    def test_menu_list_returns_only_users_data_with_mongo_data(self, mock_get_details):
        not_users_img = SatelliteImageFactory()
        img1 = SatelliteImageFactory(uploader=self.user)
        img2 = SatelliteImageFactory(uploader=self.user)

        mock_get_details.return_value = {
            str(not_users_img.id): {
                "some_property": 456,
                "satellite_image_id": str(not_users_img.id),
            },
            str(img1.id): {
                "abc": 123,
                "satellite_image_id": str(img1.id),
            },
            str(img2.id): {
                "width": 600,
                "height": 600,
                "format": "PNG",
                "satellite_image_id": str(img2.id),
            },
        }
        url = reverse("satellite_images:satellite_images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            response.data,
            [
                {
                    "id": str(not_users_img.id),
                    "title": not_users_img.title,
                    "created_at": not_users_img.created_at.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ),
                    "status": not_users_img.status,
                    "processing_data": {
                        "some_property": 456,
                        "satellite_image_id": str(not_users_img.id),
                    },
                },
                {
                    "id": str(img1.id),
                    "title": img1.title,
                    "created_at": img1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "status": img1.status,
                    "processing_data": {
                        "abc": 123,
                        "satellite_image_id": str(img1.id),
                    },
                },
                {
                    "id": str(img2.id),
                    "title": img2.title,
                    "created_at": img2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "status": img2.status,
                    "processing_data": {
                        "width": 600,
                        "height": 600,
                        "format": "PNG",
                        "satellite_image_id": str(img2.id),
                    },
                },
            ],
        )

    def test_menu_list_unauthenticated(self):
        self.client.logout()
        url = reverse("satellite_images:satellite_images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
