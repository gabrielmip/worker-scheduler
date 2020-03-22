from django.http import HttpResponse
from django.shortcuts import render

from scheduler.forms import ScheduleAnAppointment


def schedule_an_appointment(request):
    form = ScheduleAnAppointment()

    return render(
        request,
        template_name='schedule_an_appointment.html',
        context={'form': form}
    )


def process_schedule_request(request):
    form = ScheduleAnAppointment(request.POST)
    return HttpResponse('OK')
