# Hinweise für KI-Assistenten

Dieses Projekt wird überwiegend mit KI entwickelt. Der Projektverantwortliche ist kein Programmierer und kann Code nicht im Detail prüfen. Deshalb gilt: **Nachvollziehbarkeit vor Geschwindigkeit.**

## Verbindliche Regeln

Lies und befolge `CONTRIBUTING.md`. Kurzfassung:

- Code-Namen auf Englisch, alle Erklärungen auf Deutsch
- Kommentare erklären das Warum
- Docstrings für neue und geänderte öffentliche Funktionen
- Jede fachliche Regel und jeder behobene Fehler bekommt einen Test
- Komplexität höchstens 12
- Keine N+1-Abfragen
- Neue Pakete nur mit Begründung
- Die Pfadfinderregel: geänderte Stellen besser hinterlassen

## Vor jeder Änderung

1. Stand, nächste Schritte und bekannte Anforderungen: `docs/fahrplan.md`. Erledigte Punkte dort abhaken. Neue Fehler und Anforderungen als Issue auf GitHub anlegen, mit dem Skill `issue-anlegen` (Vorlagen in `.github/ISSUE_TEMPLATE/`, Prüfung auf Abhängigkeiten), nicht im Fahrplan. Das gilt auch für Fehler, die die KI selbst findet.
2. Fachliche Regeln stehen in `docs/entscheidungen.md`. Widerspricht eine Anfrage einer dort festgehaltenen Entscheidung, frag nach, statt sie still zu ändern.
3. Begriffe: `docs/glossar.md`. Aufbau des Systems: `docs/architektur.md`.

## Arbeitsweise

- **Issues erst klären, dann umsetzen** (Entscheidung vom 16.10.2026):
  - Neue Issues mit dem Skill `issue-anlegen` (`.claude/skills/issue-anlegen/`) anlegen. Er prüft auch die Abhängigkeiten zu offenen Issues.
  - Was als Nächstes kommt, bestimmt allein die Reihenfolge in `docs/fahrplan.md` (Entscheidung vom 16.10.2026). Ein Issue mit Label `geklärt` ist fertig geklärt, aber erst dran, wenn es dort an der Reihe ist.
  - Umgesetzt wird nur ein Issue mit dem Label `geklärt`. Das Label setzt der Skill `grill-me` (`.claude/skills/grill-me/`), nachdem Sebastian Frage für Frage ausgefragt wurde und zugestimmt hat. Fehlt es, zuerst `grill-me` anbieten.
  - Direkt vor dem Start die Abhängigkeiten erneut prüfen. Ist ein blockierendes Issue noch offen, nicht anfangen.
  - Ein Issue = ein Pull Request mit eigenem Test, der Reihe nach (je Strang, siehe `docs/fahrplan.md`). Taucht beim Umsetzen eine fachliche Frage auf, anhalten, fragen und die Antwort ins Issue übernehmen.
- **Erst einen Test schreiben, der das Problem zeigt**, dann beheben.
- Lokale Prüfung vor jedem Commit, im Ordner `backend/`:
  ```bash
  ruff check . && pytest
  ```
- Vor jedem Pull Request, der Code ändert: Rauchtests in der Cloud-Sitzung laufen lassen (`rauchtests/README.md`) und das Ergebnis in die Beschreibung schreiben. Ob der Pull Request das Label `rauchtests` für den Lauf auf GitHub bekommt, im Einzelfall entscheiden und begründen (Entscheidung vom 17.10.2026). Riskante Updates bekommen es immer.
- Änderungen an Keycloak-Anbindung oder Rechten zusätzlich gegen ein echtes Keycloak 26.7 testen (siehe `dev/`, in der Cloud-Sitzung `docs/arbeitsumgebung.md`), nicht nur gegen den Test-Ersatz.
- **Unabhängige Prüfung vor jedem Pull Request:** Eine zweite KI-Instanz ohne Kenntnis des bisherigen Gesprächs prüft den Diff gegen `CONTRIBUTING.md` und auf Fehler. Ihre Befunde werden behoben oder im Pull Request begründet.
- Pull-Request-Beschreibung nach `CONTRIBUTING.md` Abschnitt 6, für Nicht-Programmierer verständlich.
- Neue Entscheidungen des Projektverantwortlichen in `docs/entscheidungen.md` eintragen, mit Datum.

## Erfahrungen aus früheren Sitzungen

Diese Fehler sind tatsächlich passiert. Sie wiederholen sich leicht.

