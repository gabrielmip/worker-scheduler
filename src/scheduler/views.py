import arrow
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from scheduler.forms import ScheduleAnAppointment, UploadPhoto
from scheduler.user_timezone_capture.session_settings import TIMEZONE_KEY
from scheduler.services.emails_service import setup_email_sending
from scheduler.repositories.event_repository import (
    create_event,
    delete_event_from_id,
    get_event_from_id,
    update_event_description_with_photo_url
)


def get_welcome_page(request):
    if request.method == 'GET':
        return render(request, 'welcome.html')

    if request.method == 'POST':
        request.session[TIMEZONE_KEY] = request.POST['user_timezone']
        return HttpResponseRedirect(reverse('schedule'))


def get_reservation_page(request):
    if request.method == 'GET':
        form = ScheduleAnAppointment(request.session[TIMEZONE_KEY])
        return render(request, 'choose_timeslot.html', {'form': form})

    if request.method == 'POST':
        return _make_reservation(request)

    return HttpResponseBadRequest('Method not supported')


def upload_photo(request):
    form = UploadPhoto(request.POST, request.FILES)

    if form.is_valid():
        event_id = request.POST.get('event_id')
        event = get_event_from_id(event_id)
        event.user.photo = form.cleaned_data['photo']
        event.user.save()
        update_event_description_with_photo_url(event)

        return render(request, 'reservation_success.html', {'event': event})


def cancel_work_event(request, event_id):
    if request.method == 'GET':
        event = get_event_from_id(event_id)
        return render(request, 'cancel_work_event.html', {'event': event})

    if request.method == 'POST':
        delete_event_from_id(event_id)
        return HttpResponseRedirect(reverse('welcome'))


def _make_reservation(request):
    form = ScheduleAnAppointment(request.session[TIMEZONE_KEY], request.POST)

    if not form.is_valid():
        return render(request, 'choose_timeslot.html', {'form': form})

    new_work_event = _create_event_from_form_data(form.cleaned_data, request.session[TIMEZONE_KEY])
    setup_email_sending(new_work_event)
    context = {'event': new_work_event, 'form': UploadPhoto()}
    template_to_render = ('reservation_success.html'
        if bool(new_work_event.user.photo)
        else 'upload_photo.html')

    return render(request, template_to_render, context)


def _create_event_from_form_data(form_data, user_timezone):
    calendar_id, start_time_string, end_time_string = form_data['timeslots_available'].split('|')
    start_time = arrow.get(start_time_string)
    end_time = arrow.get(end_time_string)

    return create_event(
        form_data['email_address'],
        form_data['full_name'],
        user_timezone,
        calendar_id,
        start_time,
        end_time)
