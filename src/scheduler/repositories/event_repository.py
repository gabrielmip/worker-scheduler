import arrow

from django.conf import settings
from workforce.models import User, WorkEvent, Calendar


def create_event(email_address, user_name, user_timezone, calendar_id, start_time, end_time, comment):
    try:
        user = User.objects.get(email_address=email_address)
    except User.DoesNotExist:
        user = User.objects.create(email_address=email_address, full_name=user_name, timezone=user_timezone)

    WorkEvent.objects.create(
        user=user,
        calendar_id=calendar_id,
        start=start_time.datetime,
        end=end_time.datetime,
        comment=comment)
    return WorkEvent.objects.latest('event_id')


def get_event_from_id(event_id):
    try:
        return WorkEvent.objects.get(pk=event_id)
    except WorkEvent.DoesNotExist:
        return None


def delete_event_from_id(event_id):
    try:
        WorkEvent.objects.get(pk=event_id).delete()
    except WorkEvent.DoesNotExist:
        return None


def get_all_events_by_calendar(calendar_ids, start, end):
    work_events = (WorkEvent.objects
        .filter(calendar_id__in=calendar_ids)
        .filter(start__gte=arrow.get(start).datetime)
        .filter(end__lt=arrow.get(end).datetime)
        .all())

    by_calendar = {calendar_id: [] for calendar_id in calendar_ids}

    for work_event in work_events:
        by_calendar[work_event.calendar_id].append(_work_event_to_timeslot(work_event))

    return by_calendar


def _work_event_to_timeslot(work_event):
    return (arrow.get(work_event.start), arrow.get(work_event.end))
