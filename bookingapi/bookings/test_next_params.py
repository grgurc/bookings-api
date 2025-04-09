from unittest.mock import Mock
from django.test import TestCase
from .utils import get_next_params


class GetNextParamsTests(TestCase):
    
    def setUp(self):
        # Any setup needed for the tests (optional)
        self.base_params = {'param1': 'value1', 'param2': 'value2'}

    def test_get_next_params_single_page(self):
        # Mock response for a single page of results
        first_response = Mock()
        first_response.json.return_value = {'count': 10, 'results': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        
        # Page size is the length of results (10 in this case), so there's only one page
        result = get_next_params(self.base_params, first_response)
        
        # No additional pages should be generated
        self.assertEqual(result, [])

    def test_get_next_params_multiple_pages(self):
        # Mock response for multiple pages
        first_response = Mock()
        first_response.json.return_value = {'count': 25, 'results': [1, 2, 3, 4, 5]}
        
        # Page size is 5 (length of results), so there should be 5 pages
        result = get_next_params(self.base_params, first_response)
        
        # Expecting pages 2 to 5
        expected_params = [
            {'param1': 'value1', 'param2': 'value2', 'page': 2},
            {'param1': 'value1', 'param2': 'value2', 'page': 3},
            {'param1': 'value1', 'param2': 'value2', 'page': 4},
            {'param1': 'value1', 'param2': 'value2', 'page': 5}
        ]
        
        self.assertEqual(result, expected_params)

    def test_get_next_params_no_results(self):
        # Mock response for no results
        first_response = Mock()
        first_response.json.return_value = {'count': 0, 'results': []}
        
        # No pages should be created if there are no results
        result = get_next_params(self.base_params, first_response)
        
        self.assertEqual(result, [])

    def test_get_next_params_exact_page_size(self):
        # Mock response for exact page size (no extra pages needed)
        first_response = Mock()
        first_response.json.return_value = {'count': 20, 'results': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}
        
        # Page size is 20, so there should only be 1 page
        result = get_next_params(self.base_params, first_response)
        
        self.assertEqual(result, [])

    def test_get_next_params_last_page(self):
        # Mock response with the last page not completely full
        first_response = Mock()
        first_response.json.return_value = {'count': 32, 'results': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]}
        
        # Page size is 10, so we should have 4 pages
        result = get_next_params(self.base_params, first_response)
        
        # Expecting pages 2 to 4
        expected_params = [
            {'param1': 'value1', 'param2': 'value2', 'page': 2},
            {'param1': 'value1', 'param2': 'value2', 'page': 3},
            {'param1': 'value1', 'param2': 'value2', 'page': 4}
        ]
        
        self.assertEqual(result, expected_params)
