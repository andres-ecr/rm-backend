#!/bin/bash
set -e

echo "🚀 Starting application..."

# Run migrations and collect static files
echo "📦 Running pre-startup tasks..."
python check_db_and_migrate.py

# Start Gunicorn
echo "✅ Starting Gunicorn..."
exec gunicorn route_monitor.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

