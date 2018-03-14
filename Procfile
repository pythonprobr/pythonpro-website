release: python manage.py migrate --noinput  --fake-initial
web: gunicorn pythonpro.wsgi --log-file -
