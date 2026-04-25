#!/bin/sh
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Loading sample data..."
python manage.py seed_data

echo "==> Starting server at http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000
