from django.urls import path

from scheduler.views import get_reservation_page, make_reservation, upload_photo

urlpatterns = [
    path('', get_reservation_page),
    path('process', make_reservation),
    path('upload_photo', upload_photo)
]
