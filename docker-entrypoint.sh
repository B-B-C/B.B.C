#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $POSTGRES_HOST ${POSTGRES_PORT:-5432}; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Create logs directory
mkdir -p /app/logs

# Execute the command passed to the container
exec "$@"



