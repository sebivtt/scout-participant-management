// Einstellungen der Rauchtests. Was sie prüfen und wie man sie startet: README.md in diesem Ordner.
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  globalSetup: './global-setup.ts',
  // Seiten nacheinander statt gleichzeitig: Das Backend läuft im Entwicklungsmodus
  // mit einem einzigen Prozess. Gleichzeitige Aufrufe würden Zeitüberschreitungen
  // erzeugen, die wie Fehler im Tool aussehen.
  workers: 1,
  timeout: 60_000,
  // Kein automatischer zweiter Versuch: Ein Fehler, der nur manchmal auftritt,
  // soll sichtbar werden und nicht im zweiten Versuch verschwinden.
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.FRONTEND_URL ?? 'http://localhost:8080',
    ...devices['Desktop Chrome'],
    locale: 'de-DE',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
});
