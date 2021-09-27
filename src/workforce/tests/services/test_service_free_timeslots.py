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
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=0, hour=1),
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=20, hour=1),
                    ),
                    'calendar_id': self.nihon_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=20, hour=0),
                    ),
                    'calendar_id': self.sampa_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=20, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=40, hour=0),
                    ),
                    'calendar_id': self.sampa_worker.calendar_id
                },
                {
                    'timeslot': (
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=40, hour=0),
                        get_tomorrow(self.sampa_worker.timezone,
                                     minute=0, hour=1),
                    ),
                    'calendar_id': self.sampa_worker.calendar_id
                },

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
                                     minute=60, hour=10),
                    ),
                    'calendar_id': self.sampa_worker.calendar_id
                },
            ]
        )
