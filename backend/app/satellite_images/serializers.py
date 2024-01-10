from rest_framework import serializers

from .models import SatelliteImage


class SatelliteImageSerializer(serializers.ModelSerializer):
    processing_data = serializers.SerializerMethodField()

    class Meta:
        model = SatelliteImage
        fields = ["id", "title", "created_at", "status", "processing_data"]

    def get_processing_data(self, obj):
        details = self.context.get("details")
        if not details:
            return None
        return details.get(str(obj.id))
