// Läuft einmal vor allen Rauchtests: meldet jedes Testkonto über die echte
// Keycloak-Anmeldeseite an und ermittelt die Kennungen der Beispieldaten.
import fs from 'node:fs';
import path from 'node:path';
import { chromium, type Browser } from '@playwright/test';
import {
  ACCOUNTS, type AccountName, BACKEND_URL, FINDINGS_FILE, FRONTEND_URL, IDS_FILE, KEYCLOAK_URL, REALM,
  type SampleIds, STATE_DIR, storageStateFor,
} from './umgebung';

// Am technischen Namen erkennt load_sample_data sein Beispiellager.
const SAMPLE_TECHNICAL_NAME = 'beispieldaten';
const SAMPLE_GROUP_NAME = 'Testgruppe Lagerteam';

/** Meldet ein Konto über die Anmeldeseite an und speichert die Sitzung für die Tests. */
async function loginInBrowser(browser: Browser, account: AccountName): Promise<void> {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(`${FRONTEND_URL}/dashboard`);
  // Das Frontend leitet ohne Sitzung zur Anmeldeseite von Keycloak weiter.
  await page.waitForURL(`${KEYCLOAK_URL}/**`);
  await page.fill('#username', account);
  await page.fill('#password', ACCOUNTS[account].password);
  await page.click('#kc-login');
  await page.waitForURL(`${FRONTEND_URL}/**`);
  // Erst wenn das Frontend wieder eine eigene Seite zeigt, ist der Login abgeschlossen.
  await page.waitForLoadState('networkidle');
  await context.storageState({ path: storageStateFor(account) });
  await context.close();
}

/** Holt einen Ausweis von Keycloak ohne Browser, für Abfragen an das Backend. */
async function accessToken(account: AccountName): Promise<string> {
  const response = await fetch(`${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token`, {
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
  });
  if (!response.ok) throw new Error(`Keycloak-Login für ${account} fehlgeschlagen: ${response.status}`);
  return (await response.json()).access_token;
}

async function apiGet<T>(account: AccountName, path: string): Promise<T> {
  const response = await fetch(`${BACKEND_URL}${path}`, {
    headers: { Authorization: `Bearer ${await accessToken(account)}` },
  });
  if (!response.ok) throw new Error(`${path} als ${account}: ${response.status}`);
  return response.json() as Promise<T>;
}

/** Sucht die Kennungen des Beispiellagers, seiner Anmeldung und der Leitungsgruppe. */
async function findSampleIds(): Promise<SampleIds> {
  const events = await apiGet<{ id: string; technicalName: string }[]>('leitung', '/event/event-overview/');
  const event = events.find((e) => e.technicalName === SAMPLE_TECHNICAL_NAME);
  if (!event) {
    throw new Error('Beispiellager fehlt. Zuerst im Ordner backend/: python manage.py load_sample_data');
  }
  const registrations = await apiGet<{ id: string; event: { id: string } }[]>(
    'stammesleitung', '/event/my-registrations/');
  const registration = registrations.find((r) => r.event.id === event.id);
  if (!registration) throw new Error('Die Anmeldung von stammesleitung im Beispiellager fehlt.');
  const groups = await apiGet<{ id: string; name: string }[]>('leitung', '/auth/my-groups/');
  const group = groups.find((g) => g.name === SAMPLE_GROUP_NAME);
  if (!group) throw new Error(`Gruppe „${SAMPLE_GROUP_NAME}“ fehlt. Im Ordner backend/: python manage.py sync_keycloak_groups`);
  return { eventId: event.id, registrationId: registration.id, groupId: group.id };
}

export default async function globalSetup(): Promise<void> {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.mkdirSync(path.dirname(FINDINGS_FILE), { recursive: true });
  fs.writeFileSync(FINDINGS_FILE, '');
  fs.writeFileSync(IDS_FILE, JSON.stringify(await findSampleIds(), null, 2));
  const browser = await chromium.launch();
  try {
    for (const account of Object.keys(ACCOUNTS) as AccountName[]) {
      await loginInBrowser(browser, account);
    }
  } finally {
    await browser.close();
  }
}
