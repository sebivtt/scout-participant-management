// Rauchtest 1c: der Anmeldeablauf und die Pflichtpunkte aus Fehlern, die nur
// durch Klicken auffielen (Issues #19, #20, #23, #25, Fahrplan „Vorarbeit für die
// Rauchtests“).
//
// Anders als seiten.spec.ts klicken diese Tests ganze Abläufe durch und prüfen,
// was dabei herauskommt. Was sie im Backend anlegen oder ändern, setzen sie vor
// und nach jedem Test auf die Werte aus load_sample_data zurück, auch wenn sie
// unterwegs scheitern oder ein früherer Lauf abgebrochen wurde.
import fs from 'node:fs';
import { test, expect, type Locator, type Page, type TestInfo } from '@playwright/test';
import { api, apiGet } from '../api';
import { type ExpectedError, type Findings, unexpectedErrors, watchPage } from '../findings';
import { FINDINGS_FILE, IDS_FILE, type SampleIds, storageStateFor } from '../environment';

const ids: SampleIds = fs.existsSync(IDS_FILE) ? JSON.parse(fs.readFileSync(IDS_FILE, 'utf8')) : null;

// Werte aus backend/basic/management/commands/load_sample_data.py. Auf sie setzen
// die Tests zurück. Feste Werte statt der beim Start gelesenen: Hätte ein
// abgebrochener Lauf etwas verändert, würde sonst der veränderte Stand bewahrt.
const SAMPLE_PRICE = 15;
const SAMPLE_ADDRESS = 'Am Lagerfeuer 1';
const SHARED_ADDRESS = 'Am Bach 2';
// Stammesmitglieder von teilnehmer. Alle anderen Personen, die er gespeichert hat,
// stammen aus einem Testlauf.
const SAMPLE_MEMBERS = ['Ben Probe', 'Mia Beispiel'];

// Wie bei Nutzenden in Deutschland. Sonst zeigt der Browser Geburtstage, die das
// Backend als Mitternacht deutscher Zeit speichert, einen Tag zu früh an, und
// unverändertes Speichern würde sie verschieben.
test.use({ timezoneId: 'Europe/Berlin' });

// --- Erwartete Fehlermeldungen ---------------------------------------------------

/** Bei jeder neuen Anmeldung: Der Dialog „Stammesmitglied anmelden“ fragt die Veranstaltung als Anmeldung ab. */
function registrationProbe(): ExpectedError {
  return {
    text: `Backend antwortet 404: GET /event/registration-read/${ids.eventId}/`,
    issue: '#63',
  };
}

const MEMBER_SEARCH_403: ExpectedError = {
  text: 'Backend antwortet 403: GET /keycloak/members/?search=', issue: '#60',
};

// --- Hilfen für die Oberfläche ---------------------------------------------------

/**
 * Eingabefeld zu einer Beschriftung.
 *
 * Die Felder des Tools verknüpfen Beschriftung und Eingabe nicht (kein `for`),
 * deshalb hilft `getByLabel` nicht. Die Eingabe steht im Element direkt nach
 * der Beschriftung.
 */
function field(scope: Locator | Page, label: string): Locator {
  return scope.locator(`label:text-is("${label}") + div input, label:text-is("${label}") + div textarea`);
}

/** Inhalt des aktuellen Schritts, ohne Kopfzeile und Schrittanzeige. */
function stepContent(page: Page): Locator {
  return page.locator('main main');
}

/** Schrittanzeige oben im Anmeldeablauf. Sie zeigt die technischen Namen der Schritte. */
function stepLink(page: Page, name: string): Locator {
  return page.locator('nav[aria-label="Progress"]').getByRole('link', { name, exact: true });
}

/** Die Fehlermeldung oben rechts (Baustein Error.vue). */
function errorMessage(page: Page): Locator {
  return page.getByText('Fehler', { exact: true }).locator('..');
}

