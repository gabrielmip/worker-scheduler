import arrow
from workforce.models import Calendar, WorkEvent

from workforce.services.events import create_cancelling_token, delete_event, get_all_events_by_calendar, get_event_to_delete, get_user_next_event, is_cancelling_token
from workforce.tests.services.user_events_db_setup import UserEventsDbSetup


class TestServiceGetUserNextEvent(UserEventsDbSetup):
    def test_none_if_user_does_not_exist(self):
        self.assertIsNone(get_user_next_event('asdf@asdf.com'))

    def test_user_no_event_schedule(self):
        self.assertIsNone(get_user_next_event(
            self.user_with_no_event.email_address))

    def test_returns_the_user_s_event(self):
        self.assertEqual(
            get_user_next_event(self.user_with_event.email_address),
            self.user_event
        )


class TestServiceGetEventToDelete(UserEventsDbSetup):
    def test_gets_event_by_token(self):
        self.assertEqual(
            get_event_to_delete(self.user_event_token),
            self.user_event
        )

    def test_only_gets_future_events(self):
        start = arrow.now().shift(days=-1)
        end = start.shift(minutes=20)
        token = create_cancelling_token()

        WorkEvent.objects.create(
            user=self.user_with_event,
            calendar=self.worker.calendar,
            comment='',
            start=start.datetime,
            end=end.datetime,
            cancelling_token=token
        )

        self.assertIsNone(get_event_to_delete(token))


class TestServiceIsCancellingToken(UserEventsDbSetup):
    def test_confirms_if_comes_from_creation_fn(self):
        self.assertTrue(is_cancelling_token(create_cancelling_token()))

    def test_rejects_if_mumbo_jumbo(self):
        self.assertFalse(is_cancelling_token('asodf8asodifj209fslkdj'))

    def test_rejects_if_none(self):
        self.assertFalse(is_cancelling_token(None))

    def test_rejects_if_empty(self):
        self.assertFalse(is_cancelling_token(''))


class TestDeleteEvent(UserEventsDbSetup):
    def test_deletes_event_if_exists(self):
        prior_event_ids = {w.event_id for w in WorkEvent.objects.all()}
        id_to_be_deleted = self.user_event.event_id

        delete_event(self.user_event.cancelling_token)
        prior_event_ids.remove(id_to_be_deleted)

        expected = prior_event_ids
        post_event_ids = {w.event_id for w in WorkEvent.objects.all()}

        self.assertSetEqual(post_event_ids, expected)

    def test_does_not_raise_if_does_not_exist(self):
        self.assertIsNone(delete_event('0a98sdf0a9sd87f'))

    def test_does_not_remove_anything_if_does_not_find(self):
        prior_event_ids = {w.event_id for w in WorkEvent.objects.all()}
        delete_event('0a98sdf0a9sd87f')
        post_event_ids = {w.event_id for w in WorkEvent.objects.all()}

        self.assertSetEqual(post_event_ids, prior_event_ids)


class TestGetAllEventsByCalendar(UserEventsDbSetup):
    def setUp(self) -> None:
        super().setUp()

        # adds extra live event
        start = arrow.now().shift(days=1)
        WorkEvent.objects.create(
            user=self.user_with_event,
            calendar=self.worker.calendar,
            comment='',
            start=start.datetime,
            end=start.shift(minutes=20).datetime,
            is_live=True,
            cancelling_token=create_cancelling_token()
        )
        self.live_work_event = WorkEvent.objects.latest('event_id')

    def test_work_events_at_distance(self):
        calendar_ids = [c.calendar_id for c in Calendar.objects.all()]
        start = arrow.get()
        # arbitrary shift, just to comtemplate every created event
        end = arrow.get().shift(days=30)

        self.assertEqual(
            get_all_events_by_calendar(
                calendar_ids, start, end, is_live=False
            ),
            {
                self.worker.calendar_id: [
                    (
                        arrow.get(self.user_event.start),
                        arrow.get(self.user_event.end)
                    )
                ]
            }
        )

    def test_live_work_events(self):
        calendar_ids = [c.calendar_id for c in Calendar.objects.all()]
        start = arrow.get()
        # arbitrary shift, just to comtemplate every created event
        end = arrow.get().shift(days=30)

        self.assertEqual(
            get_all_events_by_calendar(
                calendar_ids, start, end, is_live=True),
            {
                self.worker.calendar_id: [
                    (
                        arrow.get(self.live_work_event.start),
                        arrow.get(self.live_work_event.end)
                    )
                ]
            }
        )
