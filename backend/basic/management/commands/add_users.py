from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

# Bewusst fest und öffentlich bekannt: nur für die lokale Entwicklung.
DEV_ADMIN_PASSWORD = 'admin1234'  # noqa: S105 -- nur lokal, im Echtbetrieb verweigert (Test: test_verwaltungsbefehle.py)


class Command(BaseCommand):
    """Legt für die lokale Entwicklung das Konto "admin" mit festem Passwort an.

    Läuft nur mit DEBUG=True. Im Echtbetrieb wäre ein Konto mit bekanntem
    Passwort ein offener Zugang zur Verwaltung unter /admin/. Dort legt man
    Administratoren mit "python manage.py createsuperuser" an.
    """

    help = 'Legt lokal das Konto admin an (nur mit DEBUG=True)'

    def handle(self, *args, **options):
        """Bricht ohne DEBUG=True ab, sonst legt es das Konto an, falls es noch fehlt."""
        if not settings.DEBUG:
            raise CommandError(
                'add_users ist nur für die lokale Entwicklung (DEBUG=True). '
                'Im Echtbetrieb stattdessen "python manage.py createsuperuser" verwenden.'
            )
        user_model = get_user_model()
        if not user_model.objects.filter(username='admin').exists():
            user_model.objects.create_superuser('admin', password=DEV_ADMIN_PASSWORD)
        self.stdout.write('Konto admin angelegt.')
