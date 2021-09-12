from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, reverse
from workforce.services.events import get_user_next_event
from workforce.views.rules import finished_registration_required


@finished_registration_required
def reservation_success(request):
    next_event = get_user_next_event(request.session['email_address'])

    if not next_event:
        return HttpResponse(
            'Algo de errado aconteceu. Se você tiver acabado de '
            'marcar uma sessão e recebeu esta mensagem, por favor, '
            'mande um email para reikidaconceicao@gmail.com')

    return render(request, 'reservation_success.html', context={
        'event': next_event
    })
