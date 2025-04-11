from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Booking


class BookingModelTest(TestCase):
    def setUp(self):
        self.valid_booking_data = {
            'id': 'test123',
            'code': 'BOOK123',
            'status': 'PENDING',
            'experience': 'Test Experience',
            'rate': 'Standard',
            'booking_created': timezone.now(),
            'participants': 2,
            'original_currency': 'USD',
            'price_original_currency': 100.00
        }

    def test_create_booking_with_valid_data(self):
        booking = Booking.objects.create(**self.valid_booking_data)
        self.assertEqual(booking.id, 'test123')
        self.assertEqual(booking.code, 'BOOK123')
        self.assertEqual(booking.status, 'PENDING')
        self.assertEqual(booking.experience, 'Test Experience')
        self.assertEqual(booking.participants, 2)
        self.assertEqual(booking.original_currency, 'USD')
        self.assertEqual(booking.price_original_currency, 100.00)

    def test_booking_status_choices(self):
        valid_statuses = ['ON_HOLD', 'PENDING', 'ACCEPTED', 'COMPLETED', 'CANCELLED', 'EXPIRED', 'REJECTED']
        for i, status in enumerate(valid_statuses):
            booking_data = self.valid_booking_data.copy()
            booking_data['id'] = f'test_status_{i}'
            booking_data['status'] = status
            booking = Booking.objects.create(**booking_data)
            self.assertEqual(booking.status, status)

        booking_data = self.valid_booking_data.copy()
        booking_data['id'] = 'test_invalid_status'
        booking_data['status'] = 'INVALID_STATUS'
        with self.assertRaises(ValidationError):
            booking = Booking.objects.create(**booking_data)
            booking.full_clean()

    def test_booking_ordering(self):
        now = timezone.now()
        
        booking1 = Booking.objects.create(
            **{**self.valid_booking_data, 'id': 'test_order_1', 'booking_created': now - timezone.timedelta(days=1)}
        )
        booking2 = Booking.objects.create(
            **{**self.valid_booking_data, 'id': 'test_order_2', 'booking_created': now}
        )
        booking3 = Booking.objects.create(
            **{**self.valid_booking_data, 'id': 'test_order_3', 'booking_created': now - timezone.timedelta(days=2)}
        )

        bookings = Booking.objects.all()
        
        self.assertEqual(bookings[0], booking2)
        self.assertEqual(bookings[1], booking1)
        self.assertEqual(bookings[2], booking3)

    def test_required_fields(self):
        required_fields = ['status', 'experience', 'rate', 'booking_created', 
                         'participants', 'original_currency', 'price_original_currency']
        
        for i, field in enumerate(required_fields):
            booking_data = self.valid_booking_data.copy()
            booking_data['id'] = f'test_required_{i}'
            booking = Booking.objects.create(**booking_data)
            
            setattr(booking, field, None)
            with self.assertRaises(ValidationError):
                booking.full_clean()

    def test_field_length_validation(self):
        booking_data = self.valid_booking_data.copy()
        booking_data['id'] = 'a' * 51
        with self.assertRaises(ValidationError):
            booking = Booking.objects.create(**booking_data)
            booking.full_clean()

        booking_data = self.valid_booking_data.copy()
        booking_data['id'] = 'test_length_2'
        booking_data['experience'] = 'a' * 256
        with self.assertRaises(ValidationError):
            booking = Booking.objects.create(**booking_data)
            booking.full_clean() 