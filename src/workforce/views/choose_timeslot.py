import arrow
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.decorators.cache import never_cache
from django.views import View

from workforce.forms import ScheduleAnAppointment
from workforce.services.emails import setup_email_sending
from workforce.services.events import get_user_next_event, create_event
from workforce.services.free_timeslots import get_free_timeslots
from workforce.services.users import get_user_object_from_email, has_missing_fields


class ChooseTimeslotView(View):
    @never_cache
    def get(self, request):
        if not request.session.get('email_address', False):
            return HttpResponseRedirect(reverse('welcome'))

        user, is_new = get_user_object_from_email(
            request.session['email_address'])
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

    def post(self, request):
        if not request.session.get('email_address', False):
            return HttpResponseRedirect(reverse('welcome'))

        email_address = request.session['email_address']

        if get_user_next_event(email_address):
            return HttpResponseRedirect(reverse('schedule'))

        user, _ = get_user_object_from_email(email_address)
        comment = request.POST.get('comment')
        timeslot_start = arrow.get(request.POST.get('timeslots_available'))

        new_event = _make_reservation(user, timeslot_start, comment)

        if not new_event:
            form = ScheduleAnAppointment(user, request.POST)
            return render(request, 'choose_timeslot.html', {
                'form': form,
                'has_timeslots_available': (len(form.fields['timeslots_available'].choices) > 0)
            })

        return HttpResponseRedirect(reverse('reservation_success'))


def _make_reservation(user, timeslot_start, comment):
    free_timeslots = [
        timeslot
        for timeslot in get_free_timeslots()
        if timeslot['timeslot'][0] == timeslot_start
    ]

    if not free_timeslots:
        return None

    new_work_event = create_event(
        user,
        free_timeslots[0]['calendar_id'],
        free_timeslots[0]['timeslot'][0],
        free_timeslots[0]['timeslot'][1],
        comment
    )
    setup_email_sending(new_work_event)

    return new_work_event
