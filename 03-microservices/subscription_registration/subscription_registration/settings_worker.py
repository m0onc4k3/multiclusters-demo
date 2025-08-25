import os
# In settings_worker.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Prints emails to console
CELERY_BROKER_URL = f'redis://{os.environ.get("REDIS_HOST", "my-redis")}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{os.environ.get("REDIS_HOST", "my-redis")}:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'': {'handlers': ['console'], 'level': 'DEBUG'}},
}

REDIS_HOST= 'my-redis'