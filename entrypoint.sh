#!/bin/bash

echo ">>> Migrating database"
python manage.py migrate

echo ">>> Starting local server"
python manage.py runserver 0.0.0.0:8000
