from datetime import time, datetime, date

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def get_my_schedule(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    worker = request.user.worker
    today_events = _get_today_events(worker)
    events_hash = _calculate_event_hash(today_events)

    return render(request, 'my_schedule.html', {
        'worker_timezone': worker.timezone,
        'worker_name': worker.auth_user.first_name,
        'user': request.user,
        'events_hash': events_hash,
        'today_events': today_events
    })


def get_my_schedule_hash(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    worker = request.user.worker
    today_events = _get_today_events(worker)
    events_hash = _calculate_event_hash(today_events)

    return HttpResponse(events_hash)


def _get_today_events(worker):
    today_min = datetime.combine(datetime.today(), time.min)
    today_max = datetime.combine(datetime.today(), time.max)

    return worker.calendar.workevent_set.filter(start__range=(today_min, today_max))


def _calculate_event_hash(work_events):
    joined_work_events = '|'.join([
        f"{event.user.email_address}|{event.start}"
        for event in work_events
    ])

    return hash(joined_work_events)
