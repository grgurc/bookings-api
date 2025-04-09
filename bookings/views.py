import logging
import math
import requests

import bookings.tasks as tasks
import bookings.utils as utils

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from celery import chain, chord, group
from django.conf import settings
from requests import RequestException

logger = logging.getLogger(__name__)

external_api_key = settings.EXTERNAL_API_KEY
external_api_url = settings.EXTERNAL_API_URL

# TODO: cache responses
@api_view(['GET'])
def fetch(request):
    requested_currency = request.query_params.get('currency')
    if not requested_currency:
        return Response({'error': 'error parsing currency param'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        api_key = utils.authenticate(request)
    except utils.AuthException:
        return Response({'error': 'api key error'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        date_param_dict = utils.parse_date_param(request)
    except utils.NoDateParamException:
        return Response({'error': 'error parsing date param'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        res = requests.get(
            url = external_api_url,
            params = date_param_dict,
            headers = {'x-api-key': external_api_key},
        )
        res.raise_for_status()
    except RequestException:
        return Response({'error': 'external api error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    next_params = utils.get_next_params(date_param_dict, res)

    # TODO: oof this ugly
    task_group = group([chain(tasks.fetch_bookings.s(external_api_url, params, api_key) | tasks.process_bookings.s(requested_currency=requested_currency)) for params in next_params])

    final_res = chord(task_group, tasks.sum_bookings.s())().get()

    return Response(final_res)
