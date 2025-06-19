#!/bin/sh
set -e

# Миграции
python manage.py migrate --noinput

# Сборка статики
python manage.py collectstatic --noinput

# Запускаем gunicorn
exec "$@"