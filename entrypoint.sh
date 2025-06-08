#!/bin/sh
set -eux

mkdir -p logs

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading admin user data..."
python manage.py loaddata auth_data.json || true  # dosya yüklüyse hata vermez, devam eder

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn mywebsite.wsgi:application --bind 0.0.0.0:8000
