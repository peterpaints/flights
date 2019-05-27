#!/usr/bin/env sh

set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

echo "PostgreSQL started"

cd api

if [ ! -d migrations ] ; then
  flask db init
  flask db migrate
  flask db upgrade

  python models/seed.py
else
  flask db migrate
  flask db upgrade
fi

gunicorn -w 1 -b 0.0.0.0:8000 --timeout 350 unicorn:app
exec $@
