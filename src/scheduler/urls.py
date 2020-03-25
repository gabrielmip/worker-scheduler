from django.urls import path

from scheduler.views import get_reservation_page, upload_photo

urlpatterns = [
    path('', get_reservation_page, name="index"),
    path('upload_photo', upload_photo, name="upload_photo")
]
