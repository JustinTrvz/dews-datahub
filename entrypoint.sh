#!/bin/sh

PG_HOST="dews-db"
PG_PORT="5432"
PG_DB="dews"
PG_USER="dews"
PG_PW="dews"
# Wait for PostgreSQL to become available
echo "Waiting for PostgreSQL to become available..."
while ! PGPASSWORD="$PG_PW" psql -h "$PG_HOST" -U "$PG_USER" -p "$PG_PORT" -d "$PG_DB" -c 'SELECT 1' > /dev/null 2>&1
do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

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
gunicorn dews.wsgi:application --bind 0.0.0.0:8000  -k gevent --workers 3 --reload --timeout 120
