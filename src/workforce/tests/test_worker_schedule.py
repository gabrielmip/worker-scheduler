import unittest
from datetime import time, datetime

import arrow
from django.test import TestCase, Client
import workforce

from workforce.views.my_schedule import _get_today_events
from workforce.models import Worker, WorkEvent, AuthUser, User
from workforce.utils import get_today_date_for_timezone


class TestWorkerSchedule(TestCase):

    def setUp(self):
        User.objects.create(
            email_address="a@a.com",
            full_name="John Doe",
            timezone="America/Sao_Paulo")
        self.user_without_photo = User.objects.latest('id')

        self.auth_user_br = AuthUser.objects.create_user('robson', 'robson')
        self.from_sao_paulo = Worker.objects.create(
            auth_user=self.auth_user_br,
            timezone='America/Sao_Paulo') # -3

        self.auth_user_japan = AuthUser.objects.create_user('robinho', 'robinho')
        self.from_japan = Worker.objects.create(
            auth_user=self.auth_user_japan,
            timezone='Asia/Tokyo') # +9


    def test_considering_worker_when_negative_offsets_upper_limit(self):
        ''' the Apr 1st for someone that lives in a -3 offset goes from Mar 31st 21:00 to Apr 1st 20:59 '''
        created_event = create_event_at(time(23, 30), self.from_sao_paulo, self.user_without_photo)
        retrieved_events = _get_today_events(self.from_sao_paulo)
        self.assertCountEqual(to_comparable(retrieved_events), to_comparable([created_event]))


    def test_considering_worker_when_negative_offsets_lower_limit(self):
        ''' the Apr 1st for someone that lives in a -3 offset goes from Mar 31st 21:00 to Apr 1st 20:59 '''
        created_event = create_event_at(time(0, 0), self.from_sao_paulo, self.user_without_photo)
        retrieved_events = _get_today_events(self.from_sao_paulo)
        self.assertCountEqual(to_comparable(retrieved_events), to_comparable([created_event]))


    def test_considering_worker_when_positive_offsets_upper_limit(self):
        ''' the Apr 1st for someone that lives in a +9 offset goes from
            Apr 1st 9:00 to Apr 2st 8:59
        '''
        created_event = create_event_at(time(23, 30), self.from_japan, self.user_without_photo)
        retrieved_events = _get_today_events(self.from_japan)
        self.assertCountEqual(to_comparable(retrieved_events), to_comparable([created_event]))


    def test_considering_worker_when_positive_offsets_lower_limit(self):
        ''' the Apr 1st for someone that lives in a +9 offset goes from
            Apr 1st 9:00 to Apr 2st 8:59
        '''
        created_event = create_event_at(time(0, 0), self.from_japan, self.user_without_photo)
        retrieved_events = _get_today_events(self.from_japan)
        self.assertCountEqual(to_comparable(retrieved_events), to_comparable([created_event]))


    def test_can_show_empty_schedule(self):
        client = Client()
        client.force_login(self.auth_user_br)
        client.get('/my_schedule')


    def test_can_show_schedule_with_events_without_photo(self):
        create_event_at(time(3, 0), self.from_sao_paulo, self.user_without_photo)
        create_event_at(time(7, 0), self.from_sao_paulo, self.user_without_photo)

        client = Client()
        client.force_login(self.auth_user_br)
        response = client.get('/my_schedule')
        self.assertTrue(len(response.context['today_events']) == 2, 'Number of events differs')
        self.assertTrue(response.status_code == 200)


def to_comparable(events):
    return [(e.user_id, e.start, e.end) for e in events]


def create_event_at(hour, worker, user):
    today_for_worker = get_today_date_for_timezone(worker.timezone).date()
    start = arrow.get(datetime.combine(today_for_worker, hour)).replace(tzinfo=worker.timezone)
    return WorkEvent.objects.create(
        user=user,
        start=start.datetime,
        end=start.shift(minutes=20).datetime,
        calendar=worker.calendar)
