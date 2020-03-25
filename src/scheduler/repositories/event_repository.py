import arrow

from django.conf import settings
from workforce.models import User, WorkEvent
import scheduler.repositories.google_agenda_repository as google_repo


def build_event_user_photo_url(user):
    return f"{settings.EXTERNAL_URL_BASE_PATH}{user.photo.url}"


def update_event_description_with_photo_url(work_event):
    photo_url = build_event_user_photo_url(work_event.user)

    return google_repo.edit_event_description(work_event.event_id, work_event.calendar_id, photo_url)


def can_user_schedule_event(email_address):
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
        .get())


def create_event(email_address, user_name, calendar_id, start_time, end_time):
    try:
        user = User.objects.get(email_address=email_address)
    except User.DoesNotExist:
        user = User.objects.create(email_address=email_address, full_name=user_name)

    description = (build_event_user_photo_url(user)
        if bool(user.photo)
        else "")
    new_google_event_id = google_repo.create_event(user_name, description, calendar_id, start_time, end_time)

    return WorkEvent.objects.create(
        user=user,
        calendar_id=calendar_id,
        name=user_name,
        event_id=new_google_event_id,
        start=start_time.isoformat(),
        end=end_time.isoformat())


def get_event_from_id(event_id):
    return WorkEvent.objects.get(pk=event_id)
