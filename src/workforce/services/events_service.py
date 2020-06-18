import arrow

from workforce.models import User, WorkEvent


def can_user_schedule_event(email_address):
    ''' returns True if there is no future scheduled
        event for the user, False otherwise.
    '''
    try:
        user = User.objects.get(email_address=email_address)
    except User.DoesNotExist:
        return True

    return user.workevent_set.filter(start__gte=arrow.get().datetime).count() == 0


def get_user_next_event(email_address):
    return (WorkEvent.objects
            .filter(user__email_address=email_address)
            .filter(start__gte=arrow.get().datetime)
            .order_by('start')
            .first())
