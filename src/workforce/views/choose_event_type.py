from django.shortcuts import render
from workforce.services.events import get_user_next_event

from workforce.views.rules import finished_registration_required


@finished_registration_required
def choose_event_type(request, user):
    return render(request, 'choose_event_type.html', {
        'user': user,
        'next_event': get_user_next_event(user.email_address),
        'has_timeslots_available': True
    })
