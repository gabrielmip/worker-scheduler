import uuid
import arrow

from workforce.models import WorkEvent


def create_event(user, calendar_id, start_time, end_time, comment):
    cancelling_token = str(uuid.uuid4())

    WorkEvent.objects.create(
        user=user,
        calendar_id=calendar_id,
        start=start_time.datetime,
        end=end_time.datetime,
        comment=comment,
        cancelling_token=cancelling_token)

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
        by_calendar[work_event.calendar_id].append(
            _work_event_to_timeslot(work_event))

    return by_calendar


def _work_event_to_timeslot(work_event):
    return (arrow.get(work_event.start), arrow.get(work_event.end))


def is_cancelling_token(token_to_verify):
    try:
        uuid_from_token = uuid.UUID(token_to_verify, version=4)
    except (ValueError, AttributeError):
        return False

    return str(uuid_from_token) == token_to_verify


def create_cancelling_token():
    return str(uuid.uuid4())
