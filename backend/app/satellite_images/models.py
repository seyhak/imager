from commons.models import ProcessedModel, TimestampedModel, UUIDModel
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class SatelliteImage(UUIDModel, TimestampedModel, ProcessedModel):
    MONGO_DB_NAME = "satellite_images"
    MONGO_COLLECTION_NAME = "satellite_images_details"

    title = models.CharField(max_length=255)
    uploader = models.ForeignKey(
        User,
        related_name="images",
        on_delete=models.CASCADE,
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])],
    )
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.title
