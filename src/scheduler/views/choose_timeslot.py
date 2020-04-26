import arrow
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, reverse

from scheduler.forms import ScheduleAnAppointment
from scheduler.services.emails_service import setup_email_sending
from scheduler.services.events_service import get_user_next_event
from scheduler.repositories.event_repository import create_event
from scheduler.services.user_service import get_user_object_from_email, has_missing_fields


def choose_timeslot_page(request):
    if request.method == 'GET':
        if not request.session.get('email_address', False):
            return HttpResponseRedirect(reverse('welcome'))

        user, is_new = get_user_object_from_email(request.session['email_address'])
        missing_fields = has_missing_fields(user)

        if missing_fields or is_new:
            return HttpResponseRedirect(reverse('welcome'))

        appointment_form = ScheduleAnAppointment(user)

        return render(request, 'choose_timeslot.html', {
            'form': appointment_form,
            'user': user,
            'next_event': get_user_next_event(user.email_address),
            'has_timeslots_available': (
                len(appointment_form.fields['timeslots_available'].choices) > 0)
        })

    if request.method == 'POST':
        if not request.session.get('email_address', False):
            return HttpResponseRedirect(reverse('welcome'))

        return _make_reservation(request, request.session['email_address'])

    return HttpResponseBadRequest('Method not supported')


def _make_reservation(request, email_address):
    user, _ = get_user_object_from_email(email_address)
    form = ScheduleAnAppointment(user, request.POST)

    if not form.is_valid():
        return render(request, 'choose_timeslot.html', {
            'form': form,
            'has_timeslots_available': (len(form.fields['timeslots_available'].choices) > 0)
        })

    new_work_event = _create_event_from_form_data(form.cleaned_data, user)
    setup_email_sending(new_work_event)

    return HttpResponseRedirect(reverse('reservation_success'))


def _create_event_from_form_data(form_data, user):
    calendar_id, start_time_string, end_time_string = form_data['timeslots_available'].split('|')
    start_time = arrow.get(start_time_string)
    end_time = arrow.get(end_time_string)

    return create_event(
        user,
        calendar_id,
        start_time,
        end_time,
        form_data['comment'])
