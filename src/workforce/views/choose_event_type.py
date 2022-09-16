from django.shortcuts import render
from django.conf import settings

from workforce.services.events import get_user_next_event
from workforce.services.free_timeslots import get_available_count, get_free_timeslot_choices
from workforce.utils import get_locale_from_settings
from workforce.views.rules import finished_registration_required


@finished_registration_required
def choose_event_type(request, user):
    remote_count = get_available_count(is_live=False)
    live_count = get_available_count(is_live=True)
    next_event = get_user_next_event(user.email_address)
    other_timeslots = None if not next_event else {
        'live': get_free_timeslot_choices(
            user.timezone,
            locale=get_locale_from_settings(settings.LANGUAGE_CODE),
            is_live=True,
        ),
        'remote': get_free_timeslot_choices(
            user.timezone,
            locale=get_locale_from_settings(settings.LANGUAGE_CODE),
            is_live=False,
        )
    }


    return render(request, 'choose_event_type.html', {
        'user': user,
        'next_event': next_event,
        'other_timeslots': other_timeslots,
        'has_timeslots_available': any([remote_count, live_count]),
        'count_remote_available': remote_count,
        'count_live_available': live_count,
    })
