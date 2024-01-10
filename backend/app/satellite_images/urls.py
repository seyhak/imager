from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SatelliteImageViewSet

router = DefaultRouter()
router.register(r"satellite_images", SatelliteImageViewSet, "satellite_images")

app_name = "satellite_images"
urlpatterns = [
    path("", include(router.urls)),
]
