from django.urls import path

from scheduler.views import get_reservation_page, upload_photo, get_welcome_page

urlpatterns = [
    path('', get_welcome_page, name="welcome"),
    path('schedule', get_reservation_page, name="schedule"),
    path('upload_photo', upload_photo, name="upload_photo")
]
