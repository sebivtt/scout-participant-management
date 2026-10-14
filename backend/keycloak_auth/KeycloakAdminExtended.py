"""Keycloak-Admin-Client mit ein paar Ergänzungen.

Nutzt nur die Standard-Admin-API von Keycloak. Die früher hier vorhandene
Rechteverwaltung über Client-Rollen und Policies am realm-management-Client
(Keycloak-Funktion admin-fine-grained-authz:v1, veraltet und beim Verband
abgeschaltet) ist entfallen. Gruppenrechte liegen jetzt im Tool selbst,
siehe keycloak_auth/access.py.

Benötigte Rollen des Service-Accounts (Client realm-management):
view-users, query-groups, manage-users (Gruppen und Mitgliedschaften),
manage-realm (Realm-Rollen je Gruppe), manage-clients (Rollen-Zuordnung zu
den Client-Scopes dpv_oidc_scope und dpv_saml_scope, falls vorhanden).
"""
import json
import logging
from urllib.parse import quote

from keycloak import KeycloakAdmin
from keycloak.exceptions import raise_error_from_response, KeycloakGetError, KeycloakPostError
from keycloak.urls_patterns import URL_ADMIN_GROUP_CHILD, URL_ADMIN_CLIENT_SCOPE

URL_ADMIN_GROUP_COUNT = "admin/realms/{realm-name}/groups/count"
URL_ADMIN_GROUP_BY_PATH = "admin/realms/{realm-name}/group-by-path/{path}"
URL_ADMIN_CLIENT_SCOPE_REALM_ROLE_MAPPER = URL_ADMIN_CLIENT_SCOPE + "/scope-mappings/realm"

DPV_CLIENT_SCOPES = ('dpv_oidc_scope', 'dpv_saml_scope')

logger = logging.getLogger(__name__)


class KeycloakAdminExtended(KeycloakAdmin):

    def get_group_by_path(self, path: str, search_in_subgroups: bool = True):
        """Gruppe über ihren vollen Pfad, z. B. "/Nordlicht/Stämme/Adler".

        Fragt Keycloak direkt (Endpunkt group-by-path). Die Fassung der
        Bibliothek durchsucht die Untergruppen aus get_groups(). Die liefert
        Keycloak seit Version 23 nicht mehr mit, deshalb wurden verschachtelte
        Gruppen nicht gefunden und doppelt angelegt (Fehler 409).
        """
        params_path = {"realm-name": self.realm_name, "path": quote(path.lstrip('/'), safe='/')}
        data_raw = self.raw_get(URL_ADMIN_GROUP_BY_PATH.format(**params_path))
        if data_raw.status_code == 404:
            return None
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_subgroups(self, group: dict) -> list[dict]:
        """Direkte Untergruppen. Keycloak ab Version 23 liefert sie nur noch
        über einen eigenen Endpunkt, ältere Versionen direkt in subGroups."""
        if group.get('subGroups'):
            return group['subGroups']
        if not group.get('subGroupCount'):
            return []
        params_path = {"realm-name": self.realm_name, "id": group['id']}
        data_raw = self.raw_get(URL_ADMIN_GROUP_CHILD.format(**params_path), max=-1)
        return raise_error_from_response(data_raw, KeycloakGetError)

    def get_group_by_name(self, group_name):
        return next((group for group in self.get_groups() if group['name'] == group_name), None)

    def move_group(self, group_id: str, name: str, parent: str):
        """Verschiebt eine bestehende Gruppe unter eine neue Obergruppe.

        Keycloak verschiebt nur, wenn die ID mitgeschickt wird. Ohne ID legt es
        eine neue, gleichnamige Gruppe an (früherer Fehler).
        """
        params_path = {"realm-name": self.realm_name, "id": parent}
        payload = {'id': group_id, 'name': name}
        data_raw = self.raw_post(URL_ADMIN_GROUP_CHILD.format(**params_path), data=json.dumps(payload))
        return raise_error_from_response(data_raw, KeycloakPostError, expected_codes=[200, 201, 204])

    def rename_group(self, group_id: str, name: str):
        return self.update_group(group_id=group_id, payload={'name': name})

    def add_realm_role_to_dpv_scopes(self, realm_role: dict) -> None:
        """Hängt eine Realm-Rolle an die DPV-Client-Scopes, sofern es sie gibt.

        Fehlen die Scopes (z. B. in einer Testumgebung), wird das nur geloggt.
        """
        scope_ids = {scope['name']: scope['id'] for scope in self.get_client_scopes()}
        for scope_name in DPV_CLIENT_SCOPES:
            scope_id = scope_ids.get(scope_name)
            if not scope_id:
                logger.info('Client-Scope %s fehlt, Rolle %s wird nicht zugeordnet', scope_name, realm_role['name'])
                continue
            params_path = {"realm-name": self.realm_name, "scope-id": scope_id}
            data_raw = self.raw_post(
                URL_ADMIN_CLIENT_SCOPE_REALM_ROLE_MAPPER.format(**params_path), data=json.dumps([realm_role])
            )
            raise_error_from_response(data_raw, KeycloakPostError, expected_codes=[204])

    def groups_count(self, query=None):
        query = query or dict()
        params_path = {"realm-name": self.realm_name}
        data_raw = self.raw_get(URL_ADMIN_GROUP_COUNT.format(**params_path), **query)
        return raise_error_from_response(data_raw, KeycloakGetError)
