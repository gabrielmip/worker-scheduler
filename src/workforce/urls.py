from django.urls import path
from django.contrib.auth import views as auth_views

from workforce.views import (
    ChooseTimeslotView,
    choose_event_type,
    WelcomePage,
    cancel_work_event,
    RegisterUser,
    reservation_success,
    get_my_schedule,
    get_my_schedule_hash
)

urlpatterns = [
    path('', WelcomePage.as_view(), name="welcome"),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(),
         {'next_page': '/'}, name='logout'),
    path('choose_event_type', choose_event_type, name="choose_event_type"),
    path('schedule/remote', ChooseTimeslotView.as_view(),
         {'is_live': False}, name="schedule"),
    path('schedule/live', ChooseTimeslotView.as_view(),
         {'is_live': True}, name="schedule_live"),
    path('registration', RegisterUser.as_view(), name="registration"),
    path('reservation_success', reservation_success, name="reservation_success"),
    path('cancel/<token_or_id>', cancel_work_event, name="cancel_work_event"),
    path('my_schedule', get_my_schedule, name="my_schedule"),
    path('schedule_hash', get_my_schedule_hash, name="get_schedule_hash"),
]
