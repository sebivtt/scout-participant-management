// Läuft einmal vor allen Rauchtests: meldet jedes Testkonto über die echte
// Keycloak-Anmeldeseite an und ermittelt die Kennungen der Beispieldaten.
import fs from 'node:fs';
import path from 'node:path';
import { chromium, type Browser } from '@playwright/test';
import { apiGet } from './api';
import {
  ACCOUNTS, type AccountName, FINDINGS_FILE, FRONTEND_URL, IDS_FILE, KEYCLOAK_URL,
  type SampleIds, AUTH_DIR, storageStateFor,
} from './environment';

// An den technischen Namen erkennt load_sample_data seine Veranstaltungen.
const SAMPLE_TECHNICAL_NAME = 'beispieldaten';
const TRIP_TECHNICAL_NAME = 'beispielfahrt';
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
  try {
    await page.waitForURL(`${FRONTEND_URL}/**`, { timeout: 15_000 });
  } catch {
    // Bleibt man auf der Anmeldeseite, fehlt das Konto oder das Passwort stimmt nicht.
    throw new Error(`Login als ${account} gescheitert. Testkonten anlegen: im Ordner dev/ ./keycloak-setup.sh`);
  }
  // Erst wenn das Frontend wieder eine eigene Seite zeigt, ist der Login abgeschlossen.
  await page.waitForLoadState('networkidle');
  await context.storageState({ path: storageStateFor(account) });
  await context.close();
}

/** Sucht die Kennungen des Beispiellagers, seiner Anmeldung, der Beispielfahrt und der Leitungsgruppe. */
async function findSampleIds(): Promise<SampleIds> {
  const events = await apiGet<{ id: string; technicalName: string }[]>('leitung', '/event/event-overview/');
  const event = events.find((e) => e.technicalName === SAMPLE_TECHNICAL_NAME);
  if (!event) {
    throw new Error('Beispiellager fehlt. Zuerst im Ordner backend/: python manage.py load_sample_data');
  }
  // Die Beispielfahrt leitet stammesleitung (Grund in load_sample_data).
  const ownEvents = await apiGet<{ id: string; technicalName: string }[]>('stammesleitung', '/event/event-overview/');
  const trip = ownEvents.find((e) => e.technicalName === TRIP_TECHNICAL_NAME);
  if (!trip) {
    throw new Error('Beispielfahrt fehlt: Die Beispieldaten sind älter als die Tests zum Anmeldeablauf. '
      + 'Im Ordner backend/: python manage.py load_sample_data --reset');
  }
  const registrations = await apiGet<{ id: string; event: { id: string } }[]>(
    'stammesleitung', '/event/my-registrations/');
  const registration = registrations.find((r) => r.event.id === event.id);
  if (!registration) throw new Error('Die Anmeldung von stammesleitung im Beispiellager fehlt.');
  const groups = await apiGet<{ id: string; name: string }[]>('leitung', '/auth/my-groups/');
  const group = groups.find((g) => g.name === SAMPLE_GROUP_NAME);
  if (!group) throw new Error(`Gruppe „${SAMPLE_GROUP_NAME}“ fehlt. Im Ordner backend/: python manage.py sync_keycloak_groups`);
  return { eventId: event.id, registrationId: registration.id, groupId: group.id, tripEventId: trip.id };
}

export default async function globalSetup(): Promise<void> {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
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
  await checkMembersOfParticipant();
}

/**
 * Prüft, ob `teilnehmer` unter „Stammesmitglied anmelden“ seine Personen sieht.
 *
 * Das klappt nur, wenn sein Stamm eine Keycloak-Gruppe hat. Den Stamm übernimmt
 * das Backend erst beim Login, deshalb steht die Prüfung nach den Logins. Ohne
 * sie scheiterte der Test zum Anmeldeablauf an einer leeren Liste, ohne dass
 * man sähe, warum.
 */
async function checkMembersOfParticipant(): Promise<void> {
  const members = await apiGet<{ results: { firstName: string }[] }>('teilnehmer', '/auth/my-members-addable/');
  if (!members.results.some((member) => member.firstName === 'Ben')) {
    throw new Error('teilnehmer sieht keine Stammesmitglieder. Im Ordner dev/: ./keycloak-setup.sh, '
      + 'dann im Ordner backend/: python manage.py sync_keycloak_groups und python manage.py load_sample_data --reset');
  }
}
