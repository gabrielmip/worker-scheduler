from django.urls import path
from django.contrib.auth import views as auth_views

from workforce.views import (
    choose_timeslot_page,
    WelcomePage,
    cancel_work_event,
    register_user,
    reservation_success,
    get_my_schedule,
    get_my_schedule_hash
)

urlpatterns = [
    path('', WelcomePage.as_view(), name="welcome"),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(),
         {'next_page': '/'}, name='logout'),
    path('schedule', choose_timeslot_page, name="schedule"),
    path('registration', register_user, name="registration"),
    path('reservation_success', reservation_success, name="reservation_success"),
    path('cancel/<token_or_id>', cancel_work_event, name="cancel_work_event"),
    path('my_schedule', get_my_schedule, name="my_schedule"),
    path('schedule_hash', get_my_schedule_hash, name="get_schedule_hash"),
]
