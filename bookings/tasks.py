import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

external_api_url = settings.EXTERNAL_API_URL
external_api_key = settings.EXTERNAL_API_KEY


def fetch_bookings(params):
    res = requests.get(url=external_api_url, params=params, headers={'x-api-key': external_api_key})
    res.raise_for_status()
    
    return res.json()


def parse_booking(booking):
    return {
        'id': booking['id'],
        'code': booking['bookingCode'],
        'status': booking['bookingStatus'],
        'experience': booking['experience']['name'],
        'rate': booking['rateName'],
        'bookingCreated': booking['bookingCreated'],
        'participants': sum(rate['quantity'] for rate in booking['ratesQuantity']),
        'originalCurrency': booking['price']['finalRetailPrice']['currency'],
        'priceOriginalCurrency': booking['price']['finalRetailPrice']['amount'],
    }


def convert_booking(booking, requested_currency, coefficient):
    original_price = booking['priceOriginalCurrency']

    booking['requestedCurrency'] = requested_currency
    booking['priceRequestedCurrency'] = original_price * coefficient

    return booking


def sum_bookings(bookings_list):
    final_res = {
        'bookings': [],
        'totalPriceOriginalCurrency': 0,
        'totalPriceRequestedCurrency': 0
    }

    for booking in bookings_list:
        final_res['bookings'].append({
            'code': booking['code'],
            'experience': booking['experience'],
            'rate': booking['rate'],
            'bookingCreated': booking['bookingCreated'],
            'participants': booking['participants'],
            'originalCurrency': booking['originalCurrency'],
            'priceOriginalCurrency': booking['priceOriginalCurrency'],
            'requestedCurrency': booking['requestedCurrency'],
            'priceRequestedCurrency': booking['priceRequestedCurrency'],
        })
        final_res['totalPriceOriginalCurrency'] += booking['priceOriginalCurrency']
        final_res['totalPriceRequestedCurrency'] += booking['priceRequestedCurrency']

    return final_res
