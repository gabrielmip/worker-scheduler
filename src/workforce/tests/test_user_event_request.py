import os
import datetime
import unittest

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from workforce.models import User, Worker, AuthUser, Availability, WorkEvent
from workforce.utils import get_today_date_for_timezone

from .utils import create_some_image, delete_created_user_photos


@unittest.skipUnless(
    os.environ.get('INCLUDE_E2E') == 'true',
    'Skipping test because of missing env INCLUDE_E2E')
class GenericDriverSetup(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        cls.selenium = Chrome(options=chrome_options)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        User.objects.create(
            email_address="b@a.com",
            full_name="John Deo",
            timezone="America/Sao_Paulo",
            photo=create_some_image()
        )
        self.user_with_photo = User.objects.latest('id')

        User.objects.create(
            email_address="b@b.com",
            full_name="John Dope",
            timezone="America/Sao_Paulo",
        )
        self.other_user = User.objects.latest('id')

    def tearDown(self):
        delete_created_user_photos()

    def insert_registered_email_and_click(self):
        self.selenium.get(self.live_server_url)
        self.selenium.find_element_by_id('user-is-registered-btn').click()

        email_input = self.selenium.find_element_by_id('registered-email')
        email_input.send_keys(self.user_with_photo.email_address)
        email_input.submit()


class TestNoTimeslotAvailable(GenericDriverSetup):
    def setUp(self) -> None:
        super().setUp()
        self.insert_registered_email_and_click()

    def test_timeslot_choosing(self):
        with self.assertRaises(NoSuchElementException):
            element = self.selenium.find_element_by_name('timeslots_available')
            timeslot_dropdown = Select(element)
            timeslot_dropdown.select_by_index(0)


class TestSuccessfulEventRequest(GenericDriverSetup):
    def setUp(self) -> None:
        super().setUp()
        auth_user = AuthUser.objects.create_user('robinho', 'robinho')
        worker = Worker.objects.create(
            auth_user=auth_user,
            timezone='Asia/Tokyo'
        )  # +9 hours timezone offset
        today_day_of_the_week = get_today_date_for_timezone(
            worker.timezone).shift(days=1).date()
        Availability.objects.create(
            worker=worker,
            day_of_the_week=today_day_of_the_week.weekday() + 1,
            start_time=datetime.time(0, 0),
            end_time=datetime.time(3, 0)
        )  # 9 timeslots
        self.insert_registered_email_and_click()

    def tearDown(self) -> None:
        super().tearDown()

    def test_timeslot_dropdown_has_options(self):
        timeslot_dropdown_element = self.selenium.find_element_by_name(
            'timeslots_available')
        timeslot_dropdown = Select(timeslot_dropdown_element)
        self.assertEquals(len(timeslot_dropdown.options), 9)

    def test_can_select_timezone_and_submit(self):
        current_work_event_count = WorkEvent.objects.count()

        element = self.selenium.find_element_by_name('timeslots_available')
        timeslot_dropdown = Select(element)
        timeslot_dropdown.select_by_index(0)
        element.submit()

        updated_work_event_count = WorkEvent.objects.count()

        self.assertEquals(updated_work_event_count, current_work_event_count +
                          1, 'Event was not created in database')


class TestSuccessfulEventRequestsSimultaneously(GenericDriverSetup):
    def setUp(self) -> None:
        super().setUp()
        auth_user = AuthUser.objects.create_user('robinho', 'robinho')
        worker = Worker.objects.create(
            auth_user=auth_user,
            timezone='Asia/Tokyo'
        )  # +9 hours timezone offset
        today_day_of_the_week = get_today_date_for_timezone(
            worker.timezone).shift(days=1).date()
        Availability.objects.create(
            worker=worker,
            day_of_the_week=today_day_of_the_week.weekday() + 1,
            start_time=datetime.time(0, 0),
            end_time=datetime.time(3, 0)
        )  # 9 timeslots
        self.worker = worker
        self.insert_registered_email_and_click()

    def test_can_select_timezone_and_submit_successfully_simultaneously(self):
        current_work_event_count = WorkEvent.objects.count()
        timeslot_dropdown_element = self.selenium.find_element_by_name(
            'timeslots_available')
        timeslot_dropdown = Select(timeslot_dropdown_element)

        option_to_be_selected_by_other = timeslot_dropdown.options[1]
        _, start, end = (option_to_be_selected_by_other
                         .get_attribute('value')
                         .split('|'))
        WorkEvent.objects.create(
            start=start,
            end=end,
            calendar=self.worker.calendar,
            user=self.other_user
        )

        timeslot_dropdown.select_by_index(0)
        timeslot_dropdown_element.submit()

        updated_work_event_count = WorkEvent.objects.count()

        self.assertEquals(
            updated_work_event_count,
            current_work_event_count + 2,
            'Could not create event when another was created simultaneously'
        )
