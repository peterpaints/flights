#!/usr/bin/env sh

set -e

. bin/wait_for_it.sh ;

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
