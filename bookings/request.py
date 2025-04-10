from currency_converter import CurrencyConverter, RateNotFoundError
from datetime import datetime

class Request:
    def __init__(self, params):
        self.requested_currency = params['currency']
        try:
            # TODO: load from ECB currency file daily using cronjob or sth
            c = CurrencyConverter()
            self.coefficient = c.convert(1, "EUR", self.requested_currency)
        except RateNotFoundError:
            raise ValueError(f"Invalid currency: {self.requested_currency}")
        
        try:
            self.start_time = datetime.fromisoformat(params['date[gt]']) if 'date[gt]' in params else None
            self.end_time = datetime.fromisoformat(params['date[lt]']) if 'date[lt]' in params else None
        except Exception:
            raise ValueError(f"Invalid start or end time: {params['date[gt]']}, {params['date[lt]']}")
        # TODO: add support for exact date -> [eq]

    def cache_key(self):
        return f'{self.start_time}:{self.end_time}'

    def open_ended(self):
        return self.start_time and not self.end_time

    def default_query_params(self):
        p = {'sort': 'bookingCreated'}
        if self.start_time:
            p['bookingCreated[gt]'] = self.start_time
        if self.end_time:
            p['bookingCreated[lt]'] = self.end_time
        return p
