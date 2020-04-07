from django.urls import path

from scheduler.views import get_reservation_page, upload_photo, get_welcome_page, cancel_work_event, get_user_login_page
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', get_welcome_page, name="welcome"),
    path('user_login', get_user_login_page, name="user_login"),
    path('schedule', get_reservation_page, name="schedule"),
    path('upload_photo', upload_photo, name="upload_photo"),
    path('cancel/<event_id>', cancel_work_event, name="cancel_work_event"),
]
