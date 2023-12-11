#!/bin/sh

# Create directory paths
echo "Create directories..."

satellites="sentinel-1a sentinel-2b"
directories="extracted images archive"

# Create directories
for satellite in $satellites; do
  for directory in $directories; do
    mkdir -p "/dews/media/sat_data/$directory/$satellite"
  done
done

mkdir -p "/dews/media/other"


# Create empty log
echo "Create empty Django log file..."
touch /app/dews/django.log

# Django database migration
echo "Make migrations..."
python manage.py makemigrations --noinput

echo "Migrate..."
python manage.py migrate --noinput

echo "Colect static..."
python manage.py collectstatic --noinput

# Create default super user
echo "Create default super user..."
python manage.py createsuperuser --noinput

# Start
echo "Start main app..."
gunicorn dews.wsgi:application --bind 0.0.0.0:8000 --reload
