#!/usr/bin/env bash
# Richtet einen lokalen Keycloak-Realm für das Scout-Tool ein (nur Entwicklung!).
# Standard: Keycloak aus dev/docker-compose.yml. Für ein lokal entpacktes
# Keycloak: KCADM=/pfad/zu/keycloak/bin/kcadm.sh ./keycloak-setup.sh
# Das Skript kann gefahrlos mehrfach laufen.
set -euo pipefail
cd "$(dirname "$0")"

KC_URL="${KC_URL:-http://localhost:8180}"
KCADM="${KCADM:-docker compose exec -T keycloak /opt/keycloak/bin/kcadm.sh}"
REALM="${REALM:-dpv}"
FRONT_URL="${FRONT_URL:-http://localhost:8080}"
BACKEND_SECRET="${BACKEND_SECRET:-dev-backend-secret}"

$KCADM config credentials --server "$KC_URL" --realm master --user admin --password admin >/dev/null

if ! $KCADM get "realms/$REALM" >/dev/null 2>&1; then
  $KCADM create realms -s realm="$REALM" -s enabled=true -s registrationAllowed=true \
    -s 'attributes={"unmanagedAttributePolicy":"ENABLED"}' >/dev/null
  # Freie Benutzerattribute (fahrtenname, stamm, bund) erlauben
  $KCADM update "realms/$REALM/users/profile" -f - <<'EOF' >/dev/null || true
{"unmanagedAttributePolicy":"ENABLED","attributes":[
 {"name":"username","displayName":"${username}","permissions":{"view":["admin","user"],"edit":["admin","user"]}},
 {"name":"email","displayName":"${email}","permissions":{"view":["admin","user"],"edit":["admin","user"]}},
 {"name":"firstName","displayName":"${firstName}","permissions":{"view":["admin","user"],"edit":["admin","user"]}},
 {"name":"lastName","displayName":"${lastName}","permissions":{"view":["admin","user"],"edit":["admin","user"]}}]}
EOF
fi

# Client-Scopes, die das Backend beim Start erwartet
for SCOPE in dpv_oidc_scope:openid-connect dpv_saml_scope:saml; do
  NAME="${SCOPE%%:*}"; PROTO="${SCOPE##*:}"
  if ! $KCADM get client-scopes -r "$REALM" --fields name | grep -q "\"$NAME\""; then
    $KCADM create client-scopes -r "$REALM" -s name="$NAME" -s protocol="$PROTO" >/dev/null
  fi
done
OIDC_SCOPE_ID=$($KCADM get client-scopes -r "$REALM" --fields id,name --format csv --noquotes | grep ',dpv_oidc_scope$' | cut -d, -f1)

add_mapper () { # name, json
  if ! $KCADM get "client-scopes/$OIDC_SCOPE_ID/protocol-mappers/models" -r "$REALM" --fields name | grep -q "\"$1\""; then
    echo "$2" | $KCADM create "client-scopes/$OIDC_SCOPE_ID/protocol-mappers/models" -r "$REALM" -f - >/dev/null
  fi
}
add_mapper roles '{"name":"roles","protocol":"openid-connect","protocolMapper":"oidc-usermodel-realm-role-mapper","config":{"claim.name":"roles","multivalued":"true","jsonType.label":"String","access.token.claim":"true","id.token.claim":"true","userinfo.token.claim":"true"}}'
for ATTR in fahrtenname stamm bund; do
  add_mapper "$ATTR" "{\"name\":\"$ATTR\",\"protocol\":\"openid-connect\",\"protocolMapper\":\"oidc-usermodel-attribute-mapper\",\"config\":{\"user.attribute\":\"$ATTR\",\"claim.name\":\"$ATTR\",\"jsonType.label\":\"String\",\"access.token.claim\":\"true\",\"id.token.claim\":\"true\",\"userinfo.token.claim\":\"true\"}}"
done
$KCADM update "realms/$REALM/default-default-client-scopes/$OIDC_SCOPE_ID" >/dev/null 2>&1 || true

# Frontend-Client (öffentlich)
if ! $KCADM get clients -r "$REALM" -q clientId=scout-frontend --fields id | grep -q id; then
  $KCADM create clients -r "$REALM" -s clientId=scout-frontend -s publicClient=true \
    -s standardFlowEnabled=true -s directAccessGrantsEnabled=true \
    -s "redirectUris=[\"$FRONT_URL/*\"]" -s "webOrigins=[\"$FRONT_URL\"]" \
    -s 'attributes={"post.logout.redirect.uris":"+"}' >/dev/null
fi

# Backend-Admin-Client (Service-Account mit Realm-Admin-Rechten)
if ! $KCADM get clients -r "$REALM" -q clientId=scout-backend --fields id | grep -q id; then
  $KCADM create clients -r "$REALM" -s clientId=scout-backend -s publicClient=false \
    -s secret="$BACKEND_SECRET" -s serviceAccountsEnabled=true -s standardFlowEnabled=false >/dev/null
  $KCADM add-roles -r "$REALM" --uusername service-account-scout-backend --cclientid realm-management --rolename realm-admin >/dev/null
fi

# Rolle für das Organisationsteam und Testbenutzer
$KCADM create roles -r "$REALM" -s name=anmelde_tool_team >/dev/null 2>&1 || true
create_user () { # username password first last fahrtenname team?
  if ! $KCADM get users -r "$REALM" -q username="$1" --fields id | grep -q id; then
    $KCADM create users -r "$REALM" -s username="$1" -s email="$1@example.org" -s emailVerified=true \
      -s firstName="$3" -s lastName="$4" -s enabled=true -s "attributes.fahrtenname=$5" >/dev/null
    $KCADM set-password -r "$REALM" --username "$1" --new-password "$2"
  fi
  [ "${6:-}" = team ] && $KCADM add-roles -r "$REALM" --uusername "$1" --rolename anmelde_tool_team || true
}
create_user leitung leitung123 Lena Leitung Lux team
create_user stammesleitung stamm123 Sina Stamm Eule
create_user teilnehmer teilnehmer123 Tim Teilnehmer Fuchs

# Testgruppe für Veranstaltungen: Beim Anlegen einer Veranstaltung muss man
# Gruppen wählen, in denen man selbst Mitglied ist.
TESTGRUPPE="Testgruppe Lagerteam"
if ! $KCADM get groups -r "$REALM" -q search="$TESTGRUPPE" --fields name | grep -q "\"$TESTGRUPPE\""; then
  $KCADM create groups -r "$REALM" -s name="$TESTGRUPPE" >/dev/null
fi
GROUP_ID=$($KCADM get groups -r "$REALM" -q search="$TESTGRUPPE" --fields id,name --format csv --noquotes | grep ",$TESTGRUPPE$" | cut -d, -f1)
for U in leitung stammesleitung; do
  USER_ID=$($KCADM get users -r "$REALM" -q username="$U" -q exact=true --fields id --format csv --noquotes)
  $KCADM update "users/$USER_ID/groups/$GROUP_ID" -r "$REALM" -n >/dev/null
done

echo "Keycloak-Realm '$REALM' ist eingerichtet ($KC_URL)."
