from django.core.management.base import BaseCommand

from basic.helper.initialize_keycloak_scout_hierarchies import grant_hierarchy_permissions


class Command(BaseCommand):
    help = (
        'Vergibt Standard-Gruppenrechte für vorhandene Gruppen: Führungsgruppen '
        'verwalten ihre Obergruppe, Stammesmitglieder sehen ihren Stamm. '
        'Spricht nicht mit Keycloak und kann mehrfach laufen.'
    )

    def handle(self, *args, **options):
        granted = grant_hierarchy_permissions()
        self.stdout.write(self.style.SUCCESS(f'{granted} Gruppenrechte neu vergeben'))
