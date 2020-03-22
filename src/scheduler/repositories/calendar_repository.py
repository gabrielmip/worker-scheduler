import arrow
from workforce.models import Worker, Calendar, Availability


def get_active_worker_calendars():
    workers = Worker.objects.filter(on_vacations=False).all()

    return [
        {
            'id': worker.calendar_id,
            'name': worker.calendar.name,
            'availabilities': _map_availabilities_to_date(worker.availability_set.all(), worker.timezone)
        }
        for worker in workers
    ]


def _availability_as_datetime(availability, reference_datetime, timezone):
    reference_day_of_the_week = reference_datetime.datetime.weekday() + 1
    initial_days_to_shift = (0
        if reference_day_of_the_week <= availability.day_of_the_week
        else (7 - reference_day_of_the_week + availability.day_of_the_week))

    availability_end_as_datetime = (reference_datetime.shift(days=initial_days_to_shift)
        .replace(
            hour=availability.end_time.hour,
            minute=availability.end_time.minute
        ))
    availability_start_as_datetime = availability_end_as_datetime.replace(
        hour=availability.start_time.hour,
        minute=availability.start_time.minute)

    weeks_to_shift = (1 if availability_end_as_datetime < reference_datetime else 0)

    return (
        availability_start_as_datetime.shift(weeks=weeks_to_shift).replace(tzinfo=timezone),
        availability_end_as_datetime.shift(weeks=weeks_to_shift).replace(tzinfo=timezone),
    )


def _map_availabilities_to_date(availabilities, worker_timezone):
    reference_datetime = arrow.get()

    return [
        _availability_as_datetime(availability, reference_datetime, worker_timezone)
        for availability in availabilities
    ]
