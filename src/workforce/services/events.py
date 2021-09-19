import arrow
import uuid

from workforce.models import WorkEvent
from workforce.utils import group_by


def get_user_next_event(email_address):
    return (WorkEvent.objects
            .filter(user__email_address=email_address)
            .filter(start__gte=arrow.get().datetime)
            .filter(canceled_at=None)
            .order_by('start')
            .first())


def get_event_to_delete(token_or_id):
    right_now = arrow.get().datetime

    return (WorkEvent.objects
            .filter(start__gte=right_now)
            .filter(cancelling_token=token_or_id)
            .filter(canceled_at=None)
            .first())


def delete_event(token_or_id):
    event = get_event_to_delete(token_or_id)
    if event is not None:
        event.canceled_at = arrow.get().datetime
        event.save()


def create_event(user, calendar_id, start_time, end_time, comment, is_live):
    cancelling_token = str(uuid.uuid4())

    WorkEvent.objects.create(
        user=user,
        calendar_id=calendar_id,
        start=start_time.datetime,
        end=end_time.datetime,
        comment=comment,
        is_live=is_live,
        cancelling_token=cancelling_token)

    # FIXME: concurrency prone issue here, as the retrieval
    # cab get other work event
    return WorkEvent.objects.latest('event_id')


def get_all_events_by_calendar(calendar_ids, start, end, is_live):
    work_events = (WorkEvent.objects
                   .filter(calendar_id__in=calendar_ids)
                   .filter(start__gte=arrow.get(start).datetime)
                   .filter(end__lt=arrow.get(end).datetime)
                   .filter(canceled_at=None)
                   .filter(is_live=is_live)
                   .all())

    return group_by(work_events, 'calendar_id', _work_event_to_timeslot)


def _work_event_to_timeslot(work_event):
    return (arrow.get(work_event.start), arrow.get(work_event.end))


def is_cancelling_token(token_to_verify):
    if not type(token_to_verify) is str:
        return False

    try:
        uuid_from_token = uuid.UUID(token_to_verify, version=4)
    except (ValueError, AttributeError):
        return False

    return str(uuid_from_token) == token_to_verify


def create_cancelling_token():
    return str(uuid.uuid4())
