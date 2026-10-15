#!/bin/sh

set -o errexit
set -o nounset

echo "Apply database migrations"
python manage.py migrate
# Kein Konto mit festem Passwort beim Serverstart (siehe tests/test_verwaltungsbefehle.py).
# Administratoren einmalig mit "python manage.py createsuperuser" anlegen.
echo "Load main data"
#python manage.py loaddata data/main/*.json
echo "Load test data"
#python manage.py loaddata data/test/*.json
echo "Load food inspi data"
#python manage.py loaddata data/food-init/*.json

echo "Collect static data"
python manage.py collectstatic --noinput

echo "Start server"
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers=5 --threads=8
