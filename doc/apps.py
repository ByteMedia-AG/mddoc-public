from django.apps import AppConfig


class DocConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doc'

    def ready(self):
        import doc.signals
