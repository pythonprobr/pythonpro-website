release: python manage.py sync_roles & python manage.py migrate --noinput
web: newrelic-admin run-program gunicorn pythonpro.wsgi --log-file -
worker: newrelic-admin run-program celery -A pythonpro.celery worker --loglevel=info
