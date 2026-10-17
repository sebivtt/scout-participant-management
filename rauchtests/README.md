# Rauchtests

Automatische Klicktests in einem echten Browser (Chromium, gesteuert von Playwright). Sie öffnen das Tool so, wie Nutzende es tun, und prüfen, ob es grob bricht. Gedacht vor allem als Sicherheitsnetz für Updates im Frontend. Aufbau und Gründe: `docs/entscheidungen.md`, Einträge „Rauchtests: Werkzeug und Aufbau“ (16.10.2026) und „Rauchtests: nur bei Bedarf auf GitHub“ (17.10.2026).

Die Tests laufen gegen das ganze Tool: Frontend, Backend und Keycloak 26.7, mit den Beispieldaten aus `python manage.py load_sample_data` und den drei Testkonten aus `dev/keycloak-setup.sh`.

Hilfsdateien: `findings.ts` sammelt die Fehler, `environment.ts` enthält Adressen und Testkonten, `api.ts` fragt das Backend ohne Browser, `global-setup.ts` meldet die Konten an und prüft, ob die Beispieldaten passen.

## Was geprüft wird

### Jede Seite lädt

`tests/seiten.spec.ts`: Jede Seite lädt ohne Programmfehler. Jede Seite wird einmal mit dem Testkonto geöffnet, das sie im Alltag nutzt. Ein Test scheitert, wenn

- im Browser ein Programmfehler oder eine Fehlermeldung auftritt,
- das Backend mit einem Fehler antwortet, auch mit einer Ablehnung (4xx),
- die Seite auf „Seite nicht gefunden“ oder auf der Anmeldung landet, bei einer Weiterleitung am falschen Ziel ankommt oder leer ist,
- eine Seite mit Login keine einzige Antwort vom Backend bekommt. Dann zeigt das Frontend auf eine andere Adresse als die Tests, und Fehler des Backends blieben unbemerkt.

Nach dem Laden beobachten die Tests noch eine Sekunde weiter, um nachgeladene Fehler zu erfassen.

Nur berichtet, ohne dass der Test scheitert, werden:

- Vue-Warnungen,
- Fehlermeldungen zu Dateien fremder Server, etwa Kartenkacheln und ein Lizenz-Logo. Ob die erreichbar sind, hängt vom Netz ab, in der Cloud-Sitzung sind sie gesperrt. Programmfehler zählen immer, auch wenn sie aus einer fremden Datei stammen.

**Bekannte Fehler** stehen bei ihrer Seite mit Issue-Nummer (`known`). Sie lassen den Test nicht scheitern. Tritt einer nicht mehr auf, scheitert der Test, damit die Markierung entfernt wird, wie `xfail(strict=True)` im Backend.

Grenzen:

- Nicht abgedeckt sind Seiten, die Daten brauchen, die es in den Beispieldaten nicht gibt: einzelne Aufgaben, Nachrichten und Benachrichtigungen und die Detailseite einer Person. Ebenso die Seiten der abgeschalteten Module und die Adressen `/registrations-details-statistic/…` und `/user/…`, auf die nirgends ein Link führt.
- „Seite ist leer“ greift kaum, weil Kopfzeile und Menü fast immer zu sehen sind. Ob der eigentliche Inhalt stimmt, prüfen die Tests zum Anmeldeablauf genauer.
- Ein bekannter Fehler gilt für alle Meldungen, die seinen Text enthalten, auch für eine andere Ablehnung derselben Adresse.

### Anmeldeablauf

`tests/anmeldeablauf.spec.ts` klickt ganze Abläufe durch und prüft danach über das Backend, was angekommen ist. Abgedeckt sind die Pflichtpunkte aus Fehlern, die nur durch Klicken auffielen (`docs/fahrplan.md`, „Vorarbeit für die Rauchtests“):

