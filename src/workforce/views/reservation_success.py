from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, reverse
from workforce.services.events_service import get_user_next_event


def reservation_success(request):
    if request.method != 'GET':
        return HttpResponseBadRequest('Method not supported')

    if not request.session.get('email_address', False):
        return HttpResponseRedirect(reverse('welcome'))

    next_event = get_user_next_event(request.session['email_address'])

    if not next_event:
        return HttpResponse(
            'Algo de errado aconteceu. Se você tiver acabado de '
            'marcar uma sessão e recebeu esta mensagem, por favor, '
            'mande um email para reikidaconceicao@gmail.com')

    return render(request, 'reservation_success.html', context={
        'event': next_event
    })
