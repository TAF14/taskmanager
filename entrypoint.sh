#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import psycopg2, os
url = os.environ.get('DATABASE_URL')
if url:
    psycopg2.connect(url)
else:
    psycopg2.connect(host=os.environ['DB_HOST'],port=os.environ.get('DB_PORT','5432'),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],dbname=os.environ['DB_NAME'])
" 2>/dev/null; do
    sleep 1
done

echo "PostgreSQL is ready."

python -u manage.py migrate --no-input
python -u manage.py create_superuser_if_none
python -u manage.py collectstatic --no-input --clear

exec gunicorn todoproject.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
