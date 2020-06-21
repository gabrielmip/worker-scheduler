from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from workforce.services.events_service import (
    delete_event,
    get_event_to_delete,
)


def cancel_work_event(request, token_or_id):
    if request.method == 'GET':
        event = get_event_to_delete(token_or_id)
        return render(request, 'cancel_work_event.html', {'event': event})

    if request.method == 'POST':
        delete_event(token_or_id)
        return HttpResponseRedirect(reverse('welcome'))
