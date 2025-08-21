import os
from celery import Celery

# gives Celery access to its settings via the CELERY namespace in the Django settings.py
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", 
    "subscription_registration.settings_worker"
    )

# creates the app
app = Celery("subscription_registration")

# gives Celery access to its settings via the CELERY namespace in the Django settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# explicitily discover tasks in the 'subscription' app
# otherwise INSTALLED_APPS is typically used by autodiscover_tasks() to find tasks
app.autodiscover_tasks(['subscription'])