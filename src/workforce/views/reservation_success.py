from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from workforce.services.events import get_user_next_event
from workforce.views.rules import finished_registration_required
from workforce.utils import get_locale_from_settings
from workforce.services.free_timeslots import get_free_timeslot_choices


@finished_registration_required
def reservation_success(request, user):
    next_event = get_user_next_event(request.session['email_address'])

    if not next_event:
        return HttpResponse(
            'Algo de errado aconteceu. Se você tiver acabado de '
            'agendar uma sessão e recebeu esta mensagem, por favor, '
            'mande um email para contato@reikidosantaines.site')

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

    return render(request, 'reservation_success.html', context={
        'has_timeslots_available': any([
            other_timeslots['live'], other_timeslots['remote']
        ]),
        'other_timeslots': other_timeslots,
        'event': next_event
    })
