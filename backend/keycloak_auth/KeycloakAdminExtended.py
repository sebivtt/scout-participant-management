"""Keycloak-Admin-Client mit ein paar Ergänzungen (python-keycloak 7).

Nutzt nur die Standard-Admin-API von Keycloak. Gruppenrechte liegen im Tool
selbst (keycloak_auth/access.py), nicht mehr in Keycloak.

Benötigte Rollen des Service-Accounts (Client realm-management):
view-users, query-groups, manage-users (Gruppen und Mitgliedschaften),
manage-realm (Realm-Rollen je Gruppe), manage-clients (Rollen-Zuordnung zu
den Client-Scopes dpv_oidc_scope und dpv_saml_scope, falls vorhanden).
"""
import json
import logging

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakGetError, KeycloakPostError, raise_error_from_response
from keycloak.urls_patterns import URL_ADMIN_CLIENT_SCOPE, URL_ADMIN_GROUP_CHILD

URL_ADMIN_CLIENT_SCOPE_REALM_ROLE_MAPPER = URL_ADMIN_CLIENT_SCOPE + "/scope-mappings/realm"

DPV_CLIENT_SCOPES = ('dpv_oidc_scope', 'dpv_saml_scope')

logger = logging.getLogger(__name__)


class KeycloakAdminExtended(KeycloakAdmin):

    @property
    def _realm(self) -> str:
        return self.connection.realm_name

    def get_group_by_path(self, path: str, search_in_subgroups: bool = True):
        """Gruppe über ihren vollen Pfad, z. B. "/Nordlicht/Stämme/Adler".

        Gibt None zurück, wenn es die Gruppe nicht gibt (die Bibliothek wirft
        dann einen Fehler). search_in_subgroups wird nicht mehr gebraucht und
        nur für ältere Aufrufer angenommen.
        """
        try:
            return super().get_group_by_path(path)
        except KeycloakGetError as exc:
            if exc.response_code == 404:
                return None
            raise

    def get_child_groups(self, group: dict) -> list[dict]:
        """Direkte Untergruppen. Keycloak ab Version 23 liefert sie nicht mehr
        in subGroups mit, sondern nur über einen eigenen Endpunkt."""
        if group.get('subGroups'):
            return group['subGroups']
        if not group.get('subGroupCount'):
            return []
        return self.get_group_children(group['id'], query={'max': -1})

    def get_group_by_name(self, group_name):
        return next((group for group in self.get_groups() if group['name'] == group_name), None)

    def move_group(self, group_id: str, name: str, parent: str):
        """Verschiebt eine bestehende Gruppe unter eine neue Obergruppe.

        Keycloak verschiebt nur, wenn die ID mitgeschickt wird. Ohne ID legt es
        eine neue, gleichnamige Gruppe an.
        """
        params_path = {"realm-name": self._realm, "id": parent}
        payload = {'id': group_id, 'name': name}
        data_raw = self.connection.raw_post(URL_ADMIN_GROUP_CHILD.format(**params_path), data=json.dumps(payload))
        return raise_error_from_response(data_raw, KeycloakPostError, expected_codes=[200, 201, 204])

    def rename_group(self, group_id: str, name: str):
        return self.update_group(group_id=group_id, payload={'name': name})

    def add_realm_role_to_dpv_scopes(self, realm_role: dict) -> None:
        """Hängt eine Realm-Rolle an die DPV-Client-Scopes, sofern es sie gibt."""
        scope_ids = {scope['name']: scope['id'] for scope in self.get_client_scopes()}
        for scope_name in DPV_CLIENT_SCOPES:
            scope_id = scope_ids.get(scope_name)
            if not scope_id:
                logger.info('Client-Scope %s fehlt, Rolle %s wird nicht zugeordnet', scope_name, realm_role['name'])
                continue
            params_path = {"realm-name": self._realm, "scope-id": scope_id}
            data_raw = self.connection.raw_post(
                URL_ADMIN_CLIENT_SCOPE_REALM_ROLE_MAPPER.format(**params_path), data=json.dumps([realm_role])
            )
            raise_error_from_response(data_raw, KeycloakPostError, expected_codes=[204])
