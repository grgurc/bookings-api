import logging
import requests

from celery import shared_task
from currency_converter import CurrencyConverter

logger = logging.getLogger(__name__)

# TODO: update rates daily
cv = CurrencyConverter()


# TODO: task retry
@shared_task
def fetch_bookings(url, params, api_key):
    try:
        res = requests.get(url=url, params=params, headers={'x-api-key': api_key})
        res.raise_for_status()
    except requests.RequestException:
        return []

    return res.json().get('results', [])


@shared_task
def process_bookings(bookings, requested_currency):
    processed = []
    for booking in bookings:
        original_currency = booking['price']['finalRetailPrice']['currency']
        original_currency_price = booking['price']['finalRetailPrice']['amount']
        requested_currency_price = cv.convert(original_currency_price, original_currency, requested_currency)

        res = {
            'bookingCode': booking['bookingCode'],
            'experienceName': booking['experience']['name'],
            'rateName': booking['rateName'],
            'bookingTime': booking['bookingCreated'],
            'participants': sum(rate['quantity'] for rate in booking['ratesQuantity']), # since 'participants' field is mostly null
            'originalCurrency': original_currency,
            'priceOriginalCurrency': original_currency_price,
            'requestedCurrency': requested_currency,
            'priceRequestedCurrency': requested_currency_price,
        }

        processed.append(res)

    return processed


@shared_task
def sum_bookings(bookings_lists):
    bookings_list = [booking for bookings in bookings_lists for booking in bookings]
    final_res = {'bookings': [booking for booking in bookings_list]}
    final_res['totalPriceOriginalCurrency'] = sum(booking['priceOriginalCurrency'] for booking in bookings_list)
    final_res['totalPriceRequestedCurrency'] = sum(booking['priceRequestedCurrency'] for booking in bookings_list)

    return final_res
