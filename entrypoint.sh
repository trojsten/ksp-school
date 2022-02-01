#!/bin/bash

echo ">>> Generating code highlighting CSS"
pygmentize -S monokai -f html -a .codehilite > /app/school/static/code.css

echo ">>> Waiting for database"
WAIT_start=$(date +%s)
while :
do
    (echo -n > /dev/tcp/db/5432) >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        WAIT_end=$(date +%s)
        echo "    Database UP after $((WAIT_end - WAIT_start)) seconds"
        break
    fi
    sleep 1
done

echo ">>> Migrating database"
python manage.py migrate --force-color


if [ ! -z "$USE_GUNICORN" ]; then
  echo ">>> Collect static"
  python manage.py collectstatic --no-input

  echo ">>> Starting Gunicorn"
  python -m gunicorn --workers 4 --bind 0.0.0.0:8000 school.wsgi
else
  echo ">>> Starting local server"
  python manage.py runserver 0.0.0.0:8000 --force-color
fi
