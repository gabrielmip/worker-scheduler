from django.urls import path

from scheduler.views import schedule_an_appointment, process_schedule_request

urlpatterns = [
    path('', schedule_an_appointment),
    path('process', process_schedule_request)
]
