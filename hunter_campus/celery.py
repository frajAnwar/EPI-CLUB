import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunter_campus.settings')
app = Celery('hunter_campus')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
