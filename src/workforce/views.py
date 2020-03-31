import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse



def get_my_schedule(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    today_events = request.user.worker.calendar.workevent_set.filter(start__range=(today_min, today_max))
    worker = request.user.worker

    return render(request, 'my_schedule.html', {
        'worker_timezone': worker.timezone,
        'worker_name': worker.auth_user.first_name,
        'user': request.user,
        'today_events': today_events
    })
