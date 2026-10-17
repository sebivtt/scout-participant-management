// Rauchtest 1b: Jede Seite lädt ohne Programmfehler.
//
// Jede Seite wird einmal mit dem Testkonto geöffnet, das sie im Alltag nutzt.
// Geprüft wird: keine Programmfehler im Browser, keine Serverfehler, die Seite
// zeigt Inhalt und landet nicht auf „Seite nicht gefunden“ oder der Anmeldung.
import fs from 'node:fs';
import { test, expect, type Page } from '@playwright/test';
import { watchPage } from '../fehler';
import {
  type AccountName, FINDINGS_FILE, IDS_FILE, KEYCLOAK_URL, type SampleIds, storageStateFor,
} from '../umgebung';

interface PageCheck {
  /** Wie die Seite im Testbericht heißt. */
  name: string;
  /** Adresse der Seite. Kennungen kommen aus den Beispieldaten. */
  path: (ids: SampleIds) => string;
  /** Ohne Konto: öffentliche Seite ohne Anmeldung. */
  account: AccountName | null;
  /** Für Seiten, die nur über einen Klick erreichbar sind, weil ihre Adresse eine Kennung braucht, die sonst niemand kennt. */
  then?: (page: Page) => Promise<void>;
  /**
   * Bekannte Fehler dieser Seite mit Issue. Sie lassen den Test nicht scheitern.
   * Tritt einer nicht mehr auf, scheitert der Test, damit die Markierung entfernt
   * wird (wie xfail(strict=True) im Backend). Andere Fehler bleiben Fehler.
   */
  known?: { text: string; issue: string }[];
}

