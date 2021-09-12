import arrow
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View
from django.conf import settings

from workforce.forms import ScheduleAnAppointment
from workforce.services.emails import setup_email_sending
from workforce.services.events import get_user_next_event, create_event
from workforce.services.free_timeslots import get_free_timeslot_choices, get_free_timeslots
from workforce.utils import get_locale_from_settings
from workforce.views.rules import finished_registration_required


class ChooseTimeslotView(View):
    @method_decorator(never_cache)
    @method_decorator(finished_registration_required)
    def get(self, request, user):
        choices = get_free_timeslot_choices(
            user_timezone=user.timezone,
            locale=get_locale_from_settings(settings.LANGUAGE_CODE)
        )
        appointment_form = ScheduleAnAppointment(choices)

        return render(request, 'choose_timeslot.html', {
            'form': appointment_form,
            'user': user,
            'next_event': get_user_next_event(user.email_address),
            'has_timeslots_available': (
                len(appointment_form.fields['timeslots_available'].choices) > 0)
        })

    @method_decorator(finished_registration_required)
    def post(self, request, user):
        if get_user_next_event(user.email_address):
            return HttpResponseRedirect(reverse('schedule'))

        comment = request.POST.get('comment')
        timeslot_start = arrow.get(request.POST.get('timeslots_available'))
        new_event = _make_reservation(user, timeslot_start, comment)

        if not new_event:
            choices = get_free_timeslot_choices(
                user_timezone=user.timezone,
                locale=get_locale_from_settings(settings.LANGUAGE_CODE)
            )
            form = ScheduleAnAppointment(choices, request.POST)
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

    timeslot = free_timeslots[0]
    new_work_event = create_event(
        user,
        timeslot['calendar_id'],
        timeslot['timeslot'][0],
        timeslot['timeslot'][1],
        comment
    )
    setup_email_sending(new_work_event)

    return new_work_event
