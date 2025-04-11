from currency_converter import CurrencyConverter, RateNotFoundError
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Request:
    requested_currency: str
    coefficient: Decimal
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    @classmethod
    def from_params(cls, params: Dict[str, str]) -> 'Request':
        if 'currency' not in params:
            raise ValueError("Currency parameter is required")
        if not isinstance(params['currency'], str):
            raise ValueError("Currency must be a string")
        requested_currency = params['currency'].upper()
        
        try:
            coefficient = cls._get_currency_coefficient(requested_currency)
        except ValueError as e:
            raise ValueError(str(e))
        
        try:
            start_time = cls._parse_datetime(params.get('date[gt]'))
            end_time = cls._parse_datetime(params.get('date[lt]'))
        except ValueError as e:
            raise ValueError(str(e))
        if start_time and end_time and start_time > end_time:
            raise ValueError("Start time must be before end time")
            
        return cls(
            requested_currency=requested_currency,
            coefficient=coefficient,
            start_time=start_time,
            end_time=end_time
        )
    
    @staticmethod
    def _get_currency_coefficient(currency: str) -> Decimal:
        try:
            c = CurrencyConverter()
            rate = c.convert(1, "EUR", currency)
            return Decimal(str(rate)).quantize(Decimal('0.0001'))
        except RateNotFoundError:
            raise ValueError(f"Invalid currency: {currency}")
    
    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")
