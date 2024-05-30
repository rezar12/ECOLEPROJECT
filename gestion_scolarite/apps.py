from django.apps import AppConfig


class GestionScolariteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_scolarite'
    verbose_name = 'Gestion de la Scolarité'
    icon = 'fa fa-university'
    def ready(self):
        import gestion_scolarite.signals
