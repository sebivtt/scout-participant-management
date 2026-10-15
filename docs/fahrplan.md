# Fahrplan

Stand 15.10.2026. Dieses Dokument ist der Einstieg für jede neue Arbeitssitzung, auch für eine neue KI-Instanz ohne Kenntnis früherer Gespräche. Es sammelt, was erledigt ist, was als Nächstes kommt und welche Anforderungen schon bekannt sind. Erledigte Punkte werden abgehakt, neue ergänzt.

## Einstieg für eine neue Sitzung

1. `CLAUDE.md` und `CONTRIBUTING.md` lesen. Sie sind verbindlich.
2. `docs/entscheidungen.md` lesen. Was dort steht, ist entschieden und wird nicht still geändert.
3. `docs/architektur.md`, `docs/glossar.md` (Fachbegriffe) und `docs/qualitaet.md` überfliegen.
4. `README.md` für die lokale Installation. Entwicklungswerkzeuge mit `pip install -r backend/requirements-dev.txt`, Prüfung vor jedem Commit im Ordner `backend/` mit `ruff check . && pytest`. Ein echtes Keycloak 26.7 für Livetests startet über `dev/`.
5. Mit dem nächsten offenen Punkt unten weitermachen. Derzeit läuft die KI-Fehlerprüfung (Qualität II), der nächste offene Schritt steht in ihrer Checkliste.

Pfade zu Tests und Backend-Code sind relativ zum Ordner `backend/` angegeben, z. B. `tests/test_abfragen.py` = `backend/tests/test_abfragen.py`. Arbeit erfolgt auf einem eigenen Branch je Thema, Pull Requests gehen gegen `main` von `sebivtt/scout-participant-management`.

### Zusammenarbeit mit dem Projektverantwortlichen

- Sebastian ist kein Programmierer. Erklärungen sind deutsch, in Alltagssprache und ohne Fachjargon. Fachbegriffe werden beim ersten Auftreten erklärt.
- Terminal-Anleitungen gehen Schritt für Schritt: genau ein Befehl pro Schritt, dazu, was danach zu sehen sein sollte. Er arbeitet auf einem Mac, das Projekt liegt unter `~/Projekte/scout-participant-management`.
- Er prüft und übernimmt Pull Requests auf GitHub, den Code selbst liest er nicht. Die Beschreibung eines Pull Requests ist deshalb sein wichtigstes Werkzeug (siehe `CONTRIBUTING.md` Abschnitt 6).
- Er möchte ehrlich hören, was nicht funktioniert und welche Fehler die KI selbst gemacht hat.
- Fachliche Fragen (wer darf was, welche Fristen gelten) entscheidet er. Technische Fragen entscheidet die KI und begründet sie.

## Phasen

