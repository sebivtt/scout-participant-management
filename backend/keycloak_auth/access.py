"""Gruppenrechte prüfen und vergeben.

Grundregeln (Stand 14.10.2026):
- Rechte liegen in der Tabelle GroupPermission, nicht mehr in Keycloak.
- Keycloak liefert nur, in welchen Gruppen eine Person Mitglied ist.
- Ein Recht auf eine Gruppe gilt auch für alle ihre Untergruppen.
- Admin schließt Ansicht ein. Staff und Superuser haben überall Admin.
- Ist Keycloak nicht erreichbar, zählen nur direkt vergebene Rechte
  (sicherer Ausfall: lieber zu wenig als zu viel Recht).
"""
from __future__ import annotations

import logging
from typing import Iterable

from django.contrib.auth import get_user_model
from django.db.models import Q
from keycloak import KeycloakError

from backend.settings import keycloak_admin
from keycloak_auth.enums import PermissionType
from keycloak_auth.models import GroupPermission, KeycloakGroup

logger = logging.getLogger(__name__)
User = get_user_model()

Role = GroupPermission.Role
_CACHE_ATTR = '_keycloak_group_ids'
_MAX_DEPTH = 20


def _user_of(request_or_user):
    # Eine Anfrage erkennt man an META. Nicht nur an "user": Benutzerobjekte
    # haben selbst ein Feld "user" (Rückbezug von RequestGroupAccess).
    """Benutzer aus einer Anfrage oder den Benutzer selbst."""
    if hasattr(request_or_user, 'META'):
        return getattr(request_or_user, 'user', None)
    return request_or_user


def member_group_ids(request_or_user) -> set[str]:
    """Keycloak-IDs aller Gruppen, in denen die Person direkt Mitglied ist.

    Wird pro Anfrage zwischengespeichert, damit Keycloak höchstens einmal
    gefragt wird.
    """
    cached = getattr(request_or_user, _CACHE_ATTR, None)
    if cached is not None:
        return cached

    user = _user_of(request_or_user)
    ids: set[str] = set()
    if user is not None and getattr(user, 'keycloak_id', None):
        try:
            groups = keycloak_admin.get_user_groups(user.keycloak_id, brief_representation=True)
            ids = {group['id'] for group in groups}
        except KeycloakError as exc:
            logger.warning('Gruppen von %s nicht abrufbar, nur direkte Rechte zählen: %s', user, exc)

    try:
        setattr(request_or_user, _CACHE_ATTR, ids)
    except AttributeError:
        pass
    return ids


def resolve_group(group: KeycloakGroup | str | None) -> KeycloakGroup | None:
    """Gruppe aus Objekt oder Keycloak-ID; None, wenn es sie nicht gibt."""
    if group is None or isinstance(group, KeycloakGroup):
        return group
    return KeycloakGroup.objects.filter(keycloak_id=group).first()


def group_with_ancestors(group: KeycloakGroup) -> list[KeycloakGroup]:
    """Die Gruppe und alle Obergruppen, von unten nach oben (Schutz gegen Zyklen: höchstens 20 Ebenen)."""
    chain, current = [], group
    while current is not None and len(chain) < _MAX_DEPTH:
        chain.append(current)
        current = current.parent
    return chain


def group_role(request_or_user, group: KeycloakGroup | str | None) -> str | None:
    """Höchstes Recht der Person auf die Gruppe: 'admin', 'view' oder None."""
    user = _user_of(request_or_user)
    if user is None or not user.is_authenticated:
        return None
    if user.is_staff or user.is_superuser:
        return Role.ADMIN
    group = resolve_group(group)
    if group is None:
        return None
    return _highest_role(_held_roles(request_or_user, user, group))


def _held_roles(request_or_user, user, group: KeycloakGroup) -> set[str]:
    """Rollen auf die Gruppe oder eine Obergruppe, direkt oder über Mitgliedschaft.

    Keycloak wird nur gefragt, wenn ein Recht an einer Mitgliedschaft hängt
    und die Person es nicht ohnehin direkt hat.
    """
    permissions = list(
        GroupPermission.objects
        .filter(group__in=group_with_ancestors(group))
        .filter(Q(user=user) | Q(via_group__isnull=False))
        .select_related('via_group')
    )
    roles = {p.role for p in permissions if p.user_id == user.pk}
    via = [p for p in permissions if p.via_group_id is not None and p.role not in roles]
    if via:
        member_ids = member_group_ids(request_or_user)
        roles |= {p.role for p in via if p.via_group.keycloak_id in member_ids}
    return roles