- **Nutzt das Frontend eine Adresse?** Nicht per Textsuche nach dem vollständigen Pfad entscheiden. Das Frontend setzt Pfade aus Bausteinen zusammen (`${SERVICE}-read`). Stattdessen `backend/tools/frontend_aufrufe.py` bzw. `docs/schnittstellen.md` nutzen und Store-Aktionen und Importe bis zur aufrufenden Seite verfolgen. Fast wäre so eine Adresse entfernt worden, über die fast alle Veranstaltungsseiten laden.
- **Rechte enger ziehen** heißt immer auch Gegenproben: Darf die Veranstaltungsleitung weiterhin alles, auch wenn sie nur über die Leitungsgruppe (`admin_group`) Leitung ist? Darf die anmeldende Leitung vor der Frist ändern?
- **Zugehörigkeit aus der Adresse:** Felder wie `event` oder `registration` im Inhalt einer Anfrage nie übernehmen. Viele Serializer geben mit `fields = '__all__'` alle Felder frei.
- **Tests gegen den alten Stand prüfen:** Ein Test zu einem behobenen Fehler muss ohne die Behebung fehlschlagen. Das ist mit `git worktree add <pfad> HEAD~1` schnell nachgeprüft. Einmal bestand ein Test auch ohne Behebung, weil er die falsche Adresse aufrief.
- **Die unabhängige Prüfung findet fast immer etwas.** Ihren Auftrag eng fassen (nur den Diff, konkrete Prüfpunkte), Befunde selbst nachprüfen, dann beheben. Bricht sie ab (z. B. Nutzungslimit), sie fortsetzen statt neu zu starten.
- **Zahlen in der Doku nachrechnen,** bevor sie im Pull Request stehen: `backend/tools/qualitaet_messen.py` und eigene Zählungen. Falsche Zahlen fielen mehrfach erst in der Prüfung auf.
- **Eine Adresse, mehrere Aufrufer, verschiedene Kennungen:** Dieselbe Komponente steckt oft in mehreren Seiten, und `route.params.id` bedeutet dort Verschiedenes, z. B. im Dialog „Person hinzufügen“ einmal die Veranstaltung (neue Anmeldung), einmal die Anmeldung (bestehende). PR #3 zog die Rechte der Personenprüfung auf „Anmeldung“ enger, ohne alle Aufrufer zu verfolgen, und machte damit jede neue Anmeldung unmöglich (Issue #19). Vor jeder Änderung an Rechten oder Kennungen einer Adresse alle Seiten verfolgen, die sie aufrufen, und klären, welche Kennung dort in der Adresse steht.
- **Erst gründlich nachsehen, dann „geht nicht“ festhalten:** Am 15.10. stand im Fahrplan, in der Cloud-Sitzung gebe es keinen Browser. Gesucht wurde nur mit `which` und im üblichen Zwischenspeicher, dabei liegt Chromium unter `/opt/pw-browsers` (Umgebungsvariable `PLAYWRIGHT_BROWSERS_PATH`). Die falsche Annahme hätte fast die Planung der Rauchtests bestimmt. Fehler im Frontend lassen sich so im Browser nachstellen, statt sie aus dem Code zu erraten (Issue #23). Am 16.10. dasselbe noch einmal: „Keycloak in der Cloud gesperrt“ galt nur für die Docker-Abbilder, das Programmpaket von GitHub läuft (`docs/arbeitsumgebung.md`). Eine Sperre also für jeden Bezugsweg einzeln prüfen, bevor sie festgehalten wird.
- **Erst alles hochladen, dann den Link schicken.** Sebastian übernimmt einen Pull Request oft gleich, nachdem er den Link bekommen hat. Bei PR #62 kam ein letzter Commit danach und landete deshalb erst mit PR #65 in `main`. Also vor dem Link prüfen, dass der Branch auf GitHub vollständig ist: `git rev-parse HEAD` und `git ls-remote origin <branch>` müssen dieselbe Kennung zeigen. `git status -sb` genügt nicht, weil es ohne Verknüpfung zum Branch auf GitHub (in der flachen Kopie der Cloud-Sitzung häufig) nie „ahead“ anzeigt. Danach nichts mehr nachschieben. Fällt doch noch etwas auf, Sebastian vorher Bescheid geben.
- **Eingabefelder auch wie am Handy prüfen.** Beim Update auf Quill 2 (PR #68) tippte der eigene Rauchtest nur wie am Laptop und war grün. Erst die unabhängige Prüfung fand, dass bei Handy-Tastaturen (Komposition, also Autokorrektur und Wortvorschläge) der Text mitten im Tippen verschwand: `components/field/Base.vue` hängt `@input` an jedes Feld und übernimmt `event.target.value`, bei Bausteinen ohne eigenes `input`-Ereignis landet das auf dem äußeren Rahmen. Bei Änderungen an Eingabefeldern deshalb auch eine Eingabe mit Komposition nachstellen (in Playwright über `Input.imeSetComposition`, Vorbild im Rauchtest „Texteditor: Handy-Tastatur und Link-Fenster …“).
- **Pull Requests nicht aufeinander aufbauen.** Ein auf einen anderen PR aufgebauter PR landete nach der Übernahme im falschen Branch.

## Was du nicht tun sollst

- Keine Änderungen am gemeinsamen Verbands-Keycloak voraussetzen (z. B. veraltete Feature-Flags). Das Tool muss mit der Standard-Konfiguration von Keycloak laufen.
- Bekannte Fehler nicht stillschweigend „mitbeheben“, ohne Test und ohne Erwähnung im Pull Request.
- `# noqa` nicht für neuen Code verwenden. Die bestehenden Markierungen sind Altlasten. Einzige Ausnahme sind gewollte Markierungen mit Begründung und Test (`CONTRIBUTING.md`, Abschnitt Altlasten).
- Keine echten Personendaten in Tests, Beispieldaten oder Logs.