/** Klickt „weiter“ und wartet, bis der nächste Schritt (erkennbar an der Adresse) geöffnet ist. */
async function next(page: Page, urlPart: RegExp): Promise<void> {
  await page.getByRole('button', { name: 'weiter' }).click();
  await page.waitForURL(urlPart);
}

/** Einträge der Personenliste im Schritt „Teilnehmende“, z. B. „Ben Probe (14)“. */
async function personList(page: Page): Promise<string[]> {
  const items = await stepContent(page).locator('li').allInnerTexts();
  return items.map((item) => item.split('\n')[0].trim());
}

/** Öffnet die Einladung zum Beispiellager und füllt den ersten Schritt für den Stamm Falken aus. */
async function startRegistration(page: Page): Promise<void> {
  await page.goto(`/invitation-details/${ids.eventId}`);
  await page.getByRole('button', { name: 'Anmeldung starten' }).click();
  await page.waitForURL(/\/introduction\//);
  await page.getByRole('combobox', { name: 'Gruppe*' }).fill('Falken');
  await page.getByRole('option', { name: 'Falken', exact: true }).click();
  // Datenschutzhinweis und Veranstaltungsbedingungen
  await stepContent(page).getByRole('switch').nth(0).click();
  await stepContent(page).getByRole('switch').nth(1).click();
  await next(page, /\/participants\//);
}

/** Legt im Schritt „Teilnehmende“ eine neue Person an. */
async function addNewPerson(page: Page, firstName: string, lastName: string, birthday: string): Promise<void> {
  await page.getByRole('button', { name: 'Neue Person hinzufügen' }).click();
  const dialog = page.getByRole('dialog');
  await field(dialog, 'Vorname*').fill(firstName);
  await field(dialog, 'Nachname*').fill(lastName);
  await field(dialog, 'Geburtstag*').fill(birthday);
  await field(dialog, 'Straße und Hausnummer*').fill('Zeltweg 4');
  await field(dialog, 'Postleitzahl*').fill('10115');
  await dialog.getByRole('button', { name: 'Speichern' }).click();
  await expect(dialog).toHaveCount(0);
}

/** Wählt im Dialog „Stammesmitglied anmelden“ Personen aus und bestätigt. */
async function addMembers(page: Page, names: string[]): Promise<void> {
  await page.getByRole('button', { name: 'Stammesmitglied anmelden' }).click();
  const dialog = page.getByRole('dialog');
  for (const name of names) {
    await dialog.getByRole('row', { name: new RegExp(name) }).getByRole('checkbox').check();
  }
  await dialog.getByRole('button', { name: 'Anmelden' }).click();
  await expect(dialog).toHaveCount(0);
}

/** Legt im Schritt „Anreise“ oder „Rückreise“ einen Eintrag mit Bahnhof an. */
async function addTravel(page: Page, station: string): Promise<void> {
  await page.getByRole('button', { name: 'Neuer Eintrag' }).click();
  const dialog = page.getByRole('dialog');
  await field(dialog, 'Welcher Bahnhof').fill(station);
  await dialog.getByRole('button', { name: 'Speichern' }).click();
  await expect(dialog).toHaveCount(0);
  await expect(stepContent(page).getByText(station)).toBeVisible();
}

// --- Prüfen und Aufräumen über das Backend ---------------------------------------

interface Attribute {
  type: string;
  attributeModule: { title: string };
  integerField?: number;
  stringField?: string;
  description?: string;
}

interface RegistrationRead {
  id: string;
  event: { id: string };
  scoutOrganisation: { name: string };
  registrationparticipantSet: { id: number; firstName: string; lastName: string; birthday: string;
    address: string; zipCode: { zipCode: string }; bookingOption: { id: number } }[];
  attributes: Attribute[];
}

/**
 * Entfernt, was die Tests als `teilnehmer` hinterlassen können.
 *
 * Das sind seine Anmeldungen im Beispiellager (er hat dort sonst keine) und
 * Personen, die das Backend beim Absenden dauerhaft speichert („Person dauerhaft
 * speichern“ ist im Dialog vorausgewählt). Heute entstehen dabei keine, aber
 * sonst erschienen sie im nächsten Lauf unter „Stammesmitglied anmelden“.
 */
async function cleanUpParticipant(): Promise<void> {
  const registrations = await apiGet<{ id: string; event: { id: string } }[]>('teilnehmer', '/event/my-registrations/');
  for (const registration of registrations.filter((r) => r.event.id === ids.eventId)) {
    await api('teilnehmer', 'DELETE', `/event/registration/${registration.id}/`);
  }
  const members = await apiGet<{ results: { id: string; firstName: string; lastName: string }[] }>(
    'teilnehmer', '/auth/my-members/');
  for (const member of members.results) {
    if (!SAMPLE_MEMBERS.includes(`${member.firstName} ${member.lastName}`)) {
      await api('teilnehmer', 'DELETE', `/auth/my-members/${member.id}/`);
    }
  }
}

/**
 * Hält die Befunde eines Ablaufs fest und lässt den Test bei unerwarteten Fehlern scheitern.
 *
 * Erst festhalten, dann prüfen, damit `results/pages.jsonl` auch rote Abläufe
 * enthält (Vergleich vor und nach Updates, Fahrplan „Vorgehen für künftige Updates“).
 */
async function checkFindings(page: Page, testInfo: TestInfo, findings: Findings, expected: ExpectedError[]): Promise<void> {
  // Kurz weiter beobachten, damit nachgeladene Fehler noch dazukommen.
  await page.waitForTimeout(1_000);
  const entry = { page: `Ablauf: ${testInfo.title}`, account: testInfo.titlePath.at(-2), url: page.url(), ...findings };
  fs.appendFileSync(FINDINGS_FILE, `${JSON.stringify(entry)}\n`);
  await testInfo.attach('findings.json', { body: JSON.stringify(entry, null, 2), contentType: 'application/json' });
  expect(unexpectedErrors(findings.errors, expected), 'Fehler im Ablauf').toEqual([]);
}

// --- Neue Anmeldung --------------------------------------------------------------

test.describe('teilnehmer', () => {
  test.use({ storageState: storageStateFor('teilnehmer') });

  test.beforeEach(cleanUpParticipant);
  test.afterEach(cleanUpParticipant);

  test('Personen hinzufügen, ändern, umbenennen und löschen (#19, #23)', async ({ page }, testInfo) => {
    const findings = watchPage(page);
    await startRegistration(page);

    // #19: Eine schon angemeldete Person wird sofort gemeldet, nicht erst beim
    // Absenden. Die übrigen ausgewählten Personen werden trotzdem übernommen.
    await addMembers(page, ['Ben Probe', 'Mia Beispiel']);
    await expect(errorMessage(page)).toContainText('Mia Beispiel');
    await expect(errorMessage(page)).toContainText('bereits für diese Veranstaltung angemeldet');
    await expect.poll(() => personList(page)).toEqual([expect.stringMatching(/^Ben Probe/)]);

    // #23: Jede Person über „ändern“ öffnen, der Dialog zeigt die richtige.
    await addNewPerson(page, 'Ida', 'Probe', '2011-02-03');
    const dialog = page.getByRole('dialog');
    const row = (name: string) => stepContent(page).locator('li', { hasText: name });
    for (const firstName of ['Ben', 'Ida']) {
      await row(`${firstName} Probe`).getByText('ändern').click();
      await expect(field(dialog, 'Vorname*')).toHaveValue(firstName);
      await dialog.getByRole('button', { name: 'Abbrechen' }).click();
      await expect(dialog).toHaveCount(0);
    }

    // Umbenennen: Die Person steht danach genau einmal mit neuem Namen da. Beim
    // Bearbeiten ist sie keine Dublette ihrer selbst.
    await row('Ida Probe').getByText('ändern').click();
    await field(dialog, 'Vorname*').fill('Ina');
    await dialog.getByRole('button', { name: 'Speichern' }).click();
    await expect(dialog).toHaveCount(0);
    await expect.poll(async () => (await personList(page)).sort())
      .toEqual([expect.stringMatching(/^Ben Probe/), expect.stringMatching(/^Ina Probe/)]);

    // Vor #23 erschien eine neue Person nach dem Löschen erst nach dem Neuladen.
    await row('Ben Probe').getByText('löschen').click();
    await row('Ina Probe').getByText('löschen').click();
    await expect(stepContent(page).getByText('Noch keine Person')).toBeVisible();
    await addNewPerson(page, 'Ole', 'Probe', '2012-07-08');
    await expect.poll(() => personList(page)).toEqual([expect.stringMatching(/^Ole Probe/)]);

    await checkFindings(page, testInfo, findings, [
      registrationProbe(),
      {
        text: `Backend antwortet 400: POST /event/event/${ids.eventId}/check-person/`,
        issue: 'gewollt: Mia Beispiel ist schon angemeldet',
      },
    ]);
  });

  test('Ganzer Anmeldeablauf mit allen Schritten bis zum Absenden (#19, #25)', async ({ page }, testInfo) => {
    const findings = watchPage(page);
    await startRegistration(page);

    // #19: sich selbst und ein Stammesmitglied anmelden. Aus den eigenen Daten
    // fehlen Geburtstag und Adresse, die ergänzt man im Dialog.
    await page.getByRole('button', { name: 'Mich selbst anmelden' }).click();
    const dialog = page.getByRole('dialog');
    await expect(field(dialog, 'Vorname*')).toHaveValue('Tim');
    await field(dialog, 'Geburtstag*').fill('2000-03-15');
    await field(dialog, 'Straße und Hausnummer*').fill('Zeltweg 3');
    await field(dialog, 'Postleitzahl*').fill('10115');
    await dialog.getByRole('button', { name: 'Speichern' }).click();
    await expect(dialog).toHaveCount(0);
    await addMembers(page, ['Ben Probe']);
    await expect.poll(async () => (await personList(page)).sort())
      .toEqual([expect.stringMatching(/^Ben Probe/), expect.stringMatching(/^Tim Teilnehmer/)]);
    await next(page, /\/travel\//);

    // #25: Fehlt im Reise-Dialog eine Angabe, erscheint eine Meldung, und es wird
    // nichts übernommen.
    await page.getByRole('button', { name: 'Neuer Eintrag' }).click();
    await dialog.getByRole('button', { name: 'Speichern' }).click();
    await expect(errorMessage(page)).toContainText('Bitte Felder überprüfen');
    // Das Element mit der Rolle „dialog“ selbst hat keine Fläche, deshalb wird
    // geprüft, ob sein Inhalt noch zu sehen ist.
    await expect(field(dialog, 'Welcher Bahnhof')).toBeVisible();
    await dialog.getByRole('button', { name: 'Abbrechen' }).click();
    await expect(stepContent(page).getByText(/Person\/en mit/)).toHaveCount(0);
    await addTravel(page, 'Hauptbahnhof');
    await next(page, /\/travel-back\//);
    await addTravel(page, 'Bahnhof Nord');
    await next(page, /\/custom\//);

    await expect(stepContent(page).getByRole('heading', { name: 'T-Shirts' })).toBeVisible();
    await field(page, 'T-Shirt M').fill('2');
    await field(page, 'T-Shirt L').fill('1');
    await next(page, /\/letter\//);
    await field(page, 'Zusätzliche Nachricht').fill('Rauchtest: Wir bringen eine Jurte mit.');
    await next(page, /\/custom\//);
    await expect(stepContent(page).getByRole('heading', { name: 'Lunch Pakete' })).toBeVisible();
    await field(page, 'Lunch Pakete').fill('3');
    await next(page, /\/summary\//);

    // Über die Schrittanzeige von „Lunch Pakete“ zurück zu „T-Shirts“: Die
    // Antworten sind noch da (vor Issue #25 waren die Felder dort leer).
    await stepLink(page, 'LunchMeals').click();
    await expect(field(page, 'Lunch Pakete')).toHaveValue('3');
    await stepLink(page, 'Tshirts').click();
    await expect(field(page, 'T-Shirt M')).toHaveValue('2');
    await expect(field(page, 'T-Shirt L')).toHaveValue('1');
    await next(page, /\/letter\//);
    await expect(field(page, 'Zusätzliche Nachricht')).toHaveValue('Rauchtest: Wir bringen eine Jurte mit.');
    await next(page, /\/custom\//);
    await next(page, /\/summary\//);

    // Absenden
    await stepContent(page).getByRole('switch').click();
    await page.getByRole('button', { name: 'speichern' }).click();
    await page.waitForURL(/\/registration-finished\//);
    await expect(page.getByText('Deine Anmeldung ist erfolgreich abgeschlossen')).toBeVisible();

    // Alles, was eingegeben wurde, ist im Backend angekommen, auch die Antworten
    // der Schritte, über die zurückgesprungen wurde.
    const registrationId = new URL(page.url()).pathname.split('/').pop();
    const saved = await apiGet<RegistrationRead>('teilnehmer', `/event/registration-read/${registrationId}/`);
    expect(saved.scoutOrganisation.name).toBe('Falken');
    expect(saved.registrationparticipantSet.map((p) => `${p.firstName} ${p.lastName}`).sort())
      .toEqual(['Ben Probe', 'Tim Teilnehmer']);
    const answers = Object.fromEntries(saved.attributes.map((a) => [
      a.attributeModule.title, a.integerField ?? a.stringField ?? a.description,
    ]));
    expect(answers).toMatchObject({
      'T-Shirt M': 2,
      'T-Shirt L': 1,
      'Lunch Pakete': 3,
      'Zusätzliche Anmerkungen': 'Rauchtest: Wir bringen eine Jurte mit.',
      Anreise: 'Hauptbahnhof',
      Abreise: 'Bahnhof Nord',
    });

    await checkFindings(page, testInfo, findings, [registrationProbe()]);
  });
});

// --- Bestehende Anmeldung --------------------------------------------------------

test.describe('stammesleitung', () => {
  test.use({ storageState: storageStateFor('stammesleitung') });

  test('Gespeicherte Person unverändert speichern ohne Dublettenmeldung (#19)', async ({ page }, testInfo) => {
    const findings = watchPage(page);
    await page.goto(`/registrations-details/${ids.registrationId}`);
    await page.getByRole('button', { name: /^Mia Beispiel/ }).click();
    // Im aufgeklappten Eintrag: erst „bearbeiten“, dann „löschen“ (nur Symbole).
    await page.locator('dd', { hasText: 'Geburtsdatum' }).getByRole('button').first().click();
    const dialog = page.getByRole('dialog');
    await expect(field(dialog, 'Vorname*')).toHaveValue('Mia');
    // Mit einer Dublettenmeldung bliebe der Dialog offen.
    await dialog.getByRole('button', { name: 'Speichern' }).click();
    await expect(dialog).toHaveCount(0);
    await expect(page.getByRole('button', { name: /^Mia Beispiel/ })).toHaveCount(1);

    // Unverändert gespeichert heißt: Die Daten sind noch die aus load_sample_data,
    // auch der Geburtstag (er könnte sich durch Zeitzonen um einen Tag verschieben).
    // Feste Werte statt eines Vorher-Nachher-Vergleichs: Sonst gälte ein schon
    // verschobener Geburtstag beim nächsten Lauf als richtig. Scheitert der Test
    // hier, die Beispieldaten mit load_sample_data --reset neu anlegen.
    const saved = await apiGet<RegistrationRead>('stammesleitung', `/event/registration-read/${ids.registrationId}/`);
    const mia = saved.registrationparticipantSet.filter((p) => p.firstName === 'Mia');
    expect(mia).toHaveLength(1);
    expect(mia[0]).toMatchObject({ lastName: 'Beispiel', address: SAMPLE_ADDRESS });
    expect(new Date(mia[0].birthday).toLocaleDateString('de-DE', { timeZone: 'Europe/Berlin' })).toBe('4.5.2012');

    await checkFindings(page, testInfo, findings, [MEMBER_SEARCH_403]);
  });

  test('Ort, den eine fremde Veranstaltung nutzt: Fehlermeldung statt Neuladen (#20)', async ({ page }, testInfo) => {
    const trip = await apiGet<{ location: { id: number } }>('stammesleitung', `/event/event-read/${ids.tripEventId}/`);
    // Zurücksetzen als leitung: Sie gehört zum Anmeldeteam und darf jeden Ort
    // ändern. Gerade wenn die Sperre versagt, muss der Ort wieder stimmen.
    const restore = () => api('leitung', 'PATCH', `/event/event-location/${trip.location.id}/`, { address: SHARED_ADDRESS });
    await restore();
    try {
      const findings = watchPage(page);
      await page.goto(`/event-details/${ids.tripEventId}`);
      await page.waitForLoadState('networkidle');
      const addresses = watchAddresses(page);

      await locationEditButton(page).click();
      const dialog = page.getByRole('dialog');
      await field(dialog, 'Adresse des Veranstaltungortes').fill('Rauchtestweg 9');
      await dialog.getByRole('button', { name: 'Änderung speichern' }).click();
      await expect(errorMessage(page)).toContainText('Speichern fehlgeschlagen');
      // Das Formular bleibt mit der Eingabe offen, die Seite lädt nicht neu.
      await expect(field(dialog, 'Adresse des Veranstaltungortes')).toHaveValue('Rauchtestweg 9');
      expect(addresses, 'Seite hat neu geladen oder die Adresse gewechselt').toEqual([]);
      const after = await apiGet<{ location: { address: string } }>('stammesleitung', `/event/event-read/${ids.tripEventId}/`);
      expect(after.location.address).toBe(SHARED_ADDRESS);

      await checkFindings(page, testInfo, findings, [{
        text: `Backend antwortet 403: PUT /event/event-location/${trip.location.id}/`,
        issue: 'gewollt: Den Ort nutzt auch das fremde Lager',
      }]);
    } finally {
      await restore();
    }
  });
});

// --- Veranstaltung verwalten -----------------------------------------------------

/**
 * Sammelt die Adressen, die die Seite nacheinander anzeigt, auch ohne Neuladen.
 *
 * Vor Issue #20 sprang die Seite nach dem Speichern zu `/event-details/<Kennung
 * des Lagerbeitrags>`. Ob man danach dort hängen blieb oder das gleichzeitige
 * Neuladen wieder auf der Veranstaltung landete, hing vom Zufall ab. Deshalb
 * zählt jeder Zwischenstand, nicht nur das Ende.
 */
function watchAddresses(page: Page): string[] {
  const addresses: string[] = [];
  page.on('framenavigated', (frame) => {
    if (frame === page.mainFrame()) addresses.push(new URL(frame.url()).pathname);
  });
  return addresses;
}

/** Adressen einer Veranstaltungsseite, die nicht zu dieser Veranstaltung gehören. */
function foreignEventPages(addresses: string[], eventPage: string): string[] {
  return addresses.filter((address) => address.startsWith('/event-details/') && address !== eventPage);
}

/** Bearbeiten-Knopf beim Ort: Neben der Überschrift stehen „neuer Ort“ und „bearbeiten“, nur als Symbole. */
function locationEditButton(page: Page): Locator {
  return page.locator('h3', { hasText: 'Ort der Veranstaltung' }).locator('..').getByRole('button').nth(1);
}

/** Bereich „Buchungs Optionen“ der Veranstaltungsseite. */
function bookingSection(page: Page): Locator {
  return page.locator('h3', { hasText: 'Buchungs Optionen' }).locator('xpath=../../..');
}

interface BookingOption { id: number; name: string; price: string }

const TEST_OPTION = 'Rauchtest-Option';

/** Buchungsoptionen des Beispiellagers, gelesen als dessen Leitung. */
async function bookingOptions(): Promise<BookingOption[]> {
  return apiGet<BookingOption[]>('leitung', `/event/event/${ids.eventId}/booking-options/`);
}

/** Löscht die vom Test angelegte Buchungsoption, falls es sie gibt. */
async function deleteTestOption(): Promise<void> {
  for (const option of (await bookingOptions()).filter((o) => o.name === TEST_OPTION)) {
    await api('leitung', 'DELETE', `/event/event/${ids.eventId}/booking-options/${option.id}/`);
  }
}

test.describe('leitung', () => {
  test.use({ storageState: storageStateFor('leitung') });

  test('Lagerbeitrag ändern und anlegen, danach auf der Veranstaltung bleiben (#20)', async ({ page }, testInfo) => {
    const standard = (await bookingOptions()).find((o) => o.name === 'Standard');
    if (!standard) throw new Error('Buchungsoption „Standard“ des Beispiellagers fehlt');
    const restore = async () => {
      await api('leitung', 'PATCH', `/event/event/${ids.eventId}/booking-options/${standard.id}/`, { price: SAMPLE_PRICE });
      await deleteTestOption();
    };
    await restore();
    const eventPage = `/event-details/${ids.eventId}`;
    try {
      const findings = watchPage(page);
      const addresses = watchAddresses(page);
      await page.goto(eventPage);
      const dialog = page.getByRole('dialog');

      await bookingSection(page).locator('li', { hasText: 'Standard' }).getByRole('button').click();
      await dialog.locator('#price').fill('17');
      await dialog.getByRole('button', { name: 'Speichern' }).click();
      await expect(bookingSection(page)).toContainText('Standard - 17.00 €');
      await expect(dialog).toHaveCount(0);
      expect(new URL(page.url()).pathname).toBe(eventPage);

      await bookingSection(page).locator('h3').locator('..').getByRole('button').click();
      await field(dialog, 'Name des Buchungstyp*').fill(TEST_OPTION);
      await dialog.locator('#price').fill('9');
      await dialog.getByRole('button', { name: 'Speichern' }).click();
      await expect(bookingSection(page)).toContainText(`${TEST_OPTION} - 9.00 €`);
      await expect(dialog).toHaveCount(0);
      expect(new URL(page.url()).pathname).toBe(eventPage);
      expect(foreignEventPages(addresses, eventPage), 'Zwischendurch auf falscher Seite').toEqual([]);

      await checkFindings(page, testInfo, findings, []);
    } finally {
      await restore();
    }
  });

  test('Ort ändern, danach auf der Veranstaltung bleiben (#20)', async ({ page }, testInfo) => {
    const event = await apiGet<{ location: { id: number } }>('leitung', `/event/event-read/${ids.eventId}/`);
    const restore = () => api('leitung', 'PATCH', `/event/event-location/${event.location.id}/`, { address: SAMPLE_ADDRESS });
    await restore();
    const eventPage = `/event-details/${ids.eventId}`;
    try {
      const findings = watchPage(page);
      const addresses = watchAddresses(page);
      await page.goto(eventPage);
      await locationEditButton(page).click();
      const dialog = page.getByRole('dialog');
      await field(dialog, 'Adresse des Veranstaltungortes').fill('Rauchtestweg 5');
      await dialog.getByRole('button', { name: 'Änderung speichern' }).click();
      await expect(page.getByText('Rauchtestweg 5')).toBeVisible();
      await expect(dialog).toHaveCount(0);
      expect(new URL(page.url()).pathname).toBe(eventPage);
      expect(foreignEventPages(addresses, eventPage), 'Zwischendurch auf falscher Seite').toEqual([]);

      await checkFindings(page, testInfo, findings, []);
    } finally {
      await restore();
    }
  });
});
