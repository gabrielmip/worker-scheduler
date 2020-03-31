from django.urls import path
from django.contrib.auth import views as auth_views

from workforce.views import get_my_schedule, get_my_schedule_hash


urlpatterns = [
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    path('my_schedule', get_my_schedule, name="my_schedule"),
    path('schedule_hash', get_my_schedule_hash, name="get_schedule_hash"),
]
