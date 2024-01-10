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

    def test_menu_list_returns_only_users_data(self):
        SatelliteImageFactory()
        SatelliteImageFactory(uploader=self.user)
        SatelliteImageFactory(uploader=self.user)
        url = reverse("satellite_images:satellite_images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    @mock.patch("satellite_images.views.SatelliteImageViewSet._get_details")
    def test_menu_list_returns_only_users_data_with_mongo_data(self, mock_get_details):
        SatelliteImageFactory()
        img1 = SatelliteImageFactory(uploader=self.user)
        img2 = SatelliteImageFactory(uploader=self.user)

        mock_get_details.return_value = {
            str(img1.id): {
                "_id": "659f03322736e6f85c8c8498",
                "abc": 123,
                "satellite_image_id": str(img1.id),
            },
            str(img2.id): {
                "_id": "659f05fd754afe7dcdcc431b",
                "width": 600,
                "height": 600,
                "format": "PNG",
                "satellite_image_id": str(img2.id),
            },
        }
        url = reverse("satellite_images:satellite_images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data,
            [
                {
                    "id": str(img1.id),
                    "title": img1.title,
                    "created_at": img1.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "status": img1.status,
                    "processing_data": {
                        "_id": "659f03322736e6f85c8c8498",
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
                        "_id": "659f05fd754afe7dcdcc431b",
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
