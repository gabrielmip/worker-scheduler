from django.shortcuts import render

from workforce.services.events import get_user_next_event
from workforce.services.free_timeslots import get_available_count
from workforce.views.rules import finished_registration_required


@finished_registration_required
def choose_event_type(request, user):
    remote_count = get_available_count(is_live=False)
    live_count = get_available_count(is_live=True)

    return render(request, 'choose_event_type.html', {
        'user': user,
        'next_event': get_user_next_event(user.email_address),
        'has_timeslots_available': any([remote_count, live_count]),
        'count_remote_available': remote_count,
        'count_live_available': live_count,
    })