const PAGES: PageCheck[] = [
  // Öffentliche Seiten
  { name: 'Startseite', path: () => '/landing', account: null },
  { name: 'Häufige Fragen', path: () => '/landing-faq-main', account: null },
  { name: 'Impressum', path: () => '/landing-impressum-main', account: null },
  { name: 'Datenschutz', path: () => '/landing-privacy-main', account: null },
  { name: 'Kontakt', path: () => '/landing-contact-main', account: null },
  { name: 'Karte', path: () => '/map', account: null },
  { name: 'Registrierung', path: () => '/register/start', account: null },
  { name: 'Seite nicht gefunden', path: () => '/404', account: null },

  // Für alle Eingeloggten (Konto ohne besondere Rolle)
  { name: 'Übersicht', path: () => '/dashboard/main', account: 'teilnehmer' },
  { name: 'Veranstaltungen: Einladungen', path: () => '/event/invitations?status=pending', account: 'teilnehmer' },
  { name: 'Veranstaltungen: Anmeldungen', path: () => '/event/registrations?status=pending', account: 'teilnehmer' },
  { name: 'Veranstaltungen: Planungsjurte', path: () => '/event/planungsjurte?status=open', account: 'teilnehmer' },
  { name: 'Einladung zum Beispiellager', path: (ids) => `/invitation-details/${ids.eventId}`, account: 'teilnehmer' },
  {
    name: 'Anmeldung starten: erster Schritt',
    path: (ids) => `/invitation-details/${ids.eventId}`,
    account: 'teilnehmer',
    then: async (page) => {
      await page.getByRole('button', { name: 'Anmeldung starten' }).click();
      await page.waitForURL(/\/registration-new\//);
    },
  },
  { name: 'Neue Veranstaltung: Start', path: () => '/event-new/start', account: 'teilnehmer' },
  { name: 'Gruppen: Meine Gruppen', path: () => '/group/my-groups', account: 'teilnehmer' },
  { name: 'Gruppen: Suche', path: () => '/group/group-search', account: 'teilnehmer' },
  { name: 'Aufgaben', path: () => '/task/all-tasks?status=offen', account: 'teilnehmer' },
  { name: 'Aufgaben: meine Anfragen', path: () => '/task/my-requested-tasks', account: 'teilnehmer' },
  { name: 'Benachrichtigungen', path: () => '/notification/all-notification', account: 'teilnehmer' },
  { name: 'Hilfe', path: () => '/help/all-hints', account: 'teilnehmer' },
  { name: 'Nachrichten', path: () => '/message/new-messages?status=unread', account: 'teilnehmer' },
  { name: 'Einstellungen: Allgemein', path: () => '/settings/general', account: 'teilnehmer' },
  { name: 'Einstellungen: Bearbeiten', path: () => '/settings/general/edit', account: 'teilnehmer' },
  { name: 'Einstellungen: Passwort', path: () => '/settings/password', account: 'teilnehmer' },
  { name: 'Einstellungen: Benachrichtigungen', path: () => '/settings/notifications', account: 'teilnehmer' },
  { name: 'Einstellungen: Meine Gruppen', path: () => '/settings/myGroups', account: 'teilnehmer' },

  // Anmeldende Leitung: ihre eigene Anmeldung
  {
    name: 'Meine Anmeldung zum Beispiellager',
    path: (ids) => `/registrations-details/${ids.registrationId}`,
    account: 'stammesleitung',
    // Der Dialog „Verantwortliche Person hinzufügen“ sucht beim Laden in allen
    // Konten. Das darf seit PR #2 nur, wer Admin-Recht auf eine Gruppe hat.
    known: [{ text: 'Backend antwortet 403: GET /keycloak/members/', issue: '#60' }],
  },

  // Veranstaltungsleitung: Verwaltung und Auswertung des Beispiellagers
  { name: 'Veranstaltung verwalten', path: (ids) => `/event-details/${ids.eventId}`, account: 'leitung' },
  ...['summary', 'registration', 'results', 'attributes', 'actions', 'payments', 'persons', 'maps', 'mail'].map(
    (tab): PageCheck => ({
      name: `Auswertung: ${tab}`, path: (ids) => `/event-statistic/${ids.eventId}/${tab}`, account: 'leitung',
    }),
  ),
  { name: 'Zahlungen einer Anmeldung', path: (ids) => `/event-payment-details/${ids.registrationId}`, account: 'leitung' },
  { name: 'Anmeldung ansehen (Leitung)', path: (ids) => `/registrations-details/${ids.registrationId}`, account: 'leitung' },
  { name: 'Gruppe: Übersicht', path: (ids) => `/group-details/${ids.groupId}/overview`, account: 'leitung' },
  { name: 'Gruppe: Mitglieder', path: (ids) => `/group-details/${ids.groupId}/member`, account: 'leitung' },
  { name: 'Gruppe: Beitrittsanfragen', path: (ids) => `/group-details/${ids.groupId}/requests`, account: 'leitung' },
  { name: 'Mitglieder: Personen', path: () => '/person/person-all', account: 'leitung' },
  { name: 'Mitglieder: Konten', path: () => '/person/user-all', account: 'leitung' },
];

const ids: SampleIds = fs.existsSync(IDS_FILE) ? JSON.parse(fs.readFileSync(IDS_FILE, 'utf8')) : null;

for (const check of PAGES) {
  const who = check.account ?? 'ohne Anmeldung';
  test.describe(who, () => {
    if (check.account) test.use({ storageState: storageStateFor(check.account) });

    test(check.name, async ({ page }, testInfo) => {
      const findings = watchPage(page);
      await page.goto(check.path(ids));
      await page.waitForLoadState('networkidle');
      if (check.then) {
        await check.then(page);
        await page.waitForLoadState('networkidle');
      }

      // Bekannte Fehler aussortieren. Jeder muss noch auftreten, sonst ist er behoben.
      for (const known of check.known ?? []) {
        const matching = findings.errors.filter((error) => error.includes(known.text));
        expect(matching, `Bekannter Fehler (Issue ${known.issue}) tritt nicht mehr auf: Markierung entfernen`)
          .not.toEqual([]);
        findings.errors = findings.errors.filter((error) => !error.includes(known.text));
        findings.notes.push(...matching.map((error) => `Bekannt (Issue ${known.issue}): ${error}`));
      }

      // Übersicht aller Seiten für den Vergleich vor und nach einem Update
      // (Fahrplan, „Vorgehen für künftige Updates“), auch Vue-Warnungen.
      const entry = { page: check.name, account: who, url: page.url(), ...findings };
      fs.appendFileSync(FINDINGS_FILE, `${JSON.stringify(entry)}\n`);
      await testInfo.attach('befunde.json', { body: JSON.stringify(entry, null, 2), contentType: 'application/json' });

      // Landet eine geschützte Seite auf der Anmeldung, ist die gespeicherte Sitzung ungültig.
      expect(page.url(), 'Weitergeleitet zur Anmeldung').not.toContain(KEYCLOAK_URL);
      if (!check.path(ids).startsWith('/404')) {
        expect(page.url(), 'Gelandet auf „Seite nicht gefunden“').not.toContain('/404');
      }
      await expect(page.locator('body'), 'Seite ist leer').not.toHaveText(/^\s*$/);
      expect(findings.errors, 'Fehler beim Laden').toEqual([]);
    });
  });
}
