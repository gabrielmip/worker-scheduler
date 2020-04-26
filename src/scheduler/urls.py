from django.urls import path

from scheduler.views import choose_timeslot_page, get_welcome_page, cancel_work_event, register_user, reservation_success
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', get_welcome_page, name="welcome"),
    path('schedule', choose_timeslot_page, name="schedule"),
    path('registration', register_user, name="registration"),
    path('reservation_success', reservation_success, name="reservation_success"),
    path('cancel/<event_id>', cancel_work_event, name="cancel_work_event"),
]
