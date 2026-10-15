# Entscheidungen

Fachliche und technische Entscheidungen mit Begründung. Neue Einträge oben. Wer eine Regel ändern will, ergänzt einen neuen Eintrag, statt einen alten zu überschreiben.

Format: Datum · Entscheidung · Begründung · Umsetzung

---

## 2026-10-15 · Regeln für Ausnahmen und bekannte Fehler

**Entscheidung:**
- `# noqa` nur mit Regelnummer. Pauschale und überflüssige Markierungen meldet ruff.
- Gewollte Markierungen (nötig, keine Altlast) tragen hinter der Regelnummer nach `--` eine Begründung und haben einen Test, der anschlägt, wenn die Zeile fehlt.
- Bekannte Fehler werden als `xfail(strict=True, raises=...)` mit genau der erwarteten Fehlerart festgehalten.

**Begründung:** Eine Markierung ohne Regelnummer schaltet auf ihrer Zeile auch Prüfungen ab, die erst später eingeschaltet werden, und versteckt so neue Funde. Ohne `raises` gälte jeder beliebige Fehler als „bekannt“. Ohne Begründung und Test lässt sich nicht erkennen, ob eine Markierung nötig ist: Ein scheinbar überflüssiger Import meldet zum Beispiel den Keycloak-Abgleich bei Celery an.
**Umsetzung:** `CONTRIBUTING.md` (Abschnitte 3 und Altlasten), `backend/ruff.toml` (PGH004, RUF100), `tests/test_signale.py` (PR #9)

## 2026-10-15 · Vorgehen bei der KI-Fehlerprüfung (Qualität II)

**Entscheidung:**
- Probleme, die schon für Phase 4 geplant sind (z. B. Absenden in Einzelschritten, „bestätigt“ wird nie gesetzt, feste Fehlermeldungen), werden in Qualität II nur als Test festgehalten, der sie als bekannten Fehler markiert. Behoben werden sie in Phase 4. Neu gefundene kleine Fehler werden sofort behoben, jeweils mit Test.
- Prüftiefe nach Modul: Automatische Prüfungen und die Sicherheitsprüfung von Hand (offene Adressen, Datenfreigabe, Rechte) laufen über den gesamten Code. Fachliche Randfälle und Fehlerbehandlung werden von Hand nur in den aktiven Modulen geprüft, nicht in den eingefrorenen (`food`, `inspi`, `messaging`, `notifications`).
- Funde in eingefrorenen Modulen werden in `docs/qualitaet.md` festgehalten, aber nicht behoben. Ausnahme: Sicherheitslücken werden sofort behoben, mit Test.

**Begründung:** Die Prüfung soll vollständig dokumentiert sein, ohne Aufwand in Code zu stecken, der derzeit nicht weiterentwickelt wird. Die eingefrorenen Module sind aber über eigene Adressen im Internet erreichbar, das Kontaktformular sogar ohne Login. Sicherheitslücken dort treffen deshalb das ganze Tool.
**Umsetzung:** `docs/fahrplan.md` Abschnitt „Qualität II“. Ob die eingefrorenen Module behalten oder entfernt werden, bleibt offen (siehe Fahrplan, offene Punkte).

## 2026-10-15 · Entwicklungsregeln und Qualitätsprüfungen

**Entscheidung:** Für alle Änderungen gelten die Regeln in `CONTRIBUTING.md`. GitHub prüft automatisch Stil, Komplexität, Tests, Migrationen und Sicherheitslücken. Vor jedem Pull Request prüft eine unabhängige KI-Instanz die Änderung.
**Begründung:** Der Code entsteht überwiegend mit KI, und der Projektverantwortliche kann ihn nicht im Detail prüfen. Die Qualität soll deshalb durch Mechanismen gesichert werden, nicht durch Vertrauen.
**Umsetzung:** `CONTRIBUTING.md`, `CLAUDE.md`, `backend/ruff.toml`, `.github/workflows/ci.yml`

## 2026-10-15 · Sprache im Code

**Entscheidung:** Englische Namen im Code, deutsche Erklärungen (Kommentare, Docstrings, Dokumentation, Pull Requests).
**Begründung:** Der übernommene Code ist englisch benannt. Die Erklärungen sollen für alle im Verband lesbar sein.

## 2026-10-14 · Fristen

**Entscheidung:**
- Der offizielle Anmeldeschluss sperrt nichts. Späte Anmeldungen sind im Ehrenamt üblich.
- Neue Anmeldungen lassen sich optional ab einem Datum technisch sperren oder jederzeit manuell.
- Änderungen an Anmeldungen sind bis „letzte Änderung möglich“ erlaubt, sonst bis Veranstaltungsbeginn. Auch sie lassen sich manuell sperren.
- Personen zu einer bestehenden Anmeldung hinzuzufügen zählt als Änderung.
- Sind Änderungen gesperrt, sind auch neue Anmeldungen gesperrt. Umgekehrt gilt das nicht.
- Die Veranstaltungsleitung ist von allen Sperren ausgenommen.

**Umsetzung:** `anmelde_tool/event/deadlines.py`, Tests in `tests/test_fristen.py` (PR #5)

## 2026-10-14 · Gruppenrechte im Tool statt in Keycloak

**Entscheidung:** Wer welche Gruppe verwalten oder einsehen darf, steht in der Tabelle `GroupPermission` im Tool. Keycloak liefert nur Login und Gruppenmitgliedschaften.
**Begründung:** Die bisherige Lösung brauchte die veraltete Keycloak-Funktion `admin-fine-grained-authz:v1`, die beim Verband abgeschaltet ist. Das Tool soll mit einem Standard-Keycloak laufen und Keycloak-Updates überstehen. Ein Ausfall von Keycloak führt zu weniger Rechten, nie zu mehr.
**Regeln:**
- Rechte gelten auch für Untergruppen. Admin schließt Ansicht ein.
- Führungsgruppen (Stammesführung, Bundesführung, …) verwalten die Gruppe darüber. Mitglieder eines Stamms sehen ihren Stamm.
- Eine Gruppe löschen darf nur, wer die Obergruppe verwaltet.
- Über die eigene Beitrittsanfrage entscheidet nie man selbst.
- Die Rolle „Anmeldeteam“ (Staff) hat überall Admin-Recht. Bleibt vorerst so, Feinabstimmung später.

**Umsetzung:** `keycloak_auth/access.py`, Tests in `tests/test_gruppenrechte.py` (PR #2)

## 2026-10-14 · Wer sieht welche Anmeldungen

**Entscheidung:**
- Die Veranstaltungsleitung sieht alle Anmeldungen ihrer Veranstaltung.
- Die anmeldende Leitung sieht und bearbeitet ihre eigene Anmeldung vollständig.
- Teilnehmende sehen von ihrer Gruppenanmeldung nur die Namen der Mitangemeldeten. Anmeldungen anderer Gruppen sehen sie nicht.
- Personenlisten eines Stamms sehen nur Leitungen mit Admin-Recht auf den Stamm.

**Umsetzung:** Tests in `tests/test_rechte.py`. Die Namensansicht für Teilnehmende ist noch nicht gebaut (Phase 5).

## 2026-10-14 · Zusatzfelder pro Veranstaltung

**Entscheidung:** Daten wie die Ausweisnummer werden nicht fest abgefragt, sondern von der Veranstaltungsleitung pro Veranstaltung als Zusatzfeld festgelegt.
**Begründung:** Die Ausweisnummer war nur für eine Auslandsfahrt nötig (Datensparsamkeit, DSGVO).
**Umsetzung:** offen (Phase 5)

## 2026-10-14 · Hosting und Daten

**Entscheidung:** Start mit leerer Datenbank (nur Stammdaten). Offizieller Betrieb später beim Verband, bis dahin eine günstige eigene Lösung. Keycloak des Verbands: Version 26.7.

## 2026-10-14 · Basis und Repository

**Entscheidung:** Ein gemeinsames Repository für Backend und Frontend, mit vollständiger Historie. Basis sind Backend `main` (12.03.2025) und Frontend `ce97a2d` (23.03.2025). Nutzung mit Erlaubnis der ursprünglichen Entwickler, Lizenz noch offen.
