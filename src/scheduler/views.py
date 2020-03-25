import arrow
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from scheduler.forms import ScheduleAnAppointment, UploadPhoto
from scheduler.repositories.event_repository import (
    can_user_schedule_event, create_event, get_event_from_id
)


def get_reservation_page(request):
    if request.method == 'GET':
        form = ScheduleAnAppointment()
        return render(request, 'choose_timeslot.html', {'form': form})

    if request.method == 'POST':
        print(request.POST)
        return _make_reservation(request)

    return HttpResponseBadRequest('Method not supported')


def upload_photo(request):
    form = UploadPhoto(request.POST, request.FILES)

    if form.is_valid():
        event_id = request.POST.get('event_id')
        event = get_event_from_id(event_id)
        event.user.photo = form.cleaned_data['photo']
        event.user.save()

        return render(request, 'reservation_success.html', {'event': event})

    return HttpResponse('')


def _make_reservation(request):
    form = ScheduleAnAppointment(request.POST)

    if not form.is_valid():
        return render(request, 'choose_timeslot.html', {'form': form})

    if can_user_schedule_event(form.cleaned_data['email_address']):
        new_work_event = _create_event_from_form_data(form.cleaned_data)
        context = {'event': new_work_event, 'form': UploadPhoto()}
        template_to_render = ('reservation_success.html'
            if bool(new_work_event.user.photo)
            else 'upload_photo.html')

        return render(request, template_to_render, context)

    return HttpResponse('User already has a session scheduled.')


def _create_event_from_form_data(form_data):
    calendar_id, start_time_string, end_time_string = form_data['timeslots_available'].split('|')
    start_time = arrow.get(start_time_string)
    end_time = arrow.get(end_time_string)

    return create_event(
        form_data['email_address'],
        form_data['full_name'],
        calendar_id,
        start_time,
        end_time)
