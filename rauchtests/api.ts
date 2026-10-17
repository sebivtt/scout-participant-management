// Anfragen an das Backend ohne Browser: zum Ermitteln der Kennungen in
// global-setup.ts und zum Prüfen und Aufräumen in den Tests zum Anmeldeablauf.
import { ACCOUNTS, type AccountName, BACKEND_URL, KEYCLOAK_URL, REALM } from './environment';

/** Wartet auf eine Anfrage und ersetzt „fetch failed“ durch eine verständliche Meldung. */
async function reachable(service: string, url: string, request: Promise<Response>): Promise<Response> {
  try {
    return await request;
  } catch {
    throw new Error(`${service} unter ${url} nicht erreichbar. Läuft das Tool? (docs/lokal-starten.md)`);
  }
}

/** Holt einen Ausweis von Keycloak ohne Browser, für Abfragen an das Backend. */
async function accessToken(account: AccountName): Promise<string> {
  const response = await reachable('Keycloak', KEYCLOAK_URL, fetch(`${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`, {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'password',
      client_id: 'scout-frontend',
      // Ohne „openid“ lehnt Keycloak die Abfrage der Kontodaten ab, die das Backend
      // bei jeder Anfrage stellt.
      scope: 'openid',
      username: account,
      password: ACCOUNTS[account].password,
    }),
  }));
  if (!response.ok) throw new Error(`Keycloak-Login für ${account} fehlgeschlagen: ${response.status}`);
  return (await response.json()).access_token;
}

/**
 * Schickt eine Anfrage als Testkonto ans Backend und liefert die Antwort als JSON.
 *
 * Scheitert mit einer Meldung samt Adresse und Status, wenn das Backend ablehnt.
 * Inhalte gehen in der Schreibweise des Frontends hinaus (`firstName`), das
 * Backend wandelt sie selbst um.
 */
export async function api<T = unknown>(account: AccountName, method: string, path: string, body?: unknown): Promise<T> {
  const token = await accessToken(account);
  const response = await reachable('Backend', BACKEND_URL, fetch(`${BACKEND_URL}${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, ...(body === undefined ? {} : { 'Content-Type': 'application/json' }) },
    body: body === undefined ? undefined : JSON.stringify(body),
  }));
  if (!response.ok) throw new Error(`${method} ${path} als ${account}: ${response.status} ${(await response.text()).slice(0, 200)}`);
  // Löschen antwortet ohne Inhalt, response.json() bräche dann ab.
  return (response.status === 204 ? null : await response.json()) as T;
}

/** Liest als Testkonto vom Backend (Kurzform von `api` mit GET). */
export function apiGet<T>(account: AccountName, path: string): Promise<T> {
  return api<T>(account, 'GET', path);
}