def _highest_role(roles: set[str]) -> str | None:
    """Admin vor Ansicht; None, wenn keine Rolle vorliegt."""
    for role in (Role.ADMIN, Role.VIEW):
        if role in roles:
            return role
    return None


def has_group_permission(request_or_user, group, permission_type: PermissionType | str) -> bool:
    """Hat die Person mindestens das gewünschte Recht (admin oder view) auf die Gruppe?"""
    wanted = PermissionType(permission_type)
    role = group_role(request_or_user, group)
    if wanted == PermissionType.ADMIN:
        return role == Role.ADMIN
    if wanted == PermissionType.VIEW:
        return role in (Role.ADMIN, Role.VIEW)
    return False


def is_group_member(request_or_user, group) -> bool:
    """Ist die Person direkt Mitglied der Gruppe (laut Keycloak)?"""
    group = resolve_group(group)
    return group is not None and group.keycloak_id in member_group_ids(request_or_user)


def grant(group: KeycloakGroup, role: str, *, user=None, via_group: KeycloakGroup | None = None) -> GroupPermission:
    """Vergibt ein Recht, falls es noch nicht besteht. Genau eins von user oder via_group angeben."""
    permission, _ = GroupPermission.objects.get_or_create(group=group, role=role, user=user, via_group=via_group)
    return permission


def holders(group: KeycloakGroup | str, role: str = Role.ADMIN) -> tuple[list[KeycloakGroup], list]:
    """Gruppen und Personen, die das Recht direkt auf diese Gruppe haben.

    Ohne Vererbung von oben: gedacht für die Anzeige "Wer verwaltet diese Gruppe".
    """
    group = resolve_group(group)
    if group is None:
        return [], []
    permissions = GroupPermission.objects.filter(group=group, role=role).select_related('user', 'via_group')
    groups = [p.via_group for p in permissions if p.via_group_id]
    users = [p.user for p in permissions if p.user_id]
    return groups, users


def users_with_admin(group: KeycloakGroup | str) -> list:
    """Alle Personen, die die Gruppe verwalten dürfen, auch über Obergruppen.

    Für Benachrichtigungen, z. B. bei Beitrittsanfragen.
    """
    group = resolve_group(group)
    if group is None:
        return []
    permissions = (
        GroupPermission.objects
        .filter(group__in=group_with_ancestors(group), role=Role.ADMIN)
        .select_related('via_group')
    )
    user_ids = {p.user_id for p in permissions if p.user_id}
    keycloak_ids: set[str] = set()
    for permission in permissions:
        if permission.via_group_id:
            keycloak_ids |= set(_member_keycloak_ids(permission.via_group))
    users = User.objects.filter(Q(pk__in=user_ids) | Q(keycloak_id__in=keycloak_ids), is_active=True)
    return list(users.distinct())


def _member_keycloak_ids(group: KeycloakGroup) -> Iterable[str]:
    """Keycloak-IDs der aktiven Mitglieder einer Gruppe; leer, wenn Keycloak nicht erreichbar ist."""
    try:
        members = keycloak_admin.get_group_members(group.keycloak_id)
    except KeycloakError as exc:
        logger.warning('Mitglieder von %s nicht abrufbar: %s', group, exc)
        return []
    return [member['id'] for member in members if member.get('enabled', True)]


def has_any_admin_permission(request_or_user) -> bool:
    """Verwaltet die Person irgendeine Gruppe (oder ist Staff)?"""
    user = _user_of(request_or_user)
    if user is None or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    admin = GroupPermission.objects.filter(role=Role.ADMIN)
    if admin.filter(user=user).exists():
        return True
    via_ids = set(admin.filter(via_group__isnull=False).values_list('via_group__keycloak_id', flat=True))
    return bool(via_ids and via_ids & member_group_ids(request_or_user))


def direct_group_roles(request_or_user) -> list[tuple[str, str]]:
    """(Keycloak-Gruppen-ID, Rolle) für alle Rechte, die die Person direkt
    oder über eine Mitgliedschaft hat. Untergruppen werden nicht aufgezählt,
    für sie gilt das Recht trotzdem (siehe group_role)."""
    user = _user_of(request_or_user)
    if user is None or not user.is_authenticated:
        return []
    permissions = GroupPermission.objects.filter(Q(user=user) | Q(via_group__isnull=False)).select_related(
        'group', 'via_group'
    )
    member_ids = None
    result = []
    for permission in permissions:
        if permission.via_group_id:
            if member_ids is None:
                member_ids = member_group_ids(request_or_user)
            if permission.via_group.keycloak_id not in member_ids:
                continue
        result.append((permission.group.keycloak_id, permission.role))
    return sorted(set(result))
