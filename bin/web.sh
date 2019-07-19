#!/bin/sh

if [ "$FLASK_ENV" == "development" ]; then
        flask run
else
        gunicorn --bind 0.0.0.0:$PORT wsgi
fi
