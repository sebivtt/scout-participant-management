"""Signal-Empfänger und geplante Hintergrundaufgaben müssen beim Start registriert sein.

Sie werden in apps.py nur importiert, nicht benutzt. Automatische Aufräum-
werkzeuge halten solche Importe für überflüssig und entfernen sie. Dann
fallen z. B. die Synchronisation mit Keycloak oder Benachrichtigungen still
weg, ohne dass ein Fehler auftritt. (Passiert am 15.10.2026 beim Einführen
von ruff.)
"""
import pytest
from django.conf import settings
from django.db.models.signals import post_delete, post_save

from authentication.models import RequestGroupAccess
from backend import celery_app
from keycloak_auth.models import KeycloakGroup
from messaging.models import Issue
from notifications.models import Notification


def receiver_modules(signal, sender) -> set[str]:
    sync_receivers, async_receivers = signal._live_receivers(sender)
    return {receiver.__module__ for receiver in [*sync_receivers, *async_receivers]}


@pytest.mark.parametrize('signal,sender,module', [
    (post_save, KeycloakGroup, 'keycloak_auth.signals'),
    (post_delete, KeycloakGroup, 'keycloak_auth.signals'),
    (post_save, RequestGroupAccess, 'authentication.signals'),
    (post_save, Issue, 'messaging.signals'),
    (post_save, Notification, 'authentication.custom_notifications.signals'),
])
def test_signal_registriert(signal, sender, module):
    assert module in receiver_modules(signal, sender)


@pytest.mark.parametrize('schedule_name', sorted(settings.CELERY_BEAT_SCHEDULE))
def test_geplante_aufgabe_registriert(schedule_name):
    """Jede geplante Aufgabe (z. B. der Keycloak-Abgleich alle 15 Minuten) ist bei Celery bekannt.

    Celery findet von sich aus nur Aufgaben in Dateien namens tasks.py. Der
    Keycloak-Abgleich liegt woanders und wird nur durch einen Import in
    authentication/apps.py bekannt gemacht. Fehlt der Import, verwirft Celery
    den Zeitplan-Eintrag bei jedem Lauf, und der Abgleich findet nie statt.
    """
    # Wie beim Start eines Celery-Workers: erst die übliche Suche nach tasks.py.
    celery_app.loader.import_default_modules()
    task_name = settings.CELERY_BEAT_SCHEDULE[schedule_name]['task']
    assert task_name in celery_app.tasks
