from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request

from .access import has_group_permission, is_group_member
from .enums import PermissionType
from .helper import check_group_id

User = get_user_model()


def request_access(request, role_name: str) -> bool:
    """Prüft eine Rolle aus dem Login-Token (z. B. 'anmelde_tool_team')."""
    return any(role_name == group.name for group in request.user.groups.all())


def request_group_access(request, group_id: str, permission_type: PermissionType) -> bool:
    """Hat die Person das Recht auf die Gruppe? Siehe keycloak_auth/access.py."""
    return has_group_permission(request, group_id, permission_type)


def group_id_from_view(view) -> str | None:
    """Gruppen-ID aus der URL: /keycloak/group/<pk>/ oder /keycloak/group/<group_pk>/<...>/"""
    for key in ('group_pk', 'pk'):
        group_id = view.kwargs.get(key)
        if group_id and check_group_id(group_id):
            return group_id
    return None


class IsStaffOrReadOnly(permissions.BasePermission):
    message = 'Kann nur von den Admins bearbeitet werden'

    def has_permission(self, request: Request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS or
            (request.user and request.user.is_authenticated and request.user.is_staff)
        )


class CanViewClients(permissions.BasePermission):
    message = 'Keine Berechtigung um Clients einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        return request_access(request, 'view-clients')


class IsGroupAdmin(permissions.BasePermission):
    """Admin-Recht auf die Gruppe aus der URL."""
    message = 'Keine Berechtigung, diese Gruppe zu verwalten'

    def has_permission(self, request: Request, view) -> bool:
        group_id = group_id_from_view(view)
        return bool(group_id) and has_group_permission(request, group_id, PermissionType.ADMIN)


class IsGroupViewerOrMember(permissions.BasePermission):
    """Ansichtsrecht auf die Gruppe aus der URL, oder Mitglied der Gruppe."""
    message = 'Keine Berechtigung, diese Gruppe einzusehen'

    def has_permission(self, request: Request, view) -> bool:
        group_id = group_id_from_view(view)
        if not group_id:
            return False
        return has_group_permission(request, group_id, PermissionType.VIEW) or is_group_member(request, group_id)


class IsGroupAdminForWriting(IsGroupAdmin):
    """Lesen für alle Eingeloggten, Ändern nur mit Admin-Recht auf die Gruppe."""

    def has_permission(self, request: Request, view) -> bool:
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return super().has_permission(request, view)
