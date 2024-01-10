from commons.mongo import get_mongo_db_client
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import SatelliteImage
from .serializers import SatelliteImageSerializer


class SatelliteImageViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = SatelliteImage.objects.all()
    serializer_class = SatelliteImageSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(uploader=self.request.user)
        return qs

    def _get_details(self, list_of_ids):
        """
        Get data related with PG SatelliteImage from mongoDB.
        Map each detail to PG id.
        """
        client = get_mongo_db_client()
        dbname = client[SatelliteImage.MONGO_DB_NAME]
        satellite_images = dbname[SatelliteImage.MONGO_COLLECTION_NAME]

        all_details = satellite_images.find(
            {"satellite_image_id": {"$in": list_of_ids}}
        )
        details = {
            i["satellite_image_id"]: i
            for i in all_details
            if i.get("satellite_image_id")
        }
        client.close()
        return details

    def get_serializer_context(self):
        """
        Put mongo details in context to avoid querying the db each item.
        """
        queryset = self.get_queryset()
        list_of_ids = [str(id) for id in queryset.values_list("id", flat=True)]
        context = super().get_serializer_context()
        details = self._get_details(list_of_ids)

        return {**context, "details": details}
