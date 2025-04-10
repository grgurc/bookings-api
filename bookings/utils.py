import re
import math

from django.conf import settings

external_api_key = settings.EXTERNAL_API_KEY
external_api_url = settings.EXTERNAL_API_URL

def authenticate(request):
    api_key = request.headers['x-api-key']
    if not api_key == external_api_key:
        raise Exception


# generate param dicts for all request pages
def generate_params(base_params, first_response):
    count = first_response['count']
    page_size = len(first_response['results'])
    if page_size == 0:
        return []
    
    num_pages = math.ceil(count / page_size)

    page_params = []
    for i in range(1, num_pages+1):
        new_params = base_params.copy()
        new_params['page'] = i
        page_params.append(new_params)
    
    return page_params
