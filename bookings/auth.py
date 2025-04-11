from rest_framework import authentication
from rest_framework import exceptions

from django.conf import settings


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Case-insensitive header lookup
        api_key = None
        for header, value in request.headers.items():
            if header.lower() == 'x-api-key':
                api_key = value
                break
        
        if not api_key:
            raise exceptions.AuthenticationFailed('No API key provided')
            
        if api_key != getattr(settings, 'EXTERNAL_API_KEY', None):
            raise exceptions.AuthenticationFailed('Invalid API key')
            
        return (None, None)
