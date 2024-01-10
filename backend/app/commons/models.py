import uuid
from enum import Enum

from django.db import models


class StatusEnum(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProcessedModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.name) for status in StatusEnum],
        default=StatusEnum.PENDING.value,
    )

    def set_status(self, new_status):
        all_possible_values = [status.value for status in StatusEnum]
        if new_status not in all_possible_values:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.save()

    class Meta:
        abstract = True
