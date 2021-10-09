import datetime
from django.conf import settings
from workforce.models import Availability
from workforce.services.free_timeslots import get_free_timeslots
from workforce.tests.services.worker_availability_db_setup import WorkerAvailabilityDbSetup
from workforce.utils import get_today_date_for_timezone


def get_tomorrow(timezone, **kwargs):
    return (get_today_date_for_timezone(timezone)
            .shift(days=1)
            .replace(second=0, microsecond=0, **kwargs)
            .to(settings.TIME_ZONE))


class TestGetFreeTimeslots(WorkerAvailabilityDbSetup):

    def setUp(self) -> None:
        super().setUp()
        Availability.objects.create(
            worker=self.sampa_worker,
            day_of_the_week=get_tomorrow(
                self.sampa_worker.timezone).date().weekday() + 1,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            is_live=True
        )

    def test_not_live_timeslots(self):
        response = get_free_timeslots()
        self.maxDiff = None
        self.assertEqual(
            response,
            [
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=20, hour=0),
                    ),
                    'available_count': 1,
                    'calendar_id': self.sampa_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=20, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=40, hour=0),
                    ),
                    'available_count': 1,
                    'calendar_id': self.sampa_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=40, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=1),
                    ),
                    'available_count': 1,
                    'calendar_id': self.sampa_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=0, hour=1),
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=20, hour=1),
                    ),
                    'available_count': 1,
                    'calendar_id': self.nihon_worker.calendar_id
                }
            ]
        )

    def test_live_timeslots(self):
        response = get_free_timeslots(is_live=True)
        self.assertEqual(
            response,
            [
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=10),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=11),
                    ),
                    'available_count': 1,
                    'calendar_id': self.sampa_worker.calendar_id
                },
            ]
        )

    def test_start_in_the_past_does_not_show_up(self):
        Availability.objects.all().delete()

        right_now = (get_today_date_for_timezone(self.nihon_worker.timezone)
                     .replace(second=0, microsecond=0))

        Availability.objects.create(
            worker=self.nihon_worker,
            day_of_the_week=right_now.date().weekday() + 1,
            start_time=right_now.shift(hours=-1).time(),
            end_time=right_now.shift(hours=3).time(),
            is_live=True
        )

        response = get_free_timeslots(is_live=True)
        self.assertEqual(response, [])
