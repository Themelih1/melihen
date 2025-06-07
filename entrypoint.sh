#!/bin/sh

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn mywebsite.wsgi:application --bind 0.0.0.0:8000
