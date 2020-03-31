from django.urls import path
from django.contrib.auth import views as auth_views

from workforce.views import get_my_schedule


urlpatterns = [
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('profile', get_my_schedule, name="profile")
]
