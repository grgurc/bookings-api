import logging
import requests
import math
from datetime import datetime
from django.utils import timezone
from django.db import transaction

from django.conf import settings
from celery import shared_task

from bookings.models import Booking

logger = logging.getLogger(__name__)

external_api_url = settings.EXTERNAL_API_URL
external_api_key = settings.EXTERNAL_API_KEY


@shared_task
def sync_all_bookings(is_sync=False):
    process_sync_pages({}, is_sync=is_sync)


@shared_task
def sync_latest_bookings():
    latest_booking = Booking.objects.order_by('-booking_created').first()
    base_params = {}
    if latest_booking:
        booking_created_gt = latest_booking.booking_created.isoformat()
        base_params['bookingCreated[gt]'] = booking_created_gt
        process_sync_pages(base_params, False)


def process_sync_pages(base_params, is_sync=False):
    try:
        response = fetch_bookings_page(base_params)
        total_items = response.get('count', 0)
        items_per_page = len(response.get('results', []))
        
        if items_per_page > 0:
            total_pages = math.ceil(total_items / items_per_page)

            for page in range(1, total_pages + 1):
                params = base_params.copy()
                params['page'] = page
                if is_sync:
                    process_bookings_page(params=params)
                else:
                    process_bookings_page.delay(params=params)
                
    except Exception as e:
        logger.error(f"Error in bookings synchronization: {str(e)}")
        raise


@shared_task
def process_bookings_page(params):
    try:
        response = fetch_bookings_page(params)
        with transaction.atomic():
            process_bookings_from_response(response)
    except Exception as e:
        logger.error(f"Error processing bookings page {params.get('page', 1)}: {str(e)}")
        raise


def fetch_bookings_page(params):
    res = requests.get(url=external_api_url, params=params, headers={'x-api-key': external_api_key})
    res.raise_for_status()
    
    return res.json()


def process_bookings_from_response(response):
    for booking_data in response['results']:
        try:
            parsed_booking = parse_booking(booking_data)
            booking, created = Booking.objects.update_or_create(
                id=parsed_booking['id'],
                defaults=parsed_booking
            )

        except Exception as e:
            logger.error(f"Error processing booking {booking_data.get('id', 'unknown')}: {str(e)}")
            continue


@shared_task
def update_active_bookings():
    active_bookings = Booking.objects.exclude(
        status__in=['CANCELLED', 'COMPLETED']
    ).order_by('booking_created')

    for booking in active_bookings:
        try:
            booking_data = fetch_single_booking(booking.id)
            parsed_booking = parse_booking(booking_data)
            
            with transaction.atomic():
                Booking.objects.filter(id=booking.id).update(**parsed_booking)
                
        except Exception as e:
            logger.error(f"Error updating booking {booking.id}: {str(e)}")
            continue


def parse_booking(booking):
    return {
        'id': booking['id'],
        'code': booking['bookingCode'],
        'status': booking['bookingStatus'],
        'experience': booking['experience']['name'],
        'rate': booking['rateName'],
        'booking_created': timezone.make_aware(datetime.fromisoformat(booking['bookingCreated'].replace('Z', '+00:00'))),
        'participants': sum(rate['quantity'] for rate in booking['ratesQuantity']),
        'original_currency': booking['price']['finalRetailPrice']['currency'],
        'price_original_currency': booking['price']['finalRetailPrice']['amount'],
    }


def fetch_single_booking(booking_id):
    url = f"{external_api_url}/{booking_id}"
    res = requests.get(url=url, headers={'x-api-key': external_api_key})
    res.raise_for_status()
    return res.json()
