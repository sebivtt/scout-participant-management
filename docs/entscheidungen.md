# Entscheidungen

Fachliche und technische Entscheidungen mit Begründung. Neue Einträge oben. Wer eine Regel ändern will, ergänzt einen neuen Eintrag, statt einen alten zu überschreiben.

Format: Datum · Entscheidung · Begründung · Umsetzung

---

## 2026-10-15 · Sicherheitsupdates: Hauptversion und mitgebrachte Pakete

**Entscheidung:** Bei Sicherheitsupdates verlässt kein Paket, das wir selbst wählen, seine Hauptversion. Das gilt für Pakete in `package.json` und für Vorgaben über `resolutions`. Was ein aktualisiertes Paket zwingend selbst verlangt, darf mitkommen, auch in einer neuen Hauptversion. Jedes mitgebrachte Paket in neuer Hauptversion und jedes neu hinzugekommene Paket wird im Pull Request genannt und begründet (`CONTRIBUTING.md` Abschnitt 5). Kleine Hilfspakete desselben Ursprungs dürfen in einer Sammelzeile stehen.
**Begründung:** axios 1.20.0 schließt 33 Sicherheitslücken und verlangt dafür ein Hilfspaket in neuer Hauptversion (`proxy-from-env` 2) sowie ein neues Hilfspaket (`https-proxy-agent`). Beide laufen nur auf Servern, nicht im Browser. axios deshalb alt zu lassen, hätte bekannte Lücken offengelassen.
**Umsetzung:** `docs/fahrplan.md` Phase 3d („Vorgehen für künftige Updates“), erstmals angewendet in PR #16

## 2026-10-15 · Abgleich Frontend und Backend als automatische Prüfung

