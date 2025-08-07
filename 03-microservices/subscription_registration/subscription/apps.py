from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'
    
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