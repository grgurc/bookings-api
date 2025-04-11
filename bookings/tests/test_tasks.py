from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from bookings.tasks import (
    sync_all_bookings,
    sync_latest_bookings,
    update_active_bookings,
    process_bookings_page,
    parse_booking
)
from bookings.models import Booking


class TestBookingTasks(TestCase):
    def setUp(self):
        self.sample_booking_data = {
            'id': '123',
            'bookingCode': 'ABC123',
            'bookingStatus': 'CONFIRMED',
            'experience': {'name': 'Test Experience'},
            'rateName': 'Standard Rate',
            'bookingCreated': '2024-04-11T10:00:00',
            'ratesQuantity': [{'quantity': 2}],
            'price': {
                'finalRetailPrice': {
                    'currency': 'USD',
                    'amount': 100.00
                }
            }
        }

    @patch('bookings.tasks.process_sync_pages')
    def test_sync_all_bookings(self, mock_process_sync_pages):
        sync_all_bookings(is_sync=True)
        mock_process_sync_pages.assert_called_once_with({}, is_sync=True)

    @patch('bookings.tasks.process_sync_pages')
    def test_sync_latest_bookings_with_existing(self, mock_process_sync_pages):
        Booking.objects.create(
            id='123',
            code='ABC123',
            status='CONFIRMED',
            experience='Test Experience',
            rate='Standard Rate',
            booking_created=timezone.now() - timedelta(days=1),
            participants=2,
            original_currency='USD',
            price_original_currency=100.00
        )

        sync_latest_bookings()
        mock_process_sync_pages.assert_called_once()
        call_args = mock_process_sync_pages.call_args[0][0]
        self.assertIn('bookingCreated[gt]', call_args)

    @patch('bookings.tasks.process_sync_pages')
    def test_sync_latest_bookings_without_existing(self, mock_process_sync_pages):
        sync_latest_bookings()
        mock_process_sync_pages.assert_not_called()

    @patch('bookings.tasks.fetch_single_booking')
    def test_update_active_bookings(self, mock_fetch_booking):
        booking = Booking.objects.create(
            id='123',
            code='ABC123',
            status='PENDING',
            experience='Test Experience',
            rate='Standard Rate',
            booking_created=timezone.now(),
            participants=2,
            original_currency='USD',
            price_original_currency=100.00
        )

        mock_fetch_booking.return_value = self.sample_booking_data

        update_active_bookings()

        updated_booking = Booking.objects.get(id='123')
        self.assertEqual(updated_booking.status, 'CONFIRMED')
        self.assertEqual(updated_booking.experience, 'Test Experience')  

    def test_parse_booking(self):
        parsed = parse_booking(self.sample_booking_data)
        
        self.assertEqual(parsed['id'], '123')
        self.assertEqual(parsed['code'], 'ABC123')
        self.assertEqual(parsed['status'], 'CONFIRMED')
        self.assertEqual(parsed['experience'], 'Test Experience')
        self.assertEqual(parsed['rate'], 'Standard Rate')
        self.assertEqual(parsed['participants'], 2)
        self.assertEqual(parsed['original_currency'], 'USD')
        self.assertEqual(parsed['price_original_currency'], 100.00)
        self.assertIsInstance(parsed['booking_created'], datetime)

    @patch('bookings.tasks.fetch_bookings_page')
    @patch('bookings.tasks.process_bookings_from_response')
    def test_process_bookings_page(self, mock_process_bookings, mock_fetch_page):
        mock_fetch_page.return_value = {
            'results': [self.sample_booking_data]
        }

        process_bookings_page({'page': 1})

        mock_process_bookings.assert_called_once_with(mock_fetch_page.return_value) 