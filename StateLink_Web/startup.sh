#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn StateLink_Web.wsgi:application --bind=0.0.0.0:8000 