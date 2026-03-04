#!/bin/sh
set -e

python manage.py migrate --noinput
if [ "${AUTO_SEED:-true}" = "true" ]; then
  python manage.py seed_demo_data
fi
python manage.py runserver 0.0.0.0:8000 --noreload
