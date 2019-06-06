#!/usr/bin/env sh

set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

echo "PostgreSQL started"
exec $@
