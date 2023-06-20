#!/bin/bash
set -euo pipefail

pygmentize -S monokai -f html -a .codehilite > /app/school/static/code.css

python manage.py wait_for_database
python manage.py migrate --force-color

if [ "${1:-prod}" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000 --force-color
else
  python manage.py collectstatic --no-input
  exec gunicorn --bind 0.0.0.0:8000 --access-logfile - --log-file - school.wsgi
fi
