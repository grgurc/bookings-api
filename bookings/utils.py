import re
import math

from django.conf import settings

external_api_key = settings.EXTERNAL_API_KEY
external_api_url = settings.EXTERNAL_API_URL

mods = ['eq', 'lt', 'lte', 'gt', 'gte']

class DateParamException(Exception):
    pass

class AuthException(Exception):
    pass

# return date param transformed for Turneo api
def parse_date_param(request):
    for k in request.query_params:
        match = re.search(r'date\[(.*?)\]', k)
        if not match:
            continue
        
        mod = match.group(1)
        if mod and mod in mods:
            # just replace date with bookingAdded
            return {
                f'bookingCreated[{mod}]': request.query_params[k]
            }
    # wrong format or wrong / missing modifier
    raise DateParamException

def authenticate(request):
    api_key = request.headers['x-api-key']
    if not api_key == external_api_key:
        raise AuthException
    
    return api_key

def get_next_params(base_params, first_response):
    res_json = first_response.json()

    count = res_json['count']
    page_size = len(res_json['results'])
    if page_size == 0:
        return []
    
    num_pages = math.ceil(count / page_size)

    page_params = []
    for i in range(2, num_pages+1):
        new_params = base_params.copy()
        new_params['page'] = i
        page_params.append(new_params)
    
    return page_params

# prepare params with page numbers for each page
def get_params_list(original_params, resJson):
    count = resJson['count']
    page_size = len(resJson['results'])
    num_pages = math.ceil(count / page_size)

    params_list = []
    for i in range(2, num_pages):
        params = original_params.copy()
        params['page'] = i
        params_list.append(params)

    return params_list