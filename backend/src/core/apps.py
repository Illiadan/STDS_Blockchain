from django.apps import AppConfig
from django.core.management import call_command


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        call_command('migrate',
                     app_label='core',
                     verbosity=1,
                     interactive=False,
                     database='memory')

