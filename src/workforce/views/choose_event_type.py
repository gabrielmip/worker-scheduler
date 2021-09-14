from django.shortcuts import render
from django.conf import settings

from workforce.services.events import get_user_next_event
from workforce.services.free_timeslots import get_free_timeslot_choices, get_free_timeslots
from workforce.utils import get_locale_from_settings
from workforce.views.rules import finished_registration_required


@finished_registration_required
def choose_event_type(request, user):
    locale = get_locale_from_settings(settings.LANGUAGE_CODE)
    remote_choices = get_free_timeslot_choices(
        user.timezone, locale, is_live=False)
    live_choices = get_free_timeslot_choices(
        user.timezone, locale, is_live=True)

    return render(request, 'choose_event_type.html', {
        'user': user,
        'next_event': get_user_next_event(user.email_address),
        'count_remote_available': len(remote_choices),
        'count_live_available': len(live_choices),
    })
