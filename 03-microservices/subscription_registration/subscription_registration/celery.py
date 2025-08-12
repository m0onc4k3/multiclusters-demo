import os
from celery import Celery

# gives Celery access to its settings via the CELERY namespace in the Django settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subscription_registration.settings")

# creates the app
app = Celery("subscription_registration")

# gives Celery access to its settings via the CELERY namespace in the Django settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# make the app discover our shared tasks
app.autodiscover_tasks()