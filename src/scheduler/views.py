import arrow
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from scheduler.forms import ScheduleAnAppointment
from scheduler.repositories.event_repository import can_user_schedule_event, create_event


def schedule_an_appointment(request):
    form = ScheduleAnAppointment()
    return render(request, 'schedule_an_appointment.html', {'form': form})


def process_schedule_request(request):
    form = ScheduleAnAppointment(request.POST)

    if not form.is_valid():
        return HttpResponse('Failed')

    if can_user_schedule_event(form.cleaned_data['email_address']):
        calendar_id, start_time_string, end_time_string = form.cleaned_data['timeslots_available'].split('|')
        start_time = arrow.get(start_time_string)
        end_time = arrow.get(end_time_string)

        new_event = create_event(
            form.cleaned_data['email_address'],
            form.cleaned_data['full_name'],
            calendar_id,
            start_time,
            end_time)

        return HttpResponse('OK')

    return HttpResponse('User already has a session scheduled.')
