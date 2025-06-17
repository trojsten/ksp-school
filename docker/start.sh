#!/bin/bash
set -euo pipefail

python manage.py wait_for_database
python manage.py migrate --force-color

if [ "${1:-prod}" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000 --force-color
else
  exec /base/gunicorn.sh school.wsgi
fi
