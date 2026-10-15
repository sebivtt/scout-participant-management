"""Rechte auf Veranstaltungen und Anmeldungen.

Wer darf was (Entscheidung vom 14.10.2026, siehe docs/entscheidungen.md):
- Veranstaltungsleitung: in responsible_persons oder Mitglied der admin_group.
  Darf alles an der Veranstaltung und an allen ihren Anmeldungen.
- Ansicht: Mitglied der view_group. Darf Auswertungen sehen.
- Bundes-/Ringleitung: sieht Auswertungen für den eigenen Bund/Ring, wenn die
  Veranstaltung das erlaubt (view_allow_subgroup).
- Anmeldende Leitung: in Registration.responsible_persons. Darf die eigene
  Anmeldung sehen und ändern.

Fristen prüfen require_registration_open und require_changes_open, die Regeln
selbst stehen in anmelde_tool/event/deadlines.py.
"""

from enum import Enum

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request

from anmelde_tool.event.api_exceptions import RequiredGroupNotFound
from anmelde_tool.event.helper import get_event, get_registration, custom_get_or_404
from anmelde_tool.event.models import Event
from anmelde_tool.registration.models import Registration
from keycloak_auth.access import member_group_ids

CREATE_METHOD = 'POST'

User = get_user_model()




class LeadershipRole(str, Enum):
    """Einblick als Bundes- oder Ringführung in Auswertungen (Text wird so ans Frontend geliefert)."""
    NONE = "None",
    RING_LEADER = "Ringführung",
    BUND_LEADER = "Bundesführung",


class EventRole(str, Enum):
    """Recht auf eine Veranstaltung (Text wird als canEdit/canView ans Frontend geliefert)."""
    NONE = None,
    VIEW_ROLE = "View",
    ADMIN_ROLE = "Admin",


def get_keycloak_permission(user: User, keycloak_role: Group) -> bool:
    """Hat die Person die Rolle aus dem Login-Token (Django-Gruppe gleichen Namens)?"""
    return user.groups.filter(name=keycloak_role).exists()


def get_responsible_person_permission(user: User, event: Event) -> bool:
    """Ist die Person als Verantwortliche der Veranstaltung eingetragen?"""
    return event.responsible_persons.filter(id=user.id).exists() if event.responsible_persons else False


def check_event_permission(event_id: [str, Event], request, admin_only=False) -> EventRole:
    """Recht der Person auf die Veranstaltung: ADMIN_ROLE, VIEW_ROLE oder NONE.

    admin_only=True prüft nur die Leitung und ignoriert die Ansichtsgruppe.
    """
    user = request.user
    if user.is_superuser:
        return EventRole.ADMIN_ROLE
    event = get_event(event_id)
    if event is None:
        # z. B. Listenaufruf ohne ID: früher Fehler 500, jetzt "kein Recht"
        return EventRole.NONE
    # Gruppen der Person: höchstens eine Keycloak-Abfrage pro Anfrage (zwischengespeichert)
    child_ids = member_group_ids(request)
    # Leitung zuerst: Wer Leitung ist, bleibt Leitung, auch wenn die Person
    # zusätzlich in der Ansichtsgruppe ist.
    if event.admin_group and event.admin_group.keycloak_id in child_ids:
        return EventRole.ADMIN_ROLE
    if get_responsible_person_permission(user, event):
        return EventRole.ADMIN_ROLE
    if not admin_only and event.view_group and event.view_group.keycloak_id in child_ids:
        return EventRole.VIEW_ROLE
    return EventRole.NONE


def check_leader_permission(event_id: [str, Event], user: User) -> LeadershipRole:
    """Ist die Person Bundesführung (DPV) bzw. Ringführung (DPBM) mit Einblick in die Auswertung?"""
    event: Event = get_event(event_id)
    if event is None:
        return LeadershipRole.NONE
    if event.view_allow_subgroup:
        perm_name = 'dpv_bundesfuehrungen'
        perm_name_dpbm = 'dpbm_ringfuehrungen'
        if event.invited_groups.filter(name__in=["DPV"]).exists():
            bufu_group = custom_get_or_404(RequiredGroupNotFound(perm_name), Group, name=perm_name)
            if get_keycloak_permission(user, bufu_group):
                return LeadershipRole.BUND_LEADER
        if event.invited_groups.filter(name__in=["DPBM"]).exists():
            ring_group = Group.objects.filter(name=perm_name_dpbm).first()
            if ring_group and get_keycloak_permission(user, ring_group):
                return LeadershipRole.RING_LEADER
    return LeadershipRole.NONE


def check_registration_permission(registration_id: str, request) -> bool:
    """Darf die Person die Anmeldung sehen und ändern? (anmeldende Leitung oder Veranstaltungsleitung)"""
    registration: Registration = get_registration(registration_id)
    if registration is None:
        return False
    return registration.responsible_persons.contains(request.user) \
        or check_event_permission(registration.event, request, admin_only=True) != EventRole.NONE