| Test | Konto | Was geprüft wird |
| --- | --- | --- |
| Personen hinzufügen, ändern, umbenennen und löschen | `teilnehmer` | Eine schon angemeldete Person wird sofort gemeldet (#19). Zwei Personen über „ändern“ öffnen, eine umbenennen, beide löschen, eine neue hinzufügen (#23). |
| Ganzer Anmeldeablauf bis zum Absenden | `teilnehmer` | „Mich selbst anmelden“ und ein Stammesmitglied (#19), alle Schritte der Standardvorlage, Reise-Dialog mit fehlender Angabe (#25), über die Schrittanzeige von „Lunch Pakete“ zurück zu „T-Shirts“. Danach im Backend: alle Personen und Antworten sind angekommen. |
| Gespeicherte Person unverändert speichern | `stammesleitung` | Keine Dublettenmeldung, die Daten bleiben gleich (#19). |
| Fremder Ort | `stammesleitung` | Einen Ort, den auch eine fremde Veranstaltung nutzt, ändern: Fehlermeldung, die Seite lädt nicht neu (#20). |
| Lagerbeitrag ändern und anlegen | `leitung` | Danach auf der Veranstaltung bleiben, auch zwischendurch nicht auf eine andere Adresse springen (#20). |
| Ort ändern | `leitung` | Ebenso (#20). |
| Fenster am Handy | `teilnehmer` | Personen- und Reise-Fenster stehen am unteren Rand und der Hintergrund deckt den Bildschirm ab (#37). Am Laptop prüfen der ganze Anmeldeablauf und „unverändert speichern“ zusätzlich, dass die Fenster mittig stehen. |

Fehler zählen wie bei den Seiten. Erwartete Fehler stehen beim Test, mit Issue oder Grund, z. B. die gewollte Ablehnung beim fremden Ort. Sie müssen auftreten, sonst scheitert der Test. Damit fällt auch auf, wenn eine Prüfung im Backend nicht mehr greift.

**Aufräumen:** Was die Tests im Backend anlegen oder ändern (die neue Anmeldung, Lagerbeiträge, Adressen), setzen sie vor und nach jedem Test auf die Werte aus `load_sample_data` zurück, auch wenn sie unterwegs scheitern oder ein früherer Lauf abgebrochen wurde. Die Beispieldaten bleiben so bei jedem Lauf gleich. Einzige Ausnahme: Verändert das unveränderte Speichern einer Person ihre Daten (der Fehler, den der Test sucht), bleibt der Test rot, bis die Beispieldaten mit `python manage.py load_sample_data --reset` neu angelegt sind.

Die Tests laufen mit deutscher Zeitzone, wie bei Nutzenden. Sonst zeigt der Browser Geburtstage einen Tag zu früh an.

Grenzen:

- Geprüft wird mit Chromium, nicht mit Safari. Der Fehler aus #20 trat nur manchmal auf (die Seite sprang zur falschen Adresse und lud gleichzeitig neu). Deshalb zählt jede Adresse, die die Seite zwischendurch zeigt.
- Die Tests sind nachgeprüft: Mit den alten, fehlerhaften Fassungen der Behebungen von #19, #20, #23 und #25 scheitern sie. Wie das geprüft wurde, steht in PR #62.

## Starten

Voraussetzung: Das Tool läuft mit Beispieldaten (`docs/lokal-starten.md`, auf dem Mac; in der Cloud-Sitzung `docs/arbeitsumgebung.md`).

```bash
cd rauchtests
yarn install --frozen-lockfile
npx playwright install chromium   # nur auf dem Mac nötig, in der Cloud-Sitzung ist Chromium vorhanden
yarn test
```

Ein Lauf dauert knapp 4 Minuten. Am Ende steht „56 passed“ oder eine Liste der gescheiterten Seiten und Abläufe. Einzelne Seiten oder Abläufe: `yarn test -g "Auswertung"`, nur der Anmeldeablauf: `yarn test tests/anmeldeablauf.spec.ts`.

Beispieldaten von vor dem 17.10.2026 passen nicht zu den Tests zum Anmeldeablauf. Die Einrichtung meldet das und nennt die Befehle, Anleitung in `docs/lokal-starten.md`, Teil 2.

Andere Adressen als `localhost` lassen sich über die Umgebungsvariablen `FRONTEND_URL`, `BACKEND_URL` und `KEYCLOAK_URL` einstellen.

## Ergebnisse lesen

- `playwright-report/index.html`: Bericht mit Bildschirmfoto und Ablaufaufzeichnung je gescheiterter Seite. Öffnen mit `npx playwright show-report`.
- `results/pages.jsonl`: alle Befunde, eine Zeile je Seite und je Ablauf (Name beginnt mit „Ablauf:“), auch Vue-Warnungen und bekannte Fehler. Bei Updates die Datei nach einem vollständigen Lauf vor dem Update beiseitelegen und mit der Fassung nach dem Update vergleichen (`docs/fahrplan.md`, „Vorgehen für künftige Updates“). Jeder Lauf legt sie neu an, auch einer mit `-g`.

Beide Ordner und die gespeicherten Anmeldungen (`.auth/`) stehen in `.gitignore`.

## Auf GitHub

`.github/workflows/rauchtests.yml` startet das ganze Tool und die Rauchtests, wenn ein Pull Request das Label `rauchtests` trägt, oder von Hand unter „Actions“ → „Rauchtests“ → „Run workflow“. Ein Lauf dauert gut 6,5 Minuten, abgerechnet werden 7 Minuten. Solange das Label gesetzt ist, läuft er bei jedem neuen Stand des Pull Requests erneut. Das Label also erst setzen, wenn der Pull Request fertig ist, oder nach dem Lauf wieder entfernen. Der Bericht liegt danach beim Lauf unter „Artifacts“. Ein rotes Ergebnis sperrt die Übernahme nicht (`docs/fahrplan.md`, „Regeln für die Reihenfolge“).
