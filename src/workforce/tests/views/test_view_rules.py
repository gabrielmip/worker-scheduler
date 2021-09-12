import unittest
from django.http.response import HttpResponseRedirect
from django.test import TestCase, RequestFactory
from workforce.models import User
from workforce.tests.helpers import create_some_image, delete_created_user_photos
from workforce.views.rules import finished_registration_required


class TestFinishedRegistrationRequired(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/asdf')
        self.request.session = {}
        self.mocked_fn = unittest.mock.MagicMock(
            return_value='did not redirect')
        self.decorated_fn = finished_registration_required(self.mocked_fn)

    def tearDown(self):
        delete_created_user_photos()

    def test_redirect_no_user(self):
        response = self.decorated_fn(self.request)
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_redirect_when_user_exists_but_is_incomplete(self):
        User.objects.create(
            email_address="b@a.com",
            full_name="John Deo",
            timezone="America/Sao_Paulo",
        )

        self.request.user = User.objects.latest('id')
        self.request.session = {
            'email_address': self.request.user.email_address}
        response = self.decorated_fn(self.request)
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_does_not_redirect_when_user_exists_and_is_complete(self):
        User.objects.create(
            email_address="b@a.com",
            full_name="John Deo",
            timezone="America/Sao_Paulo",
            photo=create_some_image()
        )

        self.request.user = User.objects.latest('id')
        self.request.session = {
            'email_address': self.request.user.email_address}
        response = self.decorated_fn(self.request)
        self.assertEqual(response, 'did not redirect')
