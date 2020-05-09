#!/bin/sh

export APP_ENV=product
echo The APP_ENV is $APP_ENV

echo 'Starting gunicorn...'
exec gunicorn --workers 1 \
--bind 0.0.0.0:5003 \
--log-level DEBUG \
--timeout 90 \
manager:app
