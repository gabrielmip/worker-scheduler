from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from scheduler.repositories.event_repository import (
    delete_event_from_id,
    get_event_from_id
)


def cancel_work_event(request, event_id):
    if request.method == 'GET':
        event = get_event_from_id(event_id)
        return render(request, 'cancel_work_event.html', {'event': event})

    if request.method == 'POST':
        delete_event_from_id(event_id)
        return HttpResponseRedirect(reverse('welcome'))
