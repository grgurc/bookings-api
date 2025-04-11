from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from django.test import override_settings
from ..models import Booking
from ..views import fetch, get_filtered_bookings, convert_booking, sum_bookings
from ..request import Request


@override_settings(EXTERNAL_API_KEY='test-api-key-123')
class BookingViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_X_API_KEY='test-api-key-123')
        self.url = '/bookings/'
        
        self.now = timezone.now()
        self.booking1 = Booking.objects.create(
            id='test1',
            code='BOOK1',
            status='COMPLETED',
            experience='Test Experience 1',
            rate='Standard',
            booking_created=self.now,
            participants=2,
            original_currency='USD',
            price_original_currency=Decimal('100.00')
        )
        self.booking2 = Booking.objects.create(
            id='test2',
            code='BOOK2',
            status='COMPLETED',
            experience='Test Experience 2',
            rate='Premium',
            booking_created=self.now - timezone.timedelta(days=1),
            participants=3,
            original_currency='USD',
            price_original_currency=Decimal('150.00')
        )

    def test_fetch_without_date_filter(self):
        response = self.client.get(self.url, {
            'currency': 'EUR',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['bookings']), 2)
        self.assertEqual(Decimal(data['totalPriceOriginalCurrency']), Decimal('250.00'))
        self.assertEqual(Decimal(data['totalPriceRequestedCurrency']), Decimal('250.00'))

    def test_fetch_with_date_filter(self):
        response = self.client.get(self.url, {
            'currency': 'EUR',
            'date[gt]': self.now.isoformat(),
            'date[lt]': (self.now + timezone.timedelta(days=1)).isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['bookings']), 1)
        self.assertEqual(data['bookings'][0]['code'], 'BOOK1')

    def test_fetch_with_invalid_parameters(self):
        response = self.client.get(self.url, {
            'currency': 'XYZ'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_filtered_bookings(self):
        req = Request(
            start_time=self.now - timezone.timedelta(hours=1),
            end_time=self.now + timezone.timedelta(hours=1),
            requested_currency='EUR',
            coefficient=Decimal('1.2')
        )
        bookings = get_filtered_bookings(req)
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0].code, 'BOOK1')

    def test_convert_booking(self):
        req = Request(
            requested_currency='EUR',
            coefficient=Decimal('1.2'),
            start_time=None,
            end_time=None
        )
        converted = convert_booking(self.booking1, req)
        self.assertEqual(converted['code'], 'BOOK1')
        self.assertEqual(converted['requestedCurrency'], 'EUR')
        self.assertEqual(converted['priceRequestedCurrency'], Decimal('120.00'))

    def test_sum_bookings(self):
        bookings_list = [
            {
                'code': 'BOOK1',
                'priceOriginalCurrency': Decimal('100.00'),
                'priceRequestedCurrency': Decimal('120.00')
            },
            {
                'code': 'BOOK2',
                'priceOriginalCurrency': Decimal('150.00'),
                'priceRequestedCurrency': Decimal('180.00')
            }
        ]
        result = sum_bookings(bookings_list)
        self.assertEqual(result['totalPriceOriginalCurrency'], Decimal('250.00'))
        self.assertEqual(result['totalPriceRequestedCurrency'], Decimal('300.00'))

    def test_fetch_with_missing_required_parameters(self):
        response = self.client.get(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
