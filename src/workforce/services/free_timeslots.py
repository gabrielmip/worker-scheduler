from babel.dates import format_datetime

from .active_calendars import (
    get_active_worker_calendars,
    get_range_to_analyse_availability
)


def get_free_timeslot_choices(user_timezone, locale, is_live):
    free_timeslots = get_free_timeslots(is_live)
    return _free_timeslots_to_choices(free_timeslots, user_timezone, locale)


def get_free_timeslots(is_live: bool = False):
    worker_calendars = get_active_worker_calendars(is_live)
    duration = 45 if is_live else 20
    free_timeslots = {}

    for timeslot in _get_timeslots_to_analyse(worker_calendars, duration):
        available, calendar_id = _is_timeslot_available(
            timeslot, worker_calendars)

        if available:
            free_timeslots[timeslot] = {
                'timeslot': timeslot,
                'calendar_id': calendar_id
            }

    return [*free_timeslots.values()]


def _is_timeslot_available(timeslot, calendars):
    for calendar in calendars:
        if (_is_calendar_available_for_timeslot(calendar['busy_timeslots'], timeslot)
                and not _is_calendar_available_for_timeslot(calendar['availabilities'], timeslot)):
            return True, calendar['id']

    return False, None


def _free_timeslots_to_choices(timeslots, user_timezone, locale):
    def timeslot_to_identifier(timeslot):
        return timeslot[0].isoformat()

    return [
        (
            timeslot_to_identifier(timeslot['timeslot']),
            format_datetime(
                timeslot['timeslot'][0].to(user_timezone).datetime,
                "EEEE, H'h'mm",
                locale=locale
            ).capitalize()
        )
        for timeslot in timeslots
    ]


def _get_timeslots_to_analyse(worker_calendars, duration: int = 20):
    start_time, end_time = get_range_to_analyse_availability()

    for calendar in worker_calendars:
        for availability in calendar['availabilities']:

            time_being_analysed = availability[0]
            while (time_being_analysed >= start_time
                    and time_being_analysed.shift(minutes=duration) <= end_time
                    and time_being_analysed.shift(minutes=duration) <= availability[1]):
                yield (time_being_analysed, time_being_analysed.shift(minutes=duration))
                time_being_analysed = time_being_analysed.shift(
                    minutes=duration)


def _is_timeslot_outside_range(timeslot, date_range):
    comes_before_range = (
        timeslot[0] <= date_range[0] and timeslot[1] <= date_range[0])
    comes_after_range = (timeslot[0] >= date_range[1]
                         and timeslot[1] >= date_range[1])

    return comes_before_range or comes_after_range


def _is_calendar_available_for_timeslot(busy_times, timeslot):
    if not busy_times:
        return True

    timeslot_not_conflicting = all(
        _is_timeslot_outside_range(timeslot, busy_time)
        for busy_time in busy_times
    )

    return timeslot_not_conflicting
