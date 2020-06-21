import arrow

from workforce.models import User, WorkEvent
from workforce.repositories.event_repository import is_cancelling_token


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

    if not is_cancelling_token(token_or_id):
        return (WorkEvent.objects
                .filter(start__gte=right_now)
                .filter(event_id=token_or_id)
                .filter(cancelling_token=None)
                .first())
    else:
        return (WorkEvent.objects
                .filter(start__gte=right_now)
                .filter(cancelling_token=token_or_id)
                .first())


def delete_event(token_or_id):
    event = get_event_to_delete(token_or_id)
    if event is not None:
        event.delete()
