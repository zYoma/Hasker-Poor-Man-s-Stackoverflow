from django.apps import AppConfig


class HaskerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hasker'

    def ready(self):
        import hasker.signals
