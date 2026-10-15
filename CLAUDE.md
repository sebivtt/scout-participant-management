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

## Was du nicht tun sollst

- Keine Änderungen am gemeinsamen Verbands-Keycloak voraussetzen (z. B. veraltete Feature-Flags). Das Tool muss mit der Standard-Konfiguration von Keycloak laufen.
- Bekannte Fehler nicht stillschweigend „mitbeheben“, ohne Test und ohne Erwähnung im Pull Request.
- `# noqa` nicht für neuen Code verwenden. Die bestehenden Markierungen sind Altlasten.
- Keine echten Personendaten in Tests, Beispieldaten oder Logs.
