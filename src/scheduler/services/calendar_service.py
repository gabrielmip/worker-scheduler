import random
import logging

from scheduler.repositories.calendar_repository import (
    get_active_worker_calendars,
    get_range_to_analyse_availability
)


def get_one_free_timeslot_by_hour():
    worker_calendars = get_active_worker_calendars()
    hash_slot = lambda x: f'{x[0].day} - {x[0].hour}'
    timeslot_by_hour_in_day = {}

    for timeslot in _get_timeslots_to_analyse():
        if hash_slot(timeslot) in timeslot_by_hour_in_day:
            continue

        available, calendar_id = is_timeslot_available(timeslot, worker_calendars)

        if available:
            timeslot_by_hour_in_day[hash_slot(timeslot)] = {
                'timeslot': timeslot,
                'calendar_id': calendar_id
            }

    return [*timeslot_by_hour_in_day.values()]


def is_timeslot_available(timeslot, calendars):
    random.shuffle(calendars)

    for calendar in calendars:
        if _is_calendar_available_for_timeslot(calendar['busy_timeslots'], timeslot):
            logging.debug(f"{timeslot[0].format('HH:mm')}-{timeslot[1].format('HH:mm')}: {calendar['id']}")
            return True, calendar['id']

    return False, None


def _get_timeslots_to_analyse():
    start_time, end_time = get_range_to_analyse_availability()

    time_being_analysed = start_time
    while time_being_analysed < end_time:
        yield (time_being_analysed, time_being_analysed.shift(minutes=15))
        time_being_analysed = time_being_analysed.shift(minutes=15)


def _is_timeslot_outside_range(timeslot, date_range):
    comes_before_range = (timeslot[0] <= date_range[0] and timeslot[1] <= date_range[0])
    comes_after_range = (timeslot[0] >= date_range[1] and timeslot[1] >= date_range[1])

    return comes_before_range or comes_after_range


def _is_calendar_available_for_timeslot(busy_times, timeslot):
    if not busy_times:
        return True

    timeslot_not_conflicting = all(
        _is_timeslot_outside_range(timeslot, busy_time)
        for busy_time in busy_times
    )

    return timeslot_not_conflicting
