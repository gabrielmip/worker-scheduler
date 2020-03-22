import random
import logging


def _get_timeslots_to_analyse(start_time, end_time):
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


def is_timeslot_available(timeslot, busy_times_by_calendar):
    calendars = [*busy_times_by_calendar.keys()]
    random.shuffle(calendars)

    for calendar in calendars:
        busy_times = busy_times_by_calendar[calendar]

        if _is_calendar_available_for_timeslot(busy_times, timeslot):
            logging.debug(f"{timeslot[0].format('HH:mm')}-{timeslot[1].format('HH:mm')}: {calendar}")
            return True, calendar

    return False, None


def get_one_free_timeslot_by_hour(busy_times_by_calendar, working_day_start, working_day_end):
    timeslot_by_hour = {}

    for timeslot in _get_timeslots_to_analyse(working_day_start, working_day_end):
        if timeslot[0].hour in timeslot_by_hour:
            continue

        available, calendar = is_timeslot_available(timeslot, busy_times_by_calendar)

        if available:
            timeslot_by_hour[timeslot[0].hour] = {
                'timeslot': timeslot,
                'calendar': calendar
            }

    return [*timeslot_by_hour.values()]
