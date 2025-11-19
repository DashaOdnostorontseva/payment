#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "Apply migrations..."
python manage.py migrate --noinput

echo "Load initial data (if exists)..."
python manage.py loaddata payment/fixtures/initial_data.json || true

echo "Create superuser (if not exists)..."
python manage.py createsuperuser --noinput || true

echo "Collect static files..."
python manage.py collectstatic --noinput

echo "Start gunicorn..."
gunicorn root.wsgi:application
