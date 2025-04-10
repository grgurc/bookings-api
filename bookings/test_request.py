from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from currency_converter import RateNotFoundError
from .request import Request

class RequestTests(TestCase):

    @patch('bookings.request.CurrencyConverter')
    def test_valid_request(self, MockConverter):
        mock_instance = MagicMock()
        mock_instance.convert.return_value = 1.2
        MockConverter.return_value = mock_instance

        params = {
            'currency': 'USD',
            'date[gt]': '2023-01-01T00:00:00',
            'date[lt]': '2023-01-31T00:00:00',
        }

        req = Request(params)
        self.assertEqual(req.requested_currency, 'USD')
        self.assertEqual(req.coefficient, 1.2)
        self.assertEqual(req.start_time, datetime.fromisoformat('2023-01-01T00:00:00'))
        self.assertEqual(req.end_time, datetime.fromisoformat('2023-01-31T00:00:00'))
        self.assertEqual(req.cache_key(), '2023-01-01 00:00:00:2023-01-31 00:00:00')
        self.assertFalse(req.open_ended())
        self.assertEqual(req.build_query_params(), {
            'sort': 'bookingCreated',
            'bookingCreated[gt]': datetime.fromisoformat('2023-01-01T00:00:00'),
            'bookingCreated[lt]': datetime.fromisoformat('2023-01-31T00:00:00'),
        })

    @patch('bookings.request.CurrencyConverter')
    def test_invalid_currency(self, MockConverter):
        mock_instance = MagicMock()
        mock_instance.convert.side_effect = RateNotFoundError()
        MockConverter.return_value = mock_instance

        params = {'currency': 'XXX'}
        with self.assertRaisesMessage(ValueError, "Invalid currency: XXX"):
            Request(params)

    @patch('bookings.request.CurrencyConverter')
    def test_invalid_date_format(self, MockConverter):
        mock_instance = MagicMock()
        mock_instance.convert.return_value = 1.0
        MockConverter.return_value = mock_instance

        params = {'currency': 'USD', 'date[gt]': 'not-a-date'}
        with self.assertRaises(ValueError) as cm:
            Request(params)
        self.assertIn("Invalid start or end time", str(cm.exception))

    @patch('bookings.request.CurrencyConverter')
    def test_open_ended_request(self, MockConverter):
        mock_instance = MagicMock()
        mock_instance.convert.return_value = 1.0
        MockConverter.return_value = mock_instance

        params = {'currency': 'USD', 'date[gt]': '2023-01-01T00:00:00'}
        req = Request(params)

        self.assertIsNotNone(req.start_time)
        self.assertIsNone(req.end_time)
        self.assertTrue(req.open_ended())
        self.assertEqual(req.build_query_params(), {
            'sort': 'bookingCreated',
            'bookingCreated[gt]': datetime.fromisoformat('2023-01-01T00:00:00'),
        })
