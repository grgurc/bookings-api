from django.test import TestCase
from django.http import QueryDict
from .utils import parse_date_param, DateParamException

class ParseDateParamTests(TestCase):
    
    def setUp(self):
        # Setup any common resources here (if needed)
        self.mods = ['eq', 'lt', 'lte', 'gt', 'gte']  # Updated modifiers
    
    def mock_request(self, params):
        """
        Helper method to create a mock request with query params.
        """
        request = type('Request', (object,), {'query_params': QueryDict(params)})
        return request

    def test_parse_date_param_valid(self):
        # Test with valid input
        request = self.mock_request('date[eq]=2025-04-09')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[eq]': '2025-04-09'})

        # Test with another valid modifier
        request = self.mock_request('date[lt]=2025-04-10')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[lt]': '2025-04-10'})

        # Test with another valid modifier
        request = self.mock_request('date[lte]=2025-04-11')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[lte]': '2025-04-11'})

        # Test with another valid modifier
        request = self.mock_request('date[gt]=2025-04-12')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[gt]': '2025-04-12'})

        # Test with another valid modifier
        request = self.mock_request('date[gte]=2025-04-13')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[gte]': '2025-04-13'})

    def test_parse_date_param_invalid_modifier(self):
        # Test with an invalid modifier (not in your mods)
        request = self.mock_request('date[invalid]=2025-04-09')
        with self.assertRaises(DateParamException):
            parse_date_param(request)

    def test_parse_date_param_missing_modifier(self):
        # Test with a missing or empty modifier
        request = self.mock_request('date[]=')
        with self.assertRaises(DateParamException):
            parse_date_param(request)

    def test_parse_date_param_no_date_param(self):
        # Test with no date parameter at all
        request = self.mock_request('other_param=value')
        with self.assertRaises(DateParamException):
            parse_date_param(request)

    def test_parse_date_param_multiple_parameters(self):
        # Test with multiple parameters (check if it returns the first match)
        request = self.mock_request('date[eq]=2025-04-09&date[lt]=2025-04-10')
        result = parse_date_param(request)
        self.assertEqual(result, {'bookingCreated[eq]': '2025-04-09'})
