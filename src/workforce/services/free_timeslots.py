from babel.dates import format_datetime
from .types import Timeslot
from pprint import pprint

from .active_calendars import (
    get_active_worker_calendars,
    get_range_to_analyse_availability
)


def get_free_timeslot_choices(user_timezone, locale, is_live):
    free_timeslots = get_free_timeslots(is_live)
    return _free_timeslots_to_choices(free_timeslots, user_timezone, locale)


def get_available_count(is_live):
    free_timeslots = get_free_timeslots(is_live)
    return sum((t['available_count'] for t in free_timeslots))


def get_free_timeslots(is_live: bool = False):
    worker_calendars = get_active_worker_calendars(is_live)
    free_timeslots = {}

    for timeslot in _get_timeslots_to_analyse(worker_calendars):
        available_count, calendar_id = _is_timeslot_available(
            timeslot, worker_calendars)

        if available_count:
            free_timeslots[timeslot.start] = {
                'timeslot': (timeslot.start, timeslot.end),
                'calendar_id': calendar_id,
                'available_count': available_count
            }

    values = [*free_timeslots.values()]
    values.sort(key=lambda x: x['timeslot'][0])

    return values


def _is_timeslot_available(timeslot, calendars):
    # FIXME: Consider the actual timeslots the availability produces given their duration
    # instead of assuming the start and end date of the timeslot being checked is going to
    # match the availability ones. Count is wrong because of that.
    available_calendars = [
        calendar
        for calendar in calendars
        if (_is_calendar_available_for_timeslot(calendar['busy_timeslots'], timeslot)
            and not _is_calendar_available_for_timeslot(calendar['availabilities'], timeslot))
    ]

    if not available_calendars:
        return 0, None

    available_calendars.sort(
        key=lambda calendar: _count_busy_timeslots(calendar, timeslot))
    least_busy_calendar = available_calendars[0]

    return len(available_calendars), least_busy_calendar['id']


def _count_busy_timeslots(calendar, timeslot: Timeslot):
    timeslot_day = timeslot.start.to(
        calendar['worker_timezone']).format('YYYY-MM-DD')

    return len([
        busy_timeslot
        for busy_timeslot in calendar['busy_timeslots']
        if timeslot_day == (
            busy_timeslot.start.to(
                calendar['worker_timezone']).format('YYYY-MM-DD')
        )
    ])


def _free_timeslots_to_choices(timeslot_objs, user_timezone, locale):
    def timeslot_to_identifier(timeslot):
        return timeslot[0].isoformat()

    def to_choice(timeslot_obj):
        datetime = format_datetime(
            timeslot_obj['timeslot'][0].to(user_timezone).datetime,
            "EEEE, H'h'mm",
            locale=locale
        ).capitalize()

        return f'{datetime} ({timeslot_obj["available_count"]} disp.)'

    return [
        (
            timeslot_to_identifier(timeslot_obj['timeslot']),
            to_choice(timeslot_obj),
        )
        for timeslot_obj in timeslot_objs
    ]


def _get_timeslots_to_analyse(worker_calendars):
    start_time, end_time = get_range_to_analyse_availability()

    for calendar in worker_calendars:
        for availability in calendar['availabilities']:

            time_being_analysed = availability.start
            while (time_being_analysed >= start_time
                    and time_being_analysed.shift(minutes=availability.session_duration) <= end_time
                    and time_being_analysed.shift(minutes=availability.session_duration) <= availability.end):
                yield Timeslot(
                    start=time_being_analysed,
                    end=time_being_analysed.shift(minutes=availability.session_duration)
                )
                time_being_analysed = time_being_analysed.shift(minutes=availability.session_duration)


def _is_timeslot_outside_range(timeslot: Timeslot, date_range: Timeslot):
    comes_before_range = (
        timeslot.start <= date_range.start and timeslot.end <= date_range.start)
    comes_after_range = (timeslot.start >= date_range.end
                         and timeslot.end >= date_range.end)

    return comes_before_range or comes_after_range


def _is_calendar_available_for_timeslot(busy_times: list[Timeslot], timeslot: Timeslot):
    if not busy_times:
        return True

    timeslot_not_conflicting = all(
        _is_timeslot_outside_range(timeslot, busy_time)
        for busy_time in busy_times
    )

    return timeslot_not_conflicting
