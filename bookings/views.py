import logging
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any

from bookings.auth import APIKeyAuthentication
from bookings.request import Request
from bookings.models import Booking

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([APIKeyAuthentication])
def fetch(request):
    logger.info(f"Request: {request.query_params}")
    
    try:
        req = Request.from_params(request.query_params)
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An unexpected error occurred while processing your request'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        bookings = get_filtered_bookings(req)
        converted_bookings = [convert_booking(booking, req) for booking in bookings]
        return Response(sum_bookings(converted_bookings))
    except Exception as e:
        logger.error(f"Error processing bookings: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An error occurred while processing the bookings'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_filtered_bookings(req: Request) -> List[Booking]:
    query = Booking.objects.all()
    if req.start_time:
        query = query.filter(booking_created__gte=req.start_time)
    if req.end_time:
        query = query.filter(booking_created__lte=req.end_time)
    return list(query)


def convert_booking(booking: Booking, req: Request) -> Dict[str, Any]:
    try:
        price_converted = (booking.price_original_currency * req.coefficient).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError) as e:
        logger.error(f"Error converting booking {booking.code}: {str(e)}")
        raise ValueError(f"Invalid currency conversion: {str(e)}")
        
    return {
        'code': booking.code,
        'experience': booking.experience,
        'rate': booking.rate,
        'bookingCreated': booking.booking_created,
        'participants': booking.participants,
        'originalCurrency': booking.original_currency,
        'priceOriginalCurrency': booking.price_original_currency,
        'requestedCurrency': req.requested_currency,
        'priceRequestedCurrency': price_converted
    }


def sum_bookings(bookings_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_original = sum(b['priceOriginalCurrency'] for b in bookings_list)
    total_converted = sum(b['priceRequestedCurrency'] for b in bookings_list)
    
    return {
        'bookings': bookings_list,
        'totalPriceOriginalCurrency': total_original.quantize(Decimal('0.01')),
        'totalPriceRequestedCurrency': total_converted.quantize(Decimal('0.01'))
    }
