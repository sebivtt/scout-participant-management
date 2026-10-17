// Sammelt alles, was beim Öffnen einer Seite schiefgeht: Programmfehler im
// Browser, Antworten des Backends mit Fehlerstatus, gescheiterte Anfragen und
// Vue-Warnungen.
import type { Page } from '@playwright/test';
import { BACKEND_URL, FRONTEND_URL, KEYCLOAK_URL } from './environment';

export interface Findings {
  /** Lassen den Test scheitern. */
  errors: string[];
  /** Werden nur berichtet: Vue-Warnungen und Fehlermeldungen zu Dateien fremder Server. */
  notes: string[];
  /** Zahl der Antworten vom Backend. Bleibt sie 0, passt BACKEND_URL nicht zum Frontend. */
  backendResponses: number;
}

/** Gehört die Adresse zum Tool selbst (Frontend, Backend, Keycloak)? */
function isOwnAddress(url: string): boolean {
  return [FRONTEND_URL, BACKEND_URL, KEYCLOAK_URL].some((own) => url.startsWith(`${own}/`) || url === own);
}

function isBackend(url: string): boolean {
  return url.startsWith(`${BACKEND_URL}/`);
}

/** Hängt die Beobachter an eine Seite. Das Ergebnis füllt sich, während die Seite lädt. */
export function watchPage(page: Page): Findings {
  const findings: Findings = { errors: [], notes: [], backendResponses: 0 };
  const record = (message: string) => findings.errors.push(message);

  page.on('pageerror', (error) => record(`Programmfehler: ${error.message}`));
  page.on('console', (message) => {
    const text = message.text();
    const source = message.location().url ?? '';
    if (message.type() === 'warning' && text.includes('[Vue warn]')) {
      findings.notes.push(`Vue-Warnung: ${text.split('\n')[0].slice(0, 300)}`);
    }
    if (message.type() !== 'error') return;
    // Fehlgeschlagene Anfragen ans Backend meldet der Beobachter für Antworten
    // genauer (mit Anfrageart und Status), hier nicht noch einmal.
    if (isBackend(source) && text.startsWith('Failed to load resource')) return;
    // „Failed to load resource“ nennt die Adresse nicht selbst, ohne sie ließe
    // sich ein roter Test nicht nachvollziehen.
    const line = `Fehlermeldung im Browser: ${text.slice(0, 300)}${source ? ` (${source})` : ''}`;
    // Dateien fremder Server (Kartenkacheln, Lizenz-Logo) gehören nicht zum Tool.
    // Ob sie erreichbar sind, hängt vom Netz ab, in der Cloud-Sitzung sind sie gesperrt.
    if (source && !isOwnAddress(source)) findings.notes.push(`Fremder Server: ${line}`);
    else record(line);
  });
  page.on('response', (response) => {
    if (!isBackend(response.url())) return;
    findings.backendResponses += 1;
    if (response.status() < 400) return;
    // Auch abgelehnte Anfragen (4xx) zählen als Fehler: Eine Seite, die beim Laden
    // etwas anfragt, das sie nicht darf, zeigt meist leere Felder oder Listen.
    // Ist eine Ablehnung bekannt, steht sie mit Issue bei der Seite (tests/seiten.spec.ts).
    record(`Backend antwortet ${response.status()}: ${response.request().method()} ${response.url().slice(BACKEND_URL.length)}`);
  });
  page.on('requestfailed', (request) => {
    if (!isBackend(request.url())) return;
    // Bricht der Browser eine Anfrage ab, weil man die Seite schon verlassen hat,
    // ist das kein Fehler des Tools.
    if (request.failure()?.errorText === 'net::ERR_ABORTED') return;
    record(`Anfrage gescheitert: ${request.method()} ${request.url()} (${request.failure()?.errorText})`);
  });
  return findings;
}

/** Ein Fehler, der auftreten muss: bekannt mit Issue oder an dieser Stelle gewollt (z. B. eine Ablehnung). */
export interface ExpectedError {
  /** Teil der Meldung, an dem der Fehler zu erkennen ist. */
  text: string;
  /** Issue-Nummer eines bekannten Fehlers oder Grund, warum er gewollt ist. */
  issue: string;
}

/**
 * Sortiert erwartete Fehler aus und liefert die übrigen.
 *
 * Jeder erwartete Fehler muss mindestens einmal auftreten, sonst wird das als
 * eigener Befund zurückgegeben: Ein behobener bekannter Fehler soll seine
 * Markierung verlieren (wie xfail(strict=True) im Backend), und eine gewollte
 * Ablehnung, die ausbleibt, heißt, dass die Prüfung im Backend nicht mehr greift.
 */
export function unexpectedErrors(errors: string[], expected: ExpectedError[]): string[] {
  let remaining = errors;
  const missing: string[] = [];
  for (const item of expected) {
    if (!remaining.some((error) => error.includes(item.text))) {
      missing.push(`Erwarteter Fehler (${item.issue}) tritt nicht mehr auf: ${item.text}`);
    }
    remaining = remaining.filter((error) => !error.includes(item.text));
  }
  return [...missing, ...remaining];
}
