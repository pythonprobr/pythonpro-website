release: python manage.py sync_roles & python manage.py migrate --noinput
web: gunicorn pythonpro.wsgi --log-file -
worker: celery --app pythonpro.celery worker --loglevel=info
