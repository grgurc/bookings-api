## Requirements

1. python (tested on 3.12)
2. redis-server / redis

## How to run

1. Run redis-server / redis (locally or in docker container with exposed default port)
2. Install python packages: `pip install -r requirements.txt`
3. Django migrate `python manage.py migrate`
4. Rename `.env.example` to `.env` and update `EXTERNAL_API_KEY` and `EXTERNAL_API_URL` to appropriate values
5. Run initial bookings sync `python manage.py sync_bookings`
6. Run server `python manage.py runserver`
7. Run Celery worker `celery -A bookingapi worker -l info`
8. Run Celery beat for scheduled tasks `celery -A bookingapi beat -l info`
9. Good to go

## Request example (replace API key)

`curl -X GET "localhost:8000/bookings/?date\[gt\]=2024-04-08&currency=USD" -H "x-api-key: api-key-letters-and-numbers"`
- the API only supports dates with `[gt]` and `[lt]` modifiers, not exact dates

## Further Improvements

- API rate limiting
- dockerize for 'production'
