from django.test import TestCase, RequestFactory, override_settings
from django.conf import settings
from rest_framework import exceptions
from ..auth import APIKeyAuthentication


@override_settings(EXTERNAL_API_KEY='test-api-key-123')
class APIKeyAuthenticationTest(TestCase):
    def setUp(self):
        self.auth = APIKeyAuthentication()
        self.factory = RequestFactory()

    def test_authentication_with_valid_key(self):
        request = self.factory.get('/')
        request.headers = {'x-api-key': 'test-api-key-123'}
        
        result = self.auth.authenticate(request)
        self.assertEqual(result, (None, None))

    def test_authentication_without_key(self):
        request = self.factory.get('/')
        request.headers = {}
        
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)
        self.assertEqual(str(context.exception), 'No API key provided')

    def test_authentication_with_invalid_key(self):
        request = self.factory.get('/')
        request.headers = {'x-api-key': 'invalid-key'}
        
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)
        self.assertEqual(str(context.exception), 'Invalid API key')

    def test_authentication_with_wrong_header_case(self):
        request = self.factory.get('/')
        request.headers = {'X-API-KEY': 'test-api-key-123'}
        
        result = self.auth.authenticate(request)
        self.assertEqual(result, (None, None))

    def test_authentication_with_empty_key(self):
        request = self.factory.get('/')
        request.headers = {'x-api-key': ''}
        
        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth.authenticate(request)
        self.assertEqual(str(context.exception), 'No API key provided') 