from factory import SubFactory, fuzzy
from factory.django import DjangoModelFactory
from satellite_images.models import SatelliteImage

from .user import UserFactory


class SatelliteImageFactory(DjangoModelFactory):
    title = fuzzy.FuzzyText()
    uploader = SubFactory(UserFactory)

    class Meta:
        model = SatelliteImage
