from django.contrib import admin

from .models import SatelliteImage
from .services import SatelliteImageService


@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    readonly_fields = ["image", "title", "uploader", "status"]
    list_display = ("id", "title", "uploader", "created_at", "status")
    search_fields = [
        "uploader__username",
        "title",
    ]
    ordering = ["created_at"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ["title", "uploader", "status"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.title = form.files["image"].name
            obj.uploader = request.user

        super().save_model(request, obj, form, change)
        if not change:
            image_path = obj.image.path
            service = SatelliteImageService(
                obj.id, image_path, obj.title, obj.uploader.email
            )
            service.handle_service()
