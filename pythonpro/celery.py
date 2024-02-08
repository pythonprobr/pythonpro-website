import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonpro.settings')
app = Celery('pythonpro.celery')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()