class IsStaffOrReadOnly(permissions.BasePermission):
    """Lesen für alle, Ändern nur für das Anmeldeteam (Staff)."""
    message = 'Kann nur von den Admins bearbeitet werden'

    def has_permission(self, request: Request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS or
            (request.user and request.user.is_authenticated and request.user.is_staff)
        )


class IsEventSuperResponsiblePerson(permissions.BasePermission):
    """Veranstaltungsleitung für die Veranstaltung aus der URL (pk). Anlegen darf jede eingeloggte Person."""
    message = 'Du darfst dieses Event nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.method == CREATE_METHOD:
            return True
        event_id: str = view.kwargs.get("pk", None)
        return check_event_permission(event_id, request, admin_only=True) == EventRole.ADMIN_ROLE


class IsSubEventSuperResponsiblePerson(permissions.BasePermission):
    """Veranstaltungsleitung für Unterseiten einer Veranstaltung (event_pk), auch beim Anlegen.

    Anders als bei IsEventSuperResponsiblePerson gibt es keine Ausnahme für
    POST: Wer etwas in einer bestehenden Veranstaltung anlegt, braucht das
    Recht auf diese Veranstaltung.
    """
    message = 'Du darfst dieses Event nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        event_id: str = view.kwargs.get('event_pk', None)
        return check_event_permission(event_id, request, admin_only=True) == EventRole.ADMIN_ROLE


class IsSubEventResponsiblePerson(permissions.BasePermission):
    """Leitung oder Ansichtsgruppe der Veranstaltung (event_pk), z. B. für Auswertungen."""
    message = 'Du darfst dieses Event nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        event_id: str = view.kwargs.get('event_pk', None)
        return check_event_permission(event_id, request) != EventRole.NONE


class IsLeaderPerson(permissions.BasePermission):
    """Bundes- oder Ringführung mit Einblick in die Auswertung (event_pk)."""
    message = 'Du darfst die Statistik dieses Events nicht ansehen'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        event_id: str = view.kwargs.get('event_pk', None)
        return check_leader_permission(event_id, request.user) != LeadershipRole.NONE


class IsSubEventResponsiblePersonOrReadOnly(permissions.BasePermission):
    """Lesen für Eingeloggte, Ändern nur für die Veranstaltungsleitung (event_pk).

    Die Ansichtsgruppe darf nichts ändern (Entscheidung vom 15.10.2026).
    Früher durfte sie hier Bausteine und Preisstufen bearbeiten.
    """
    message = 'Du darfst dieses Event nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return True
        event_id: str = view.kwargs.get('event_pk', None)
        return check_event_permission(event_id, request, admin_only=True) == EventRole.ADMIN_ROLE


class IsRegistrationResponsiblePerson(permissions.BasePermission):
    """Anmeldende Leitung oder Veranstaltungsleitung für die Anmeldung aus der URL (pk)."""
    message = 'Du darfst diese Registrierung nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == CREATE_METHOD:
            return True
        if request.user.is_superuser:
            return True
        registration_id: str = view.kwargs.get('pk', None)
        return check_registration_permission(registration_id, request)


class IsSubRegistrationResponsiblePerson(permissions.BasePermission):
    """Wie IsRegistrationResponsiblePerson, für Unterseiten einer Anmeldung (registration_pk)."""
    message = 'Du darfst diese Registrierung nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        registration_id: str = view.kwargs.get('registration_pk', None)
        if registration_id is None:
            registration_id: str = view.kwargs.get('pk', None)
        return check_registration_permission(registration_id, request)


def is_event_manager(request, event) -> bool:
    """Veranstaltungsleitung (oder Superuser): von allen Fristsperren ausgenommen."""
    if request.user.is_superuser:
        return True
    return check_event_permission(event, request, admin_only=True) == EventRole.ADMIN_ROLE


def require_registration_open(request, event) -> None:
    """Wirft TooEarly oder RegistrationClosed, wenn keine neue Anmeldung möglich ist. Leitung ausgenommen."""
    from anmelde_tool.event import deadlines
    from anmelde_tool.event.api_exceptions import RegistrationClosed, TooEarly
    if is_event_manager(request, event):
        return
    if not deadlines.registration_started(event):
        raise TooEarly()
    if not deadlines.can_register(event):
        raise RegistrationClosed()


def require_changes_open(request, event) -> None:
    """Wirft TooEarly oder ChangesClosed, wenn keine Änderung möglich ist. Leitung ausgenommen."""
    from anmelde_tool.event import deadlines
    from anmelde_tool.event.api_exceptions import ChangesClosed, TooEarly
    if is_event_manager(request, event):
        return
    if not deadlines.registration_started(event):
        raise TooEarly()
    if not deadlines.can_change(event):
        raise ChangesClosed()
