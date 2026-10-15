"""Jede schreibende Schnittstelle der aktiven Module prüft mehr als nur den Login.

Qualität II (Schritt 1b-2) fand viele Schnittstellen, die Ändern oder Löschen
erlaubten, aber nur prüften, ob jemand eingeloggt ist. Dieser Test geht alle
Adressen durch und meldet jede neue Schnittstelle dieser Art. Ist die Prüfung
an anderer Stelle umgesetzt (z. B. in perform_update), kommt die Klasse mit
Begründung in die Liste unten.
"""
import inspect

from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

# Eingefrorene Module werden nicht weiterentwickelt (docs/entscheidungen.md).
# food und inspi stehen bewusst nicht hier: Sie sind abgeschaltet. Schaltet sie
# jemand wieder ein, meldet dieser Test ihre offenen Schnittstellen sofort.
FROZEN_APPS = ('messaging.', 'notifications.')

WRITE_ACTIONS = {'create', 'update', 'partial_update', 'destroy'}

# Klasse -> wo das Recht stattdessen geprüft wird
CHECKED_ELSEWHERE = {
    'AttributeModuleViewSet': 'perform_create/update/destroy: Leitung der Veranstaltung, Vorlagen nur Staff',
    'BooleanAttributeViewSet': 'AttributeAnswerUpdateViewSet.perform_update: Recht auf die Anmeldung und Änderungsfrist',
    'IntegerAttributeViewSet': 'wie BooleanAttributeViewSet',
    'FloatAttributeViewSet': 'wie BooleanAttributeViewSet',
    'StringAttributeViewSet': 'wie BooleanAttributeViewSet',
    'TravelAttributeViewSet': 'wie BooleanAttributeViewSet',
    'DateTimeAttributeViewSet': 'wie BooleanAttributeViewSet',
    'MailReminderViewSet': 'create: Leitung der Veranstaltung aus der Anfrage',
    'MailSingleReminderViewSet': 'create: Leitung der Veranstaltung der Anmeldung',
    'EventLocationViewSet': 'update/perform_destroy: Leitung aller Veranstaltungen am Ort; Anlegen für alle nötig',
    'MarkAsReadViewSet': 'nur eigene Benachrichtigungen (get_queryset)',
    'MarkAsUnreadViewSet': 'nur eigene Benachrichtigungen (get_queryset)',
    'DeleteViewSet': 'nur eigene Benachrichtigungen (get_queryset)',
    'EmailSettingsViewSet': 'nur die eigenen Einstellungen',
    'MyOwnRequestGroupAccessViewSet': 'nur eigene Beitrittsanfragen (get_queryset)',
    'MyMembersViewSet': 'nur selbst angelegte Personen, Stamm nur mit Admin-Recht (get_queryset)',
    'RequestGroupAccessViewSet': 'get_permissions: IsGroupAdmin außer beim Anfragen',
    'LeaveGroupViewSet': 'nur selbst austreten',
    'MyMembersUploadViewSet': 'legt nur Personen an, die der Person selbst zugeordnet sind (created_by)',
    'AllGroupsViewSet': 'create: Admin-Recht auf die Obergruppe; Ändern und Löschen: tests/test_gruppenrechte.py',
}


def iter_views(patterns, prefix=''):
    """Alle Adressen mit ihrer View, auch aus eingebundenen URL-Listen."""
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            yield from iter_views(pattern.url_patterns, prefix + str(pattern.pattern))
        elif isinstance(pattern, URLPattern) and getattr(pattern.callback, 'cls', None):
            yield prefix + str(pattern.pattern), pattern.callback


def only_login_checked(view_cls) -> bool:
    """Prüft die Klasse nur, ob jemand eingeloggt ist?"""
    permissions = list(getattr(view_cls, 'permission_classes', api_settings.DEFAULT_PERMISSION_CLASSES))
    # Kombinierte Prüfungen (A | B) sind keine Klassen und keine reinen Login-Prüfungen.
    if not all(inspect.isclass(permission) for permission in permissions):
        return False
    return set(permissions) == {IsAuthenticated}


def test_schreibende_schnittstellen_pruefen_mehr_als_login():
    unchecked = set()
    for route, callback in iter_views(get_resolver().url_patterns):
        view_cls = callback.cls
        if view_cls.__module__.startswith(FROZEN_APPS):
            continue
        actions = set((getattr(callback, 'actions', None) or {}).values())
        if actions & WRITE_ACTIONS and only_login_checked(view_cls) and view_cls.__name__ not in CHECKED_ELSEWHERE:
            unchecked.add(f'{view_cls.__module__}.{view_cls.__name__} ({route})')
    assert not unchecked, 'Schreibende Schnittstellen nur mit Login-Prüfung:\n' + '\n'.join(sorted(unchecked))
