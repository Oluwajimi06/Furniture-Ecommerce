from django.apps import AppConfig

class SitepagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sitepages'



    def ready(self):
        import sitepages.signals  # Import the signals module

    
