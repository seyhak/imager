from .tasks import handle_processing_satellite_image_service


class SatelliteImageService:
    def __init__(self, satellite_image_id, image_path, image_name, uploader_email):
        self.satellite_image_id = satellite_image_id
        self.image_path = image_path
        self.image_name = image_name
        self.uploader_email = uploader_email

    def handle_service(self):
        handle_processing_satellite_image_service.delay(
            self.satellite_image_id,
            self.image_path,
            self.image_name,
            self.uploader_email,
        )
