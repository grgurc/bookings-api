## Requirements
1. python
2. redis-server

## How to run
1. Install python packages: `pip install -r requirements.txt`
2. Django migrate `python manage.py migrate`
3. Rename `.env.example` to `.env` and update `EXTERNAL_API_KEY` and `EXTERNAL_API_URL` to appropriate values
4. Run server `python manage.py runserver`
6. Good to go

## Request example (replace API key)
`curl -X GET "localhost:8000/bookings/?date\[gt\]=2024-04-08&currency=USD" -H "x-api-key: api-key-letters-and-numbers"`

## TODO
- caching
- rate limiting
- dockerize for 'production'
