import os
from django.apps import AppConfig
from django.core.cache import cache

class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'
    
    def ready(self) -> None:
        if os.environ.get('RUN_MAIN'):
            try:
                magazines = [
                    {'title': 'Django Demystified', 'description': 'Go beyond the standard Django features and learn features only experienced pros know.'},
                    {'title': 'Microservices Magic', 'description': 'Take yourself to the next level as a developer and master microservices.'},
                    {'title': 'Python to Perfection', 'description': 'Squeeze every last last bit out of Python with the very latest Python features, tips and tricks.'}
                ]
                # from .models import Magazine
                # magazines = Magazine.objects.all()
                # cache.set('magazines', magazines)
                cache.set('magazines', magazines, timeout=None)  # Cache indefinitely
                logger.info(f'Magazines added to Django cache: {magazines}')
            except Exception as e:
                logger.error(f'Failed to cache magazines: {str(e)}')
            #print('Magazines added to Django cache')
        
    # def ready(self):
    #     # Setup certificate when Django starts
    #     try:
    #         from subscription_registration.mongodb_setup import mongodb_cert_manager
    #         mongodb_cert_manager.setup_certificate()
    #     except Exception as e:
    #         print(f"Warning: Failed to setup MongoDB certificate: {e}")
    
    # def __del__(self):
    #     # Cleanup on shutdown
    #     try:
    #         from subscription_registration.mongodb_setup import mongodb_cert_manager
    #         mongodb_cert_manager.cleanup_certificate()
    #     except:
    #         pass