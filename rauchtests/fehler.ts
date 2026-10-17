// Sammelt alles, was beim Öffnen einer Seite schiefgeht: Programmfehler im
// Browser, Serverfehler des Backends, abgebrochene Anfragen und Vue-Warnungen.
import type { Page } from '@playwright/test';
import { BACKEND_URL, FRONTEND_URL, KEYCLOAK_URL } from './umgebung';

export interface Findings {
  /** Lassen den Test scheitern. */
  errors: string[];
  /** Werden nur berichtet: Vue-Warnungen und Fehler fremder Server. */
  notes: string[];
}

/** Gehört die Adresse zum Tool selbst (Frontend, Backend, Keycloak)? */
function isOwnAddress(url: string): boolean {
  return [FRONTEND_URL, BACKEND_URL, KEYCLOAK_URL].some((own) => url.startsWith(own));
}

/** Hängt die Beobachter an eine Seite. Das Ergebnis füllt sich, während die Seite lädt. */
export function watchPage(page: Page): Findings {
  const findings: Findings = { errors: [], notes: [] };
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
    if (source.startsWith(BACKEND_URL) && text.startsWith('Failed to load resource')) return;
    // „Failed to load resource“ nennt die Adresse nicht selbst, ohne sie ließe
    // sich ein roter Test nicht nachvollziehen.
    const line = `Fehlermeldung im Browser: ${text.slice(0, 300)}${source ? ` (${source})` : ''}`;
    // Bilder fremder Server (Kartenkacheln, Lizenz-Logo) gehören nicht zum Tool.
    // Ob sie erreichbar sind, hängt vom Netz ab, in der Cloud-Sitzung sind sie gesperrt.
    if (source && !isOwnAddress(source)) findings.notes.push(`Fremder Server: ${line}`);
    else record(line);
  });
  page.on('response', (response) => {
    if (!response.url().startsWith(BACKEND_URL) || response.status() < 400) return;
    // Auch abgelehnte Anfragen (4xx) zählen als Fehler: Eine Seite, die beim Laden
    // etwas anfragt, das sie nicht darf, zeigt meist leere Felder oder Listen.
    // Ist eine Ablehnung bekannt, steht sie mit Issue bei der Seite (tests/seiten.spec.ts).
    record(`Backend antwortet ${response.status()}: ${response.request().method()} ${response.url().slice(BACKEND_URL.length)}`);
  });
  page.on('requestfailed', (request) => {
    if (!request.url().startsWith(BACKEND_URL)) return;
    // Bricht der Browser eine Anfrage ab, weil man die Seite schon verlassen hat,
    // ist das kein Fehler des Tools.
    if (request.failure()?.errorText === 'net::ERR_ABORTED') return;
    record(`Anfrage gescheitert: ${request.method()} ${request.url()} (${request.failure()?.errorText})`);
  });
  return findings;
}
