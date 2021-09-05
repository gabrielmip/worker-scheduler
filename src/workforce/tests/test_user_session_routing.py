from django.test import TestCase, Client
from workforce.models import User

from .utils import (
    get_client_with_user_in_session,
    create_some_image,
    delete_created_user_photos
)


class TestUserSessionRouting(TestCase):
    def setUp(self):
        User.objects.create(
            email_address="a@a.com",
            full_name="John Doe",
            timezone="America/Sao_Paulo"
        )
        self.user_without_photo = User.objects.latest('id')

        User.objects.create(
            email_address="b@a.com",
            full_name="John Deo",
            timezone="America/Sao_Paulo",
            photo=create_some_image()
        )
        self.user_with_photo = User.objects.latest('id')
        self.client = Client()

    def tearDown(self):
        delete_created_user_photos()

    def test_no_redirect_when_user_not_exists(self):
        response = self.client.post(
            '/',
            {'registered_email': 'mumbojumbo@jumbomumbo.com'},
            follow=True)
        self.assertEqual(len(response.redirect_chain), 0)

    def test_redirect_when_user_exists_but_is_incomplete(self):
        response = self.client.post('/', {
            'registered_email': self.user_without_photo.email_address
        })
        self.assertEqual(response.url, '/registration')

    def test_redirect_to_schedule_if_exists_and_is_complete(self):
        response = self.client.post(
            '/', {'registered_email': self.user_with_photo.email_address})
        self.assertEqual(response.url, '/schedule')

    def test_remove_cookies_from_welcome_request(self):
        client = get_client_with_user_in_session(self.user_without_photo)
        response = client.get('/')
        self.assertFalse(
            response.client.session.has_key('email_address'),
            'session remained with email_address')

    def test_registration_no_redirect_when_is_new(self):
        response = self.client.get('/registration', follow=True)
        self.assertTrue(len(response.redirect_chain) ==
                        0, 'there was a redirection')

    def test_registration_no_redirect_when_has_missing_fields(self):
        client = Client()
        session = client.session
        session['email_address'] = self.user_without_photo.email_address
        session.save()
        response = client.get('/registration', follow=True)
        self.assertTrue(len(response.redirect_chain) ==
                        0, 'there was a redirection')

    def test_registration_redirect_when_user_is_complete(self):
        client = get_client_with_user_in_session(self.user_with_photo)
        response = client.get('/registration', follow=True)
        self.assertGreater(len(response.redirect_chain), 0,
                           'complete user was not redirected')

    def test_can_register_new_user(self):
        previous_count = User.objects.filter(
            email_address='robert@pattin.son').count()

        response = Client().post('/registration', {
            'full_name': 'Robert Pattinson',
            'email_address': 'robert@pattin.son',
            'timezone': 'America/Sao_Paulo',
            'photo': create_some_image()
        }, follow=True)
        self.assertGreater(len(response.redirect_chain), 0,
                           'new user was not redirected')
        self.assertEqual(response.client.session.get(
            'email_address'), 'robert@pattin.son')

        after_count = User.objects.filter(
            email_address='robert@pattin.son').count()
        self.assertEqual(previous_count + 1, after_count)

    def test_cannot_change_address_to_existing_one(self):
        client = Client()
        session = client.session
        session['email_address'] = self.user_without_photo.email_address
        session.save()

        response = client.post('/registration', {
            'full_name': self.user_without_photo.full_name,
            'email_address': self.user_with_photo.email_address,
            'timezone': self.user_without_photo.timezone,
            'photo': create_some_image()
        }, follow=True)
        self.assertEqual(len(response.redirect_chain), 0)

        possibly_updated_user = User.objects.get(pk=self.user_with_photo.id)
        self.assertEqual(possibly_updated_user.full_name,
                         self.user_with_photo.full_name)
