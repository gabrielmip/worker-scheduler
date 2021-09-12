from django.conf import settings
from workforce.services.free_timeslots import get_free_timeslots
from workforce.tests.services.worker_availability_db_setup import WorkerAvailabilityDbSetup
from workforce.utils import get_today_date_for_timezone


def get_tomorrow(timezone, **kwargs):
    return (get_today_date_for_timezone(timezone)
            .shift(days=1)
            .replace(second=0, microsecond=0, **kwargs)
            .to(settings.TIME_ZONE))


class TestGetFreeTimeslots(WorkerAvailabilityDbSetup):

    def test_sampa_worker_timeslots(self):
        response = get_free_timeslots()
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
                {
                    'timeslot': (
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=0, hour=1),
                        get_tomorrow(self.nihon_worker.timezone,
                                     minute=20, hour=1),
                    ),
                    'calendar_id': self.nihon_worker.calendar_id
                }
            ]
        )
