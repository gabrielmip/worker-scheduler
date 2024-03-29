import re
from datetime import time, datetime

import arrow
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import F
from django.shortcuts import render
from django.urls import reverse

from workforce.utils import get_today_date_for_timezone, group_by, index_by


def get_my_schedule(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if not hasattr(request.user, 'worker'):
        return HttpResponse(
            'Você não foi cadastrado como trabalhador. Peça '
            'às pessoas administradoras do sistema que te adicione.')

    requested_date = _get_requested_date(request)
    worker = request.user.worker
    today_events = _get_events_from_date(worker, requested_date)
    events_hash = _calculate_event_hash(today_events)

    return render(request, 'my_schedule.html', {
        'worker_timezone': worker.timezone,
        'worker_name': worker.auth_user.first_name,
        'user': request.user,
        'events_hash': events_hash,
        'requested_date': requested_date,
        'today_events': today_events
    })


def get_my_schedule_hash(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    worker = request.user.worker
    requested_date = _get_requested_date(request)
    today_events = _get_events_from_date(worker, requested_date)
    events_hash = _calculate_event_hash(today_events)

    return HttpResponse(events_hash)


def _get_events_from_date(worker, requested_date):
    def get_today_time(time_limit):
        today_for_worker = get_today_date_for_timezone(
            worker.timezone, requested_date).date()
        today_at_limit = datetime.combine(today_for_worker, time_limit)
        return arrow.get(today_at_limit).replace(tzinfo=worker.timezone).datetime

    today_min = get_today_time(time.min)
    today_max = get_today_time(time.max)

    events = (worker.calendar.workevent_set
              .filter(start__range=(today_min, today_max))
              .order_by('start')
              # first the canceled, then the actives.
              # this way the indexing will override canceled
              # with active events with the same start
              .order_by(F('canceled_at').asc(nulls_last=True)))

    unique_events = [*index_by(events, 'start').values()]
    unique_events.sort(key=lambda x: x.start)

    return unique_events


def _calculate_event_hash(work_events):
    joined_work_events = '|'.join([
        f"{event.user.email_address}|{event.start}|{event.canceled_at}"
        for event in work_events
    ])

    return hash(joined_work_events)


def _get_requested_date(request):
    from_request = request.GET.get('date', '').strip()
    return (from_request
            if len(from_request) > 0 and re.search(r'\d\d\d\d-\d\d-\d\d$', from_request)
            else datetime.now().strftime('%Y-%m-%d'))
