import arrow
from django.test import TestCase

from workforce.models import User, Worker, AuthUser, WorkEvent
from workforce.services.events import create_cancelling_token


class UserEventsDbSetup(TestCase):
    def setUp(self) -> None:
        super().setUp()

        User.objects.create(
            email_address="b@b.com",
            full_name="John Dope",
            timezone="America/Sao_Paulo",
        )
        self.user_with_no_event = User.objects.latest('id')

        worker = Worker.objects.create(
            auth_user=AuthUser.objects.create_user('robino', 'robino'),
            timezone='America/Sao_Paulo'
        )

        User.objects.create(
            email_address="a@a.com",
            full_name="John Duh",
            timezone="America/Sao_Paulo",
        )
        self.user_with_event = User.objects.latest('id')

        start = arrow.now().shift(days=1)
        end = start.shift(minutes=20)
        token = create_cancelling_token()
        WorkEvent.objects.create(
            user=self.user_with_event,
            calendar=worker.calendar,
            comment='',
            start=start.datetime,
            end=end.datetime,
            cancelling_token=token
        )

        self.worker = worker
        self.user_event = WorkEvent.objects.latest('event_id')
        self.user_event_token = token
