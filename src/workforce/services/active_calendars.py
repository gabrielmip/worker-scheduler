import arrow
from django.conf import settings

from workforce.services.events import get_all_events_by_calendar
from workforce.models import Worker


def get_active_worker_calendars(is_live=False):
    ''' Returns an dictionary for each active worker's calendar.
        An active worker is someone that is not on vacations at the moment.
        Explanations:
        'availabilities': working hours specified by worker.
        'busy_timeslots': busy timelots currently being observed in the
                          worker's agenda.
    '''
    workers = Worker.objects.active_workers().all()
    busy_timeslots_by_calendar = _get_week_busy_timeslots_by_calendar(
        workers,
        is_live=is_live
    )

    return [
        {
            'id': worker.calendar_id,
            'availabilities': _map_availabilities_to_date(
                worker.availability_set.filter(is_live=is_live).all(),
                worker.timezone
            ),
            'worker_timezone': worker.timezone,
            'busy_timeslots': busy_timeslots_by_calendar[worker.calendar_id]
        }
        for worker in workers
    ]


def get_range_to_analyse_availability():
    reference_time = (arrow.now()
                      .to(settings.TIME_ZONE)
                      .replace(second=0, microsecond=0))

    return (reference_time, reference_time.shift(days=+6))


def _get_week_busy_timeslots_by_calendar(workers, is_live):
    calendar_ids = [w.calendar_id for w in workers]
    start, end = get_range_to_analyse_availability()

    return get_all_events_by_calendar(calendar_ids, start, end, is_live)


def _availability_as_datetime(availability, reference_datetime, worker_timezone):
    reference_day_of_the_week = reference_datetime.datetime.weekday() + 1
    initial_days_to_shift = (availability.day_of_the_week - reference_day_of_the_week
                             if reference_day_of_the_week <= availability.day_of_the_week
                             else (7 - reference_day_of_the_week + availability.day_of_the_week))

    availability_end_as_datetime = (reference_datetime.shift(days=initial_days_to_shift)
                                    .replace(
                                        hour=availability.end_time.hour,
                                        minute=availability.end_time.minute,
                                        second=0,
                                        microsecond=0
    ))
    availability_start_as_datetime = availability_end_as_datetime.replace(
        hour=availability.start_time.hour,
        minute=availability.start_time.minute,
        second=0,
        microsecond=0
    )

    weeks_to_shift = (1 if availability_end_as_datetime <
                      reference_datetime else 0)

    return (
        _availability_to_system_zone(availability_start_as_datetime,
                                     weeks_to_shift, worker_timezone),
        _availability_to_system_zone(availability_end_as_datetime,
                                     weeks_to_shift, worker_timezone),
    )


def _availability_to_system_zone(datetime, weeks_to_shift, worker_timezone):
    return (datetime.shift(weeks=weeks_to_shift)
            .replace(tzinfo=worker_timezone)
            .to(settings.TIME_ZONE))


def _map_availabilities_to_date(availabilities, worker_timezone):
    reference_datetime = arrow.get()

    return [
        _availability_as_datetime(
            availability, reference_datetime, worker_timezone)
        for availability in availabilities
    ]
