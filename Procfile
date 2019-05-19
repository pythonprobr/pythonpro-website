release: python manage.py sync_roles
release: python manage.py migrate --noinput
web: gunicorn pythonpro.wsgi --log-file -
