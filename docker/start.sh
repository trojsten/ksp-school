#!/bin/bash
set -euo pipefail

python manage.py migrate
exec gunicorn school.wsgi --bind 127.0.0.1:8001 --workers 4 --max-requests 1000