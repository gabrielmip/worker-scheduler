import datetime
from unittest import TestCase

import arrow
from django.contrib.auth import get_user_model
from django.test import TestCase

from workforce.models import Calendar, Patient, Worker, Availability, WorkEvent
from workforce.utils import get_today_date_for_timezone


def get_tomorrow(timezone, **kwargs):
    return get_today_date_for_timezone(timezone).shift(days=1).replace(second=0, microsecond=0, **kwargs)


class WorkerAvailabilityDbSetup(TestCase):
    def setUp(self) -> None:
        super().setUp()
        auth_user = get_user_model().objects.create_user('robinho', 'robinho')

        nihon_worker = Worker.objects.create(
            auth_user=auth_user,
            timezone='Asia/Tokyo'
        )

        auth_user_2 = get_user_model().objects.create_user('robino', 'robino')

        sampa_worker = Worker.objects.create(
            auth_user=auth_user_2,
            timezone='America/Sao_Paulo'
        )

        Availability.objects.create(
            worker=nihon_worker,
            day_of_the_week=get_tomorrow(
                nihon_worker.timezone).date().weekday() + 1,
            start_time=datetime.time(1, 0),
            end_time=datetime.time(1, 20)
        )  # 1 timeslot

        Availability.objects.create(
            worker=sampa_worker,
            day_of_the_week=get_tomorrow(
                sampa_worker.timezone).date().weekday() + 1,
            start_time=datetime.time(0, 0),
            end_time=datetime.time(1, 0)
        )  # 3 timeslots

        # creating user + one event
        Patient.objects.create(
            email_address="b@b.com",
            full_name="John Dope",
            timezone="America/Sao_Paulo",
        )
        user = Patient.objects.latest('id')
        start = arrow.now().shift(days=1)
        end = start.shift(minutes=20)

        WorkEvent.objects.create(
            user=user,
            calendar=sampa_worker.calendar,
            comment='',
            start=start.datetime,
            end=end.datetime,
        )

        self.sampa_worker_event_start = start
        self.sampa_worker_event_end = end
        self.sampa_worker = sampa_worker
        self.nihon_worker = nihon_worker
        self.calendar_ids = {
            calendar.calendar_id
            for calendar in Calendar.objects.all()
        }
