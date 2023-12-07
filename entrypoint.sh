#!/bin/sh

# Create directory paths
echo "Create directories..."

satellites="sentinel-1a sentinel-2b"
directories="extracted images zip"

# Create directories
for satellite in $satellites; do
  for directory in $directories; do
    mkdir -p "/dews/media/sat_data/$directory/$satellite"
  done
done

for satellite in $satellites; do
    mkdir -p "/dews/media/other/meta_data/$satellite"
done

# Django database migration
echo "Make migrations..."
python manage.py makemigrations --noinput

echo "Migrate..."
python manage.py migrate --noinput

echo "Colect static..."
python manage.py collectstatic --noinput

# Create default admin user
echo "Create default admin user..."
python manage.py createadmin dews dews dews@dews.de

# Start
echo "Start main app..."
gunicorn dews.wsgi:application --bind 0.0.0.0:8000
