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


def get_redirect_view_name(is_live):
    return 'schedule_live' if is_live else 'schedule'


class ChooseTimeslotView(View):
    @method_decorator(never_cache)
    @method_decorator(finished_registration_required)
    def get(self, request, user, is_live):
        if get_user_next_event(user.email_address):
            return HttpResponseRedirect(reverse(get_redirect_view_name(is_live)))

        choices = get_free_timeslot_choices(
            user_timezone=user.timezone,
            locale=get_locale_from_settings(settings.LANGUAGE_CODE),
            is_live=is_live
        )
        appointment_form = ScheduleAnAppointment(choices)

        return render(request, 'choose_timeslot.html', {
            'form_action': get_redirect_view_name(is_live),
            'form': appointment_form,
            'has_timeslots_available': (len(appointment_form.fields['timeslots_available'].choices) > 0),
            'is_live': is_live,
            'user': user,
        })

    @method_decorator(finished_registration_required)
    def post(self, request, user, is_live):
        if get_user_next_event(user.email_address):
            return HttpResponseRedirect(reverse(get_redirect_view_name(is_live)))

        comment = request.POST.get('comment')
        timeslot_start = arrow.get(request.POST.get('timeslots_available'))
        new_event = _make_reservation(user, timeslot_start, comment, is_live)

        if not new_event:
            choices = get_free_timeslot_choices(
                user_timezone=user.timezone,
                locale=get_locale_from_settings(settings.LANGUAGE_CODE),
                is_live=is_live
            )
            form = ScheduleAnAppointment(choices, request.POST)
            return render(request, 'choose_timeslot.html', {
                'form_action': get_redirect_view_name(is_live),
                'form': form,
                'has_timeslots_available': (len(form.fields['timeslots_available'].choices) > 0),
                'is_live': is_live,
                'user': user,
            })

        return HttpResponseRedirect(reverse('reservation_success'))


def _make_reservation(user, timeslot_start, comment, is_live):
    free_timeslots = [
        timeslot
        for timeslot in get_free_timeslots(is_live)
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
        comment,
        is_live,
    )
    setup_email_sending(new_work_event)

    return new_work_event