| Phase | Inhalt | Stand |
| --- | --- | --- |
| 1 Fundament | Gemeinsames Repository und lokale Installation (direkte Commits), Backend ohne Keycloak startfähig, Testgerüst | ✅ Vorarbeit + PR #1 |
| 2 Rechte | Gruppenrechte im Tool statt in Keycloak, Sicherheitslücken geschlossen | ✅ PR #2 |
| 3a Sicherheit und Fehler | Login-Pflicht als Standard, Fehler bei frischer Installation | ✅ PR #3 |
| Fehlerbehebung | Speichern persönlicher Daten löschte E-Mail und Namen in Keycloak | ✅ PR #4 |
| 3b Fristen | Anmelde- und Änderungsfristen, manuelle Sperren | ✅ PR #5 |
| 3c Modernisierung Backend | Django 5.2, aktuelle Pakete, pip-audit | ✅ PR #6 |
| Qualität | Regeln, ruff, Dokumentation, Messung | ✅ PR #7 |
| **Qualität II: KI-Fehlerprüfung** | siehe unten | **in Arbeit** (PR #9) |
| 4 Frontend und Anmeldeablauf | siehe unten | offen |
| 5 Datenschutz | siehe unten | offen |
| 6 Eigene Ideen | Ideen des Projektverantwortlichen umsetzen | offen |
| 7 Anforderungsanalyse | Andere im Verband nach Bedarf fragen | offen |
| Betrieb | Hosting, Dockerfile, Lizenz | offen, wartet auf Entscheidung |

## Qualität II: Prüfung auf typische KI-Fehler

**Auftrag:** Den gesamten Code, den übernommenen und den von KI geänderten, auf typische Fehler von KI-generiertem Code prüfen. Grundlage ist der Artikel <https://scand.de/unternehmen/blog/why-ai-generated-code-doesnt-work-and-how-to-fix-it/>. Gefundene Probleme werden als Tests oder als automatische Prüfung festgehalten. Noch offene Fehler werden als `xfail(strict=True, raises=…)` mit genau der erwarteten Fehlerart markiert, damit nicht jeder beliebige Fehler als „bekannt“ durchgeht (Vorbild: `tests/test_abfragen.py`). Was sich nicht automatisch prüfen lässt, kommt als Regel in `CONTRIBUTING.md`. Ein Ergebnisabschnitt kommt in `docs/qualitaet.md`.

Die Tabelle fasst die Fehlerarten des Artikels vollständig zusammen und übersetzt sie auf dieses Projekt. Der Artikel muss nicht erneut gelesen werden.

| Fehlerart laut Artikel | Was hier konkret zu prüfen ist | Heute schon abgedeckt? |
| --- | --- | --- |
| Nur der Normalfall ist bedacht | Leere Listen, fehlende Felder, doppelte Anfragen, gleichzeitige Änderungen, Keycloak oder Mail nicht erreichbar, Fristen genau auf der Grenze | teilweise (Fristen-Grenzen, Keycloak-Ausfall bei Rechten) |
| Fehlende Fehlerbehandlung, stille Fehler | `except: pass`, verschluckte Fehler, Rückgabe `None` statt Fehlermeldung, Frontend-Meldungen, die den echten Fehler verdecken | teilweise (ruff E722; 7 Altlasten mit `# noqa: E722` sind ein konkreter Startpunkt) |
| Fehlende Eingabeprüfung | Serializer ohne Prüfung, Datei-Uploads (Excel-Import), Längen und Formate, Rechte nur im Frontend | teilweise (Datumsreihenfolge, Rechte-Tests) |
| Sicherheitslücken | SQL über `raw()` oder `extra()`, Zugangsdaten im Code oder in `.env.example`, offene Endpunkte (`AllowAny`), Massenzuweisung über `fields = '__all__'`, fehlende Begrenzung öffentlicher Endpunkte | teilweise (pip-audit, Login-Pflicht als Standard). `fields = '__all__'` kommt oft vor, z. B. in `anmelde_tool/event/serializers.py`: jede Fundstelle einzeln bewerten |
| Erfundene Funktionen oder falsche Versionen | Aufrufe von Bibliotheksfunktionen, die es in der installierten Version nicht gibt (v. a. python-keycloak, DRF), Frontend-Pakete | nein (nur indirekt über Tests) |
| Falsche Annahmen über Datenstrukturen | Antworten von Keycloak (Felder optional?), Frontend erwartet andere Feldnamen als das Backend liefert, `None` vs. leere Liste | nein |
| Lokal richtig, passt nicht ins Ganze | Doppelte Logik an mehreren Stellen (z. B. Rechteprüfung, Datumsprüfung), Regeln aus `docs/entscheidungen.md` nicht überall umgesetzt | teilweise (zwei Fälle in PR #7 gefunden) |
| Zu einfach oder zu kompliziert | Übersprungene Details, unnötige Abstraktionen, tote oder doppelte Funktionen | teilweise (ruff C901) |
| Schwer nachvollziehbar | Annahmen nicht dokumentiert, keine Docstrings | teilweise (Docstring-Quote 8 %) |

**Vorgehen in dieser Reihenfolge**, jeweils ein eigener Pull Request (am 15.10.2026 mit dem Projektverantwortlichen abgestimmt; Prüftiefe und Abgrenzung zu Phase 4 siehe `docs/entscheidungen.md`):
- [x] 1a. Pauschale `# noqa` ohne Regelnummer aufräumen, damit sie neue Regeln nicht verstecken. ruff verbietet sie künftig (PR #9).
- [ ] 1b. Sicherheitsregeln (ruff `S`) einschalten und jede Fundstelle von `fields = '__all__'` bewerten (gesamter Code, auch eingefrorene Module).
- [ ] 1c. Weitere Regelgruppen (`DJ`, `PERF`, `RET`, `W605`, pauschales `except Exception`) mit Zählung und Bewertung, dazu die 7 Altlasten mit `except:`. Bekannte Treffer: `authentication/views.py` Passwortprüfung (`W605`, ungültige Escape-Sequenz, funktioniert heute noch); `anmelde_tool/registration/signals.py` besteht nur aus auskommentiertem Code (klären, ob die Mail „Anmeldung angelegt“ fehlt oder anderswo verschickt wird).
- [ ] 2. Frontend-Aufrufe mit den Backend-Endpunkten und ihren Feldnamen abgleichen. Achtung: Das Backend wandelt Feldnamen automatisch um (`first_name` ↔ `firstName`, Paket `djangorestframework-camel-case`). Dazu die Frontend-Pakete prüfen (Tabellenzeile „Erfundene Funktionen“).
- [ ] 3. Genutzte python-keycloak-Methoden mit der installierten Version (7.1.1) abgleichen, mit Livetest gegen Keycloak 26.7.
- [ ] 4a. Randfälle und Fehlerbehandlung beim Anmelden und Ändern mit Tests absichern.
- [ ] 4b. Dasselbe für Rechte und Gruppen, dazu doppelte Logik an mehreren Stellen (Tabellenzeile „Lokal richtig, passt nicht ins Ganze“).
- [ ] 5. Abschluss: Tabelle oben vollständig beantworten, Ergebnisabschnitt in `docs/qualitaet.md`, neue Review-Regeln in `CONTRIBUTING.md`.

**Fertig ist die Phase**, wenn jede Zeile der Tabelle mit „abgedeckt“ oder „bewusst nicht, weil …“ beantwortet ist und `docs/qualitaet.md` einen Ergebnisabschnitt hat.

**Hinweise:**
- Vorgehen wie im Artikel empfohlen: erst reproduzieren, dann isolieren und Annahmen prüfen, erst danach ändern.
- Mögliche Werkzeuge, jeweils nur mit Begründung (`CONTRIBUTING.md` Abschnitt 5):
  - weitere ruff-Regelgruppen wie `S` (Sicherheit, entspricht bandit), `DJ` (Django), `PERF` und `RET`,
  - ein Abgleich der Frontend-Aufrufe mit den Backend-Endpunkten,
  - ein Abgleich der genutzten python-keycloak-Methoden mit der installierten Version.
- Kleine, thematische Pull Requests. Die Prüfung darf sich in mehrere aufteilen.
- Vor jedem Pull Request eine unabhängige Prüfung durch eine zweite KI-Instanz (siehe `CLAUDE.md`).

## Phase 4: Frontend und Anmeldeablauf

### Backend, aus der Qualitätsmessung (`docs/qualitaet.md`)

- [ ] **N+1-Abfragen** (die Seite fragt die Datenbank für jeden Listeneintrag einzeln ab) auf sechs Seiten beheben: Auswertung, Meine Anmeldungen, Kassenliste, Gruppenliste, Veranstaltungsübersicht, Meine Einladungen. Ist eine Seite behoben, meldet `tests/test_abfragen.py` das, und die `xfail`-Markierung wird entfernt.
- [ ] **Absenden als „ganz oder gar nicht“:** Das Frontend schickt heute viele Einzelanfragen. Scheitert eine, bleibt eine halbe Anmeldung übrig. Ziel: ein Endpunkt, der alles in einem Schritt anlegt, der entweder vollständig gelingt oder gar nichts verändert (Datenbank-Transaktion).
- [ ] **Fehlermeldungen:** Die festen Texte („Ein Pflichtfeld fehlt“, „Stamm nicht gefunden“) durch die echte Meldung des Backends ersetzen, verständlich formuliert.
- [ ] **`is_confirmed` setzen:** Das Feld wird nie gesetzt, deshalb erreichen Rundmails an „bestätigte Anmeldungen“ niemanden. Test dazu.
- [ ] Zu komplexe Funktionen aufteilen, wenn sie ohnehin angefasst werden (Liste in `docs/qualitaet.md`).

### Rückmeldungen aus dem lokalen Test des Projektverantwortlichen (14.10.2026)

Die Stichpunkte sind aus dem Gespräch übernommen. Vor der Umsetzung kurz mit ihm klären, was genau gemeint war.

- [ ] Der Anmeldeablauf hat keinen **Zurück-Knopf**.
- [ ] Die **Schritte** im Ablauf sind **nicht beschriftet**. Man weiß nicht, wo man ist und was noch kommt.
- [ ] Texte sollen **als Fragen formuliert** sein („Wer kommt mit?“ statt „Teilnehmende“).
- [ ] Der Reiter **„Module“** beim Anlegen einer Veranstaltung ist unverständlich und soll grundlegend überarbeitet werden.
- [ ] Die **Stammauswahl** ist eine lange flache Liste, die sich schlecht scrollen lässt. Gewünscht ist eine hierarchische Auswahl (Bund → Ring/Gau → Stamm).
- [ ] Das **E-Mail-Feld** in den persönlichen Daten ist gesperrt, ohne Erklärung. Es kommt aus Keycloak. Ein erklärender Hinweis fehlt.
- [ ] **Adressfelder** sollen aufgeteilt werden (Straße, PLZ, Ort) und um ein **Bundesland** ergänzt werden.
- [ ] Nach dem **Speichern** führt die Weiterleitung auf die nächste Seite (`router.push`) ins Leere oder scheitert. Welche Seite betroffen war, ist nicht mehr bekannt: nachfragen, reproduzieren, beheben.
- [ ] Ein **abgelaufener Login** führt zu stillen 401-Fehlern. Stattdessen soll man eine klare Meldung sehen oder neu angemeldet werden.
- [ ] Die **Schalter für Fristen und Sperren** aus Phase 3b sind im Backend fertig, haben aber keine Bedienelemente im Frontend.

### Technische Grundlage Frontend

- [ ] eslint (automatische Code-Prüfung für das Frontend) in die automatischen Prüfungen auf GitHub (CI) aufnehmen. Heute gibt es 198 Fehler und ca. 2.800 Warnungen. Zuerst die Fehler beheben, die Warnungen schrittweise.
- [ ] Erste Tests für das Frontend, mindestens für den Anmeldeablauf.
- [ ] Die Hauptdatei (1,2 MB) aufteilen, sodass Seiten erst bei Bedarf geladen werden.

## Phase 5: Datenschutz

- [ ] **Namensansicht für Teilnehmende:** Sie sehen von ihrer Gruppenanmeldung nur die Namen (siehe `docs/entscheidungen.md`).
- [ ] **Zusatzfelder pro Veranstaltung**, z. B. die Ausweisnummer, statt fester Felder.
- [ ] **Browserspeicher:** Die Eingaben der Anmeldung, auch Daten von Kindern, liegen bis zum Absenden dauerhaft im Browser (Zwischenspeicher `frontend/src/modules/event/store/register.ts` mit `persist: true`). Nach dem Absenden oder Abmelden löschen oder gar nicht dauerhaft speichern.
- [ ] **API-Logger:** Er speichert jede Anfrage samt Inhalt dauerhaft in der Datenbank. Inhalte nicht speichern oder nach kurzer Frist löschen.
- [ ] Löschfristen für Anmeldungen nach Veranstaltungsende festlegen (fachliche Entscheidung nötig).

## Offene Punkte für später

| Punkt | Herkunft | Wer entscheidet |
| --- | --- | --- |
| Beim Anmelden kann man jeden Stamm wählen, nicht nur den eigenen | PR #3 | Projektverantwortlicher |
| Feinabstimmung der Rechte des Anmeldeteams (Staff hat heute überall Admin) | PR #2 | Projektverantwortlicher |
| Begrenzung der Anfragen pro Minute für die öffentliche E-Mail-Prüfung | PR #3 | technisch |
| Kleinste nötige Rollen für das Keycloak-Dienstkonto (getestet nur mit `realm-admin`) | PR #2 | technisch, mit Verbands-Admin |
| `django-stdimage` ist veraltet, Nachfolger `django-pictures` | PR #6 | technisch |
| Dockerfile für den Echtbetrieb | PR #6 | mit der Hosting-Entscheidung |
| Hosting: vorerst günstiger eigener Server, später ggf. AWS beim Verband | Gespräch | Projektverantwortlicher |
| Lizenz des Projekts | `docs/entscheidungen.md` | mit den ursprünglichen Entwicklern |
| Eingefrorene Module (z. B. `food`) behalten oder entfernen | Phase 1 | Projektverantwortlicher |

## Ideen (Phase 6)

Noch keine eigenen Ideen festgehalten. Hierarchische Stammauswahl, Adressfelder mit Bundesland und die Neugestaltung der Module sind in Phase 4 vorgezogen. Weitere Ideen sammelt der Projektverantwortliche, bevor die Anforderungsanalyse im Verband beginnt (Phase 7).
