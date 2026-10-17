// Adressen, Testkonten und Ablageorte, die alle Rauchtests gemeinsam nutzen.
import path from 'node:path';

export const FRONTEND_URL = process.env.FRONTEND_URL ?? 'http://localhost:8080';
export const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';
export const KEYCLOAK_URL = process.env.KEYCLOAK_URL ?? 'http://localhost:8180';
export const REALM = process.env.KEYCLOAK_REALM ?? 'dpv';

// Die Testkonten aus dev/keycloak-setup.sh. Ihre Rollen im Beispiellager legt
// `python manage.py load_sample_data` fest (docs/lokal-starten.md).
export const ACCOUNTS = {
  leitung: { password: 'leitung123' },
  stammesleitung: { password: 'stamm123' },
  teilnehmer: { password: 'teilnehmer123' },
} as const;

export type AccountName = keyof typeof ACCOUNTS;

// Hier legt die Einrichtung die Anmeldungen und Kennungen ab. Der Ordner steht
// in .gitignore, denn er enthält gültige Anmeldedaten der laufenden Sitzung.
export const STATE_DIR = path.join(__dirname, '.anmeldung');

export function storageStateFor(account: AccountName): string {
  return path.join(STATE_DIR, `${account}.json`);
}

export const IDS_FILE = path.join(STATE_DIR, 'kennungen.json');

// Befunde aller Seiten eines Laufs, eine Zeile je Seite. Wird bei jedem Lauf neu
// angelegt. Zum Vergleich vor und nach einem Update die Datei beiseitelegen.
export const FINDINGS_FILE = path.join(__dirname, 'ergebnisse', 'seiten.jsonl');

/** Kennungen der Beispieldaten, ermittelt in global-setup.ts. */
export interface SampleIds {
  eventId: string;
  registrationId: string;
  groupId: string;
}
