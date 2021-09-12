from babel.dates import format_datetime

from .active_calendars import (
    get_active_worker_calendars,
    get_range_to_analyse_availability
)


def get_free_timeslot_choices(user_timezone, locale):
    free_timeslots = get_free_timeslots()
    return _free_timeslots_to_choices(free_timeslots, user_timezone, locale)


def get_free_timeslots(is_live=False):
    worker_calendars = get_active_worker_calendars(is_live)
    free_timeslots = {}

    for timeslot in _get_timeslots_to_analyse():
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


def _get_timeslots_to_analyse():
    start_time, end_time = get_range_to_analyse_availability()

    time_being_analysed = start_time
    while time_being_analysed < end_time:
        yield (time_being_analysed, time_being_analysed.shift(minutes=20))
        time_being_analysed = time_being_analysed.shift(minutes=20)


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
