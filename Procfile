release: python manage.py sync_roles & python manage.py migrate --noinput
web: newrelic-admin run-program gunicorn pythonpro.wsgi --log-file -