**Entscheidung (technisch):** Jede Anfrage des Frontends muss eine vorhandene Backend-Adresse mit erlaubter Anfrageart treffen. Ein Test prüft das bei jeder Änderung, und die Karte `docs/schnittstellen.md` wird aus dem Code erzeugt statt von Hand gepflegt.
**Begründung:** In PR #11 hätte das Entfernen einer Adresse fast alle Veranstaltungsseiten lahmgelegt, weil eine Textsuche zusammengesetzte Pfade nicht fand. Eine von Hand gepflegte Liste würde schnell veralten.
**Umsetzung:** `backend/tools/frontend_aufrufe.py`, `backend/tools/schnittstellen_karte.py`, `tests/test_frontend_abgleich.py` (PR #14)

## 2026-10-15 · Reihenfolge: erst Sicherheitsnetz, dann Frontend aktualisieren

**Entscheidung:** Vor den großen Versionssprüngen im Frontend entsteht ein Sicherheitsnetz: der automatische Abgleich zwischen Frontend und Backend und Rauchtests für das Frontend. Sicherheitsupdates innerhalb der Hauptversionen kommen früher. Die Modernisierung des Frontends (Phase 3d) kommt vor Phase 4. Die vollständige Reihenfolge steht im Fahrplan.
**Begründung:** Das Backend-Update war beherrschbar, weil 135 Tests jeden Schritt geprüft haben. Das Frontend hat keinen Test, ob nach einem Update noch alles geht, ließe sich also nur durch Klicken prüfen. Phase 4 baut den Anmeldeablauf stark um und soll nicht auf dem alten Fundament entstehen.
**Umsetzung:** `docs/fahrplan.md` Abschnitte „Reihenfolge der nächsten Schritte“ und „Phase 3d“

## 2026-10-15 · Abstimmung aller Funktionen und Abläufe vor Phase 4

**Entscheidung:** Bevor Anforderungen und Funktionen angepasst werden, stimmen KI und Projektverantwortlicher alle Funktionen und Abläufe gemeinsam ab. Am Ende gibt es zu jedem Ablauf einen Prozessablauf, und jede Funktion ist mit ihren Anforderungen abgestimmt: was kann wer, was darf wer und wann darf was gemacht werden.
**Begründung:** Diese Fragen stellen sich an vielen Stellen, auch bei der KI-Fehlerprüfung. Solange der Projektverantwortliche nicht nebenbei testen kann, ist ohne eine solche Grundlage kaum einzuschätzen, was wer wann darf.
**Umsetzung:** `docs/fahrplan.md` Abschnitt „Abstimmung der Funktionen und Abläufe“, Ergebnis in `docs/ablaeufe/`. Qualität II 4a/4b folgen danach.

## 2026-10-15 · Ansichtsgruppe ändert nichts

**Entscheidung:** Die Ansichtsgruppe einer Veranstaltung darf nichts ändern, auch keine Bausteine oder Preisstufen.
**Begründung:** So beschreibt es das Glossar. Der Code erlaubte ihr bisher, Bausteine und Preisstufen zu ändern und Anmeldungen zusammenzulegen.
**Umsetzung:** `anmelde_tool/event/permissions.py` (`IsSubEventResponsiblePersonOrReadOnly`), Tests in `tests/test_zugriffsschutz.py` (PR #11)

## 2026-10-15 · Veranstaltungsorte

**Entscheidung:**
- Den Ort einer bestimmten Veranstaltung passen nur das Anmeldeteam und die Veranstaltungsleitung an, beim Anlegen oder Bearbeiten der Veranstaltung.
- Zusätzlich soll es eine zentrale Verwaltung der Orte geben (neue Funktion), in der Admins und Leitungen Orte verwalten dürfen. Welche Leitungen genau, wird in der Abstimmung der Abläufe geklärt.

**Umsetzung bis zur zentralen Verwaltung:** Einen Ort ändert, wer alle Veranstaltungen an diesem Ort leitet, oder das Anmeldeteam. Unbenutzte Orte ändert nur das Anmeldeteam (PR #11).

## 2026-10-15 · Essensplanung und Programmideen abschalten

**Entscheidung:** Die eingefrorenen Module `food` (Essensplanung) und `inspi` (Programmideen) werden zunächst abgeschaltet. Abgesichert werden sie gegebenenfalls später, wenn ihre Anforderungen geklärt sind.
**Begründung:** In beiden kann jede eingeloggte Person Einträge anderer ändern oder löschen. Sie abzusichern wäre aufwendig, und ihre Anforderungen sind ohnehin offen.
**Umsetzung:** `backend/backend/urls.py`, Menüs im Frontend, Test `tests/test_abgeschaltete_module.py` (PR #12)

## 2026-10-15 · Rechte auf schreibende Schnittstellen

**Entscheidung (technisch):**
- Wer etwas ändert, braucht das Recht auf genau dieses Objekt: die Anmeldung (anmeldende Leitung oder Veranstaltungsleitung) oder die Veranstaltung (Veranstaltungsleitung). Der Login allein genügt nie.
- Die Zugehörigkeit eines Eintrags (zu welcher Veranstaltung, zu welcher Anmeldung) kommt aus der Adresse, nicht aus dem Inhalt der Anfrage.
- Antworten auf Zusatzfelder unterliegen derselben Änderungsfrist wie die Anmeldung.
- Gemeinsam genutzte Daten (Vorlagen für Zusatzfelder, Farbschemata) ändert nur das Anmeldeteam.
- Veranstaltungsorte siehe Eintrag „Veranstaltungsorte“ (15.10.2026).

**Begründung:** Qualität II fand 20 Lücken dieser Art, darunter Lesen und Ändern der Antworten aller Anmeldungen durch jede eingeloggte Person. Die Regeln folgen aus der Entscheidung „Wer sieht welche Anmeldungen“ vom 14.10.2026.
**Umsetzung:** `tests/test_zugriffsschutz.py`, `tests/test_schreibrechte_inventar.py`, `CONTRIBUTING.md` Abschnitt 3 (PR #11)

## 2026-10-15 · Sicherheitsregeln und feste Passwörter

**Entscheidung:**
- Die automatische Prüfung meldet bekannte unsichere Muster: abgeschaltete Zertifikatsprüfung, Passwörter im Code, verschluckte Fehler, unsichere Aufrufe (ruff, Regelgruppe S).
- Ein festes Passwort ist nur in Code erlaubt, der im Echtbetrieb verweigert wird (Prüfung auf `DEBUG=True`), mit Test. Administratoren im Echtbetrieb werden mit `python manage.py createsuperuser` angelegt.
- Tests dürfen `assert` und erfundene Passwörter verwenden.

**Begründung:** Das alte Startskript legte bei jedem Serverstart ein Administratorkonto mit öffentlich bekanntem Passwort an. Solche Fehler soll die Prüfung künftig von selbst finden.
**Umsetzung:** `CONTRIBUTING.md` Abschnitt 3, `backend/ruff.toml`, `tests/test_verwaltungsbefehle.py` (PR #10)

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
