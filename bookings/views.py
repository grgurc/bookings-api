import logging
import json

import bookings.tasks as tasks
import bookings.utils as utils

from bookings.request import Request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


logger = logging.getLogger(__name__)

@api_view(['GET'])
def fetch(request):
    try:
        utils.authenticate(request)
    except Exception:
        return Response({'error': 'api key error'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        req = Request(request.query_params)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    values = []
    cache_values = cache.get(req.cache_key())
    if cache_values:
        values = json.loads(cache_values)
    
    if values:
        if not req.open_ended():
            converted_responses = [tasks.convert_booking(booking, req.requested_currency, req.coefficient) for booking in values]
            return Response(tasks.sum_bookings(converted_responses))
        else:
            last_time = values[-1]['bookingCreated']
            req.start_time = datetime.fromisoformat(last_time) + timedelta(seconds=1)
    else:
        values = []

    params = req.default_query_params()

    try:
        res = tasks.fetch_bookings(params)
    except Exception:
        return Response({'error': 'external api error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    pages_params = utils.generate_params(params, res)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        responses = list(executor.map(tasks.fetch_bookings, pages_params))
        bookings_lists = list(executor.map(lambda response: response['results'], responses))
        flattened_bookings = [booking for booking_list in bookings_lists for booking in booking_list]
        parsed_responses = list(executor.map(tasks.parse_booking, flattened_bookings))

    values.extend(parsed_responses)
    cache.set(req.cache_key(), json.dumps(values), 5*60)

    converted_bookings = [tasks.convert_booking(booking, req.requested_currency, req.coefficient) for booking in values]

    return Response(tasks.sum_bookings(converted_bookings))
