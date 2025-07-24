from django.apps import AppConfig

class DjangoblogAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangoblog'

    def ready(self):
        super().ready()
        # Import and load plugins here
        from .plugin_manage.loader import load_plugins
        load_plugins() 