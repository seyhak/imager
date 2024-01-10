from django.contrib.auth.models import User
from factory import fuzzy
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    username = fuzzy.FuzzyText(length=12)

    class Meta:
        model = User
