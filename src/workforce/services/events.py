import arrow
import uuid

from workforce.models import User, WorkEvent
from workforce.utils import group_by


def can_user_schedule_event(email_address):
    ''' returns True if there is no future scheduled
        event for the user, False otherwise.
    '''
    try:
        user = User.objects.get(email_address=email_address)
    except User.DoesNotExist:
        return True

    return (user.workevent_set
            .filter(start__gte=arrow.get().datetime)
            .count()) == 0


def get_user_next_event(email_address):
    return (WorkEvent.objects
            .filter(user__email_address=email_address)
            .filter(start__gte=arrow.get().datetime)
            .order_by('start')
            .first())


def get_event_to_delete(token_or_id):
    right_now = arrow.get().datetime

    if not is_cancelling_token(token_or_id) and token_or_id.isdigit():
        try:
            return (WorkEvent.objects
                    .filter(start__gte=right_now)
                    .filter(event_id=token_or_id)
                    .filter(cancelling_token=None)
                    .first())
        except OverflowError:  # int too big for the database
            return None
    else:
        return (WorkEvent.objects
                .filter(start__gte=right_now)
                .filter(cancelling_token=token_or_id)
                .first())


def delete_event(token_or_id):
    event = get_event_to_delete(token_or_id)
    if event is not None:
        event.delete()


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

    return group_by(work_events, 'calendar_id', _work_event_to_timeslot)


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
