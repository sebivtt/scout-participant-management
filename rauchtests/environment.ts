// Adressen, Testkonten und Ablageorte, die alle Rauchtests gemeinsam nutzen.
import path from 'node:path';

/**
 * Liest eine Adresse aus der Umgebung und entfernt einen Schrägstrich am Ende.
 * `dev/frontend.env.example` schreibt Keycloak mit Schrägstrich. Ohne das
 * Entfernen entstünden Adressen wie `…8180//realms`, und der Vergleich, ob eine
 * Anfrage zum Tool gehört, ginge ins Leere.
 */
function address(name: string, fallback: string): string {
  return (process.env[name] ?? fallback).replace(/\/+$/, '');
}

export const FRONTEND_URL = address('FRONTEND_URL', 'http://localhost:8080');
export const BACKEND_URL = address('BACKEND_URL', 'http://localhost:8000');
export const KEYCLOAK_URL = address('KEYCLOAK_URL', 'http://localhost:8180');
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
export const AUTH_DIR = path.join(__dirname, '.auth');

export function storageStateFor(account: AccountName): string {
  return path.join(AUTH_DIR, `${account}.json`);
}

export const IDS_FILE = path.join(AUTH_DIR, 'sample-ids.json');

// Befunde aller Seiten eines Laufs, eine Zeile je Seite. Wird bei jedem Lauf neu
// angelegt, auch bei einem Lauf mit nur einzelnen Seiten (-g). Zum Vergleich
// vor und nach einem Update die Datei nach einem vollständigen Lauf beiseitelegen.
export const FINDINGS_FILE = path.join(__dirname, 'results', 'pages.jsonl');

/** Kennungen der Beispieldaten, ermittelt in global-setup.ts. */
export interface SampleIds {
  eventId: string;
  registrationId: string;
  groupId: string;
}
