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

1. Stand, nächste Schritte und bekannte Anforderungen: `docs/fahrplan.md`. Erledigte Punkte dort abhaken, neue ergänzen.
2. Fachliche Regeln stehen in `docs/entscheidungen.md`. Widerspricht eine Anfrage einer dort festgehaltenen Entscheidung, frag nach, statt sie still zu ändern.
3. Begriffe: `docs/glossar.md`. Aufbau des Systems: `docs/architektur.md`.

## Arbeitsweise

- **Erst einen Test schreiben, der das Problem zeigt**, dann beheben.
- Lokale Prüfung vor jedem Commit, im Ordner `backend/`:
  ```bash
  ruff check . && pytest
  ```
- Änderungen an Keycloak-Anbindung oder Rechten zusätzlich gegen ein echtes Keycloak 26.7 testen (siehe `dev/`), nicht nur gegen den Test-Ersatz.
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
- **Pull Requests nicht aufeinander aufbauen.** Ein auf einen anderen PR aufgebauter PR landete nach der Übernahme im falschen Branch.

## Was du nicht tun sollst

- Keine Änderungen am gemeinsamen Verbands-Keycloak voraussetzen (z. B. veraltete Feature-Flags). Das Tool muss mit der Standard-Konfiguration von Keycloak laufen.
- Bekannte Fehler nicht stillschweigend „mitbeheben“, ohne Test und ohne Erwähnung im Pull Request.
- `# noqa` nicht für neuen Code verwenden. Die bestehenden Markierungen sind Altlasten. Einzige Ausnahme sind gewollte Markierungen mit Begründung und Test (`CONTRIBUTING.md`, Abschnitt Altlasten).
- Keine echten Personendaten in Tests, Beispieldaten oder Logs.
