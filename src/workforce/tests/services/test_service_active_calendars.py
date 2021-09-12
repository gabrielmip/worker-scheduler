import datetime
from django.conf import settings
from django.test import TestCase
from workforce.models import Availability

from workforce.services.active_calendars import get_active_worker_calendars
from workforce.tests.services.worker_availability_db_setup import WorkerAvailabilityDbSetup, get_tomorrow


def find_calendar(calendars, calendar_id):
    return [
        c for c in calendars
        if c['id'] == calendar_id
    ][0]


class TestEmptyGetActiveWorkerCalendars(TestCase):
    def test_empty_workers(self):
        self.assertListEqual(get_active_worker_calendars(), [])


class TestGetActiveWorkerCalendars(WorkerAvailabilityDbSetup):

    def test_returns_one_by_calendar(self):
        response = get_active_worker_calendars()
        ids = {calendar['id'] for calendar in response}

        self.assertEqual(len(response), 2)
        self.assertSetEqual(ids, self.calendar_ids)

    def test_sampa_worker_availabilities(self):
        response = get_active_worker_calendars()
        calendar = find_calendar(response, self.sampa_worker.calendar_id)

        self.assertEqual(calendar['availabilities'], [
            (get_tomorrow(self.sampa_worker.timezone, minute=0, hour=0).to(settings.TIME_ZONE),
             get_tomorrow(self.sampa_worker.timezone, minute=0, hour=1).to(settings.TIME_ZONE)),
        ])

    def test_sampa_worker_busy_timeslots(self):
        response = get_active_worker_calendars()
        calendar = find_calendar(response, self.sampa_worker.calendar_id)

        self.assertEqual(calendar['busy_timeslots'], [
            (self.sampa_worker_event_start, self.sampa_worker_event_end)
        ])

    def test_sampa_worker_with_live_availabilities(self):
        Availability.objects.create(
            worker=self.sampa_worker,
            day_of_the_week=get_tomorrow(
                self.sampa_worker.timezone).date().weekday() + 1,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(10, 20),
            is_live=True
        )

        response = get_active_worker_calendars(is_live=True)
        calendar = find_calendar(response, self.sampa_worker.calendar_id)

        self.assertEqual(calendar['availabilities'], [
            (get_tomorrow(self.sampa_worker.timezone, minute=0, hour=10).to(settings.TIME_ZONE),
             get_tomorrow(self.sampa_worker.timezone, minute=20, hour=10).to(settings.TIME_ZONE)),
        ])

    def test_nihon_worker_availabilities(self):
        response = get_active_worker_calendars()
        calendar = find_calendar(response, self.nihon_worker.calendar_id)

        self.assertEqual(calendar['availabilities'], [
            (get_tomorrow(self.nihon_worker.timezone, minute=0, hour=1).to(settings.TIME_ZONE),
             get_tomorrow(self.nihon_worker.timezone, minute=20, hour=1).to(settings.TIME_ZONE)),
        ])

    def test_nihon_worker_empty_busy_timeslots(self):
        response = get_active_worker_calendars()
        calendar = find_calendar(response, self.nihon_worker.calendar_id)

        self.assertEqual(len(calendar['busy_timeslots']), 0)
