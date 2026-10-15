from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        import authentication.signals  # noqa: F401 -- registriert die Signal-Empfänger
        from authentication.sync_keycloak_users import import_keycloak_members  # noqa: F401 -- meldet den Keycloak-Abgleich bei Celery an
