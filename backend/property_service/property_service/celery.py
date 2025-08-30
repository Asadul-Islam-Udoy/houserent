import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_service.settings')
app = Celery('property_service')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
