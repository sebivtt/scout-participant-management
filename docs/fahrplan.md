# Fahrplan

Stand 15.10.2026. Dieses Dokument ist der Einstieg für jede neue Arbeitssitzung, auch für eine neue KI-Instanz ohne Kenntnis früherer Gespräche. Es sammelt, was erledigt ist, was als Nächstes kommt und welche Anforderungen schon bekannt sind. Erledigte Punkte werden abgehakt, neue ergänzt.

## Einstieg für eine neue Sitzung

1. `CLAUDE.md` und `CONTRIBUTING.md` lesen. Sie sind verbindlich.
2. `docs/entscheidungen.md` lesen. Was dort steht, ist entschieden und wird nicht still geändert.
3. `docs/architektur.md`, `docs/glossar.md` (Fachbegriffe) und `docs/qualitaet.md` überfliegen.
4. `README.md` für die lokale Installation. Entwicklungswerkzeuge mit `pip install -r backend/requirements-dev.txt`, Prüfung vor jedem Commit im Ordner `backend/` mit `ruff check . && pytest`. Ein echtes Keycloak 26.7 für Livetests startet über `dev/`.
5. Den Abschnitt „Übergabe“ unten lesen: Er beschreibt den nächsten Schritt konkret und die Eigenheiten der Arbeitsumgebung.
6. Mit dem nächsten offenen Punkt der „Reihenfolge der nächsten Schritte“ weitermachen.

Pfade zu Tests und Backend-Code sind relativ zum Ordner `backend/` angegeben, z. B. `tests/test_abfragen.py` = `backend/tests/test_abfragen.py`. Arbeit erfolgt auf einem eigenen Branch je Thema, Pull Requests gehen gegen `main` von `sebivtt/scout-participant-management`.

### Zusammenarbeit mit dem Projektverantwortlichen

- Sebastian ist kein Programmierer. Erklärungen sind deutsch, in Alltagssprache und ohne Fachjargon. Fachbegriffe werden beim ersten Auftreten erklärt.
- Terminal-Anleitungen gehen Schritt für Schritt: genau ein Befehl pro Schritt, dazu, was danach zu sehen sein sollte. Er arbeitet auf einem Mac, das Projekt liegt unter `~/Projekte/scout-participant-management`.
- Er prüft und übernimmt Pull Requests auf GitHub, den Code selbst liest er nicht. Die Beschreibung eines Pull Requests ist deshalb sein wichtigstes Werkzeug (siehe `CONTRIBUTING.md` Abschnitt 6).
- Er möchte ehrlich hören, was nicht funktioniert und welche Fehler die KI selbst gemacht hat.
- Fachliche Fragen (wer darf was, welche Fristen gelten) entscheidet er. Technische Fragen entscheidet die KI und begründet sie.
- Pull Requests werden nicht aufeinander aufgebaut. Der nächste beginnt erst, wenn der vorige in `main` ist. (PR #12 landete sonst im falschen Branch und musste mit PR #13 nachgeholt werden.)

## Übergabe (Stand 15.10.2026, nach PR #14)

### Was erledigt ist

Qualität II, KI-Fehlerprüfung, bisher:
- **PR #9:** pauschale Ausnahmen aufgeräumt
- **PR #10:** Sicherheitsregeln an, Admin-Konto mit festem Passwort entfernt
- **PR #11:** 20 Lücken im Zugriffsschutz geschlossen
- **PR #12/#13:** Essensplanung und Programmideen abgeschaltet
- **PR #14:** automatischer Abgleich zwischen Frontend und Backend, dazu die Karte `docs/schnittstellen.md`

228 Tests. Ergebnisse in `docs/qualitaet.md`, Entscheidungen in `docs/entscheidungen.md`.

### Nächster Schritt: Sicherheitsupdates im Frontend innerhalb der Hauptversionen

Ziel ist, bekannte Sicherheitslücken in Code zu schließen, der im Browser läuft, ohne große Versionssprünge.

- **Bestandsaufnahme:** `yarn audit --groups dependencies` im Ordner `frontend/`. Am 15.10. waren es 63 Lücken, betroffen u. a.:
  - `axios` (in `package.json` fest auf `1.7.4`, mit `form-data` als „kritisch“)
  - `nanoid`, `postcss`, `source-map-js`, `follow-redirects`, `moment`, `quill`, `uuid`, `@vue/server-renderer` (Teil von Vue 3.3)
- **Nur innerhalb der Hauptversion:** z. B. axios 1.x, Vue 3.x. Nicht Vite, vue-router, Pinia, Tailwind, TypeScript oder eslint auf neue Hauptversionen heben, das ist Phase 3d.
- **`yarn.lock` und `package.json`:** `yarn.lock` wird mit aktualisiert. Jede Paketänderung bekommt eine Begründung im Pull Request (`CONTRIBUTING.md` Abschnitt 5).
- **Prüfen, ob noch alles geht:**
  - Frontend-Build ohne Fehler
  - `tests/test_frontend_abgleich.py`
  - eslint in den geänderten Dateien vorher und nachher vergleichen (keine neuen Fehler)
  - Klickliste für Sebastian im Pull Request: Login, Veranstaltung ansehen und bearbeiten, Anmeldung anlegen und ändern, Person löschen, Kasse, Gruppen
- **Danach** laut Reihenfolge oben: Rauchtests mit Anleitung zum lokalen Start, dann die großen Versionssprünge (Phase 3d).

### Offene Fragen an Sebastian

- **Klicktest zu PR #11:** Die Rechte wurden spürbar enger. Klickliste siehe PR #11, Abschnitt 3. Ist er erfolgt, und ist etwas fälschlich gesperrt?
- **Weiterleitung nach dem Speichern** (Phase 4, Rückmeldungen): War das Speichern eines Veranstaltungsorts gemeint? `EventEdit/location/Form.vue` springt nach dem Ändern mit der Kennung des Orts statt der Veranstaltung zur Detailseite.
- **Person aus einer Anmeldung löschen** schlug lokal wegen eines fehlenden Schrägstrichs fehl (behoben in PR #14). Ist das beim Testen aufgefallen?

### Eigenheiten der Arbeitsumgebung (Cloud-Sitzung)

- **Backend einrichten:**
  ```
  cd backend
  python3 -m venv .venv
  .venv/bin/pip install -r requirements-dev.txt
  ```
  Tests laufen mit `DJANGO_SETTINGS_MODULE=backend.settings_test`. Das steht auch in `pytest.ini`.
- **Frontend:**
  - Installieren mit `CYPRESS_INSTALL_BINARY=0 yarn install --frozen-lockfile`.
  - `yarn build` braucht die Umgebungsvariablen `VITE_APP_API`, `VITE_APP_URL`, `VITE_APP_KEYCLOAK_URL`, `VITE_APP_KEYCLOAK_REALM` und `VITE_APP_KEYCLOAK_CLIENT_ID` (Werte wie in `.github/workflows/ci.yml`).
  - Der Build ändert `frontend/components.d.ts` (eine Zeile `StepperNav`). Diese Änderung ist älter und gehört nicht in fremde Pull Requests: mit `git checkout frontend/components.d.ts` zurücksetzen.
- **Livetest gegen Keycloak ist in der Cloud nicht möglich.** Docker lässt sich mit `dockerd &` starten, aber das Abbild `quay.io/keycloak/keycloak` ist gesperrt. Livetests macht deshalb Sebastian auf seinem Mac, mit einer Schritt-für-Schritt-Anleitung (ein Befehl pro Schritt).
- **GitHub:** `gh pr …` geht nicht (GraphQL gesperrt). Stattdessen die REST-Schnittstelle, z. B. `gh api repos/sebivtt/scout-participant-management/pulls -f title=… -f head=… -f base=main -F body=@datei.md`. Den Stand der automatischen Prüfungen zeigt `gh api repos/…/commits/<sha>/check-runs`.
- **Branches:** Die Kopie des Repositorys ist flach und kennt nur `main`. Neue Branches mit `git push -u origin <branch>` hochladen. Meldet ein Hinweis „unpushed commits“, obwohl gepusht wurde, mit `git ls-remote origin <branch>` prüfen.
- **Nach dem Ändern von Adressen oder Rechten** die Karte neu erzeugen: `.venv/bin/python tools/schnittstellen_karte.py` im Ordner `backend/`. Sonst schlägt ein Test an.

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
| **Qualität II: KI-Fehlerprüfung** | siehe unten | **in Arbeit** (PR #9 bis #14), Rest siehe Reihenfolge |
| 3d Modernisierung Frontend | siehe unten | offen |
| **Abstimmung der Funktionen und Abläufe** | siehe unten | offen, kann parallel zu 3d beginnen |
| 4 Frontend und Anmeldeablauf | siehe unten | offen |
| 5 Datenschutz | siehe unten | offen |
| 6 Eigene Ideen | Ideen des Projektverantwortlichen umsetzen | offen |
| 7 Anforderungsanalyse | Andere im Verband nach Bedarf fragen | offen |
| Betrieb | Hosting, Dockerfile, Lizenz | offen, wartet auf Entscheidung |

### Reihenfolge der nächsten Schritte (Bestandsaufnahme vom 15.10.2026)

1. **Qualität II, Schritt 2: Frontend und Backend abgleichen**, mit automatischer Prüfung. Adressen und Anfragearten erledigt (2a, PR #14), Feldnamen offen (2b). Das ist das erste Sicherheitsnetz für alle weiteren Änderungen und liefert die Karte „welche Seite ruft welche Schnittstelle auf“, die die Abstimmung der Abläufe braucht.
2. **Sicherheitsupdates im Frontend innerhalb der Hauptversionen**, z. B. axios. Wenig riskant und dringend: 63 bekannte Sicherheitslücken betreffen Code, der im Browser läuft.
3. **Rauchtests für das Frontend**: jede Seite einmal öffnen, dazu ein Durchlauf des Anmeldeablaufs. Ohne sie lässt sich nach den großen Versionssprüngen nicht prüfen, ob noch alles geht. Das Frontend hat heute keinen einzigen Test.
4. **Phase 3d, Modernisierung Frontend**: die großen Versionssprünge einzeln, je mit Rauchtests und Klicktest. Vor Phase 4, damit der neue Anmeldeablauf nicht auf dem alten Fundament entsteht.
5. **Qualität II, Schritt 3: Keycloak-Abgleich**, zusammen mit dem Keycloak-Baustein im Frontend.
6. **Qualität II, Schritt 1c**: die restlichen Prüfregeln, klein und unabhängig, auch zwischendurch möglich.
7. **Abstimmung der Funktionen und Abläufe**, danach Qualität II 4a/4b und Phase 4. Die Abstimmung kann beginnen, sobald die Karte aus Schritt 1 steht, parallel zur technischen Arbeit.

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
- [x] 1b-1. Sicherheitsregeln (ruff `S`) einschalten und die Funde beheben: Administratorkonto mit festem Passwort beim Serverstart, abgeschaltete Zertifikatsprüfung (PR #10).
- [x] 1b-2. Alle 70 Fundstellen von `fields = '__all__'`, alle schreibenden Schnittstellen und alle öffentlichen Adressen bewertet. 20 Lücken im Zugriffsschutz behoben, darunter die Schreibrechte der Ansichtsgruppe (Entscheidung vom 15.10.2026), automatische Prüfung für schreibende Schnittstellen (PR #11, Ergebnis in `docs/qualitaet.md`).
- [x] 1d. Essensplanung (`food`) und Programmideen (`inspi`) abgeschaltet: Adressen und Menüpunkte entfernt, Code und Datenbanktabellen bleiben (Entscheidung vom 15.10.2026, PR #12).
- [ ] Noch aus 1b: `add_state` bricht bei einem unbekannten Bundesland mit einem unverständlichen Fehler ab.
- [ ] 1c. Weitere Regelgruppen (`DJ`, `PERF`, `RET`, `W605`, pauschales `except Exception`) mit Zählung und Bewertung, dazu die 7 Altlasten mit `except:`. Bekannte Treffer: `authentication/views.py` Passwortprüfung (`W605`, ungültige Escape-Sequenz, funktioniert heute noch); `anmelde_tool/registration/signals.py` besteht nur aus auskommentiertem Code (klären, ob die Mail „Anmeldung angelegt“ fehlt oder anderswo verschickt wird).
- [x] 2a. Frontend-Aufrufe mit den Backend-Adressen und Anfragearten abgleichen, automatisch bei jeder Änderung (`tests/test_frontend_abgleich.py`), dazu die Karte `docs/schnittstellen.md` (PR #14). Frontend-Pakete: Die automatische Prüfung installiert sie bei jedem Lauf aus der festen Paketliste, erfundene Pakete würden dort scheitern.
- [ ] 2b. Feldnamen abgleichen: Liest das Frontend Felder, die das Backend nicht liefert? Achtung: Das Backend wandelt Feldnamen automatisch um (`first_name` ↔ `firstName`, Paket `djangorestframework-camel-case`).
- [ ] 3. Genutzte python-keycloak-Methoden mit der installierten Version (7.1.1) abgleichen, mit Livetest gegen Keycloak 26.7.
- [ ] 4a. Randfälle und Fehlerbehandlung beim Anmelden und Ändern mit Tests absichern. **Erst nach der Abstimmung der Funktionen und Abläufe**, damit die Tests die abgestimmten Regeln prüfen.
- [ ] 4b. Dasselbe für Rechte und Gruppen, dazu doppelte Logik an mehreren Stellen (Tabellenzeile „Lokal richtig, passt nicht ins Ganze“). Ebenfalls erst nach der Abstimmung.
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

## Phase 3d: Modernisierung Frontend

Stand 15.10.2026: Vite 2.9 (aktuell 8), Vue 3.3 (3.5), vue-router 4.0 (5), Pinia 2 (4), Tailwind 3 (4), TypeScript 4.6 (7), eslint 8 (10). Bekannte Sicherheitslücken: 329, davon 63 in Code, der im Browser läuft (u. a. axios, form-data).

- [ ] Sicherheitsupdates innerhalb der Hauptversionen (Reihenfolge oben, Schritt 2).
- [ ] Rauchtests: jede Seite lädt ohne Fehler, Anmeldeablauf läuft durch. Werkzeug voraussichtlich Playwright (steuert einen echten Browser, unabhängig von der Vite-Version); als neues Paket mit Begründung.
- [ ] Anleitung, das Tool lokal mit Beispieldaten zu starten (dieselben Beispieldaten nutzen die Rauchtests).
- [ ] eslint in die automatischen Prüfungen auf GitHub. Heute 198 Fehler und ca. 2.800 Warnungen: zuerst die Fehler, Warnungen schrittweise.
- [ ] Große Versionssprünge einzeln, je ein Pull Request mit Rauchtests und Klicktest.

## Abstimmung der Funktionen und Abläufe

Vereinbart am 15.10.2026. Ziel: Für jeden Ablauf ist abgestimmt, wer was darf und wann. Ohne diese Grundlage muss die KI bei Rechten und Fristen raten oder einzeln nachfragen, und der Projektverantwortliche kann nur schwer einschätzen, was wann gilt, solange er nicht nebenbei testen kann.

**Vorgehen:**
1. Die KI erstellt den Ist-Stand aus dem Code, ein Dokument pro Ablauf in `docs/ablaeufe/`. Beispiele: Veranstaltung anlegen, Anmelden, Anmeldung ändern, Kasse, Auswertung, Gruppen verwalten, Konto und persönliche Daten. Jedes Dokument enthält:
   - ein Ablaufdiagramm,
   - eine Tabelle „wer darf was in welcher Phase“, also vor dem Anmeldestart, während der Anmeldung, nach dem Anmeldeschluss und nach der Änderungsfrist,
   - eine Liste der Stellen, die vermutlich nicht so gewollt sind.
2. Der Projektverantwortliche geht die Abläufe einzeln durch und entscheidet pro Zeile: so lassen oder ändern. Das Ergebnis steht als Soll im Dokument und in `docs/entscheidungen.md`.
3. Jede abgestimmte Regel bekommt einen Test. Danach folgen Qualität II 4a/4b und Phase 4.

**Schon gesammelte Fragen:**
- Wer darf welche Veranstaltung sehen? Heute liefert `/event/event-read/` jeder eingeloggten Person jede Veranstaltung.
- Wer darf in der geplanten zentralen Ortsverwaltung Orte verwalten?
- Darf die Ansichtsgruppe Excel-Listen erzeugen? Heute ja, weil das eine Form der Auswertung ist.
- Was passiert mit Orten, die angelegt, aber keiner Veranstaltung zugeordnet wurden?
- Sollen beim Zusammenlegen zweier Anmeldungen auch deren Bewertungen (und Workshops, falls das Modul wieder eingebunden wird) übernommen werden? Heute gehen sie mit der gelöschten Anmeldung verloren.

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
- [ ] Die Schaltfläche **„Anmeldungen zusammenfassen“** in der Auswertung erscheint auch für Ansichtsgruppe sowie Bundes- und Ringführung. Seit Qualität II 1b-2 lehnt das Backend das ab, die Oberfläche zeigt dann keine Meldung, sondern bricht still ab. Nur der Veranstaltungsleitung anzeigen, Fehler anzeigen.
- [ ] Die **Schalter für Fristen und Sperren** aus Phase 3b sind im Backend fertig, haben aber keine Bedienelemente im Frontend.

### Technische Grundlage Frontend

- [ ] Die Hauptdatei (1,2 MB) aufteilen, sodass Seiten erst bei Bedarf geladen werden.

eslint in den automatischen Prüfungen und die ersten Frontend-Tests sind in Phase 3d vorgezogen.

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
| Begrenzung der Anfragen pro Minute für die öffentlichen Adressen: Registrierung, Kontaktformular, Prüfung von Benutzername und E-Mail (verraten, ob eine Adresse registriert ist) | PR #3, Qualität II 1b-2 | technisch |
| Zentrale Verwaltung der Veranstaltungsorte (neue Funktion, Entscheidung vom 15.10.2026). Offen: Welche „Leitungen“ dürfen dort Orte verwalten? | Qualität II 1b-2 | Projektverantwortlicher, in der Abstimmung der Abläufe |
| Kleinste nötige Rollen für das Keycloak-Dienstkonto (getestet nur mit `realm-admin`) | PR #2 | technisch, mit Verbands-Admin |
| `django-stdimage` ist veraltet, Nachfolger `django-pictures` | PR #6 | technisch |
| Dockerfile für den Echtbetrieb. Das alte Setup in `backend/` (Dockerfile, docker-compose.yml, start.sh) ist ungeprüft. Djangos Prüfung für den Echtbetrieb (`manage.py check --deploy`) verlangt dort `SECURE_SSL_REDIRECT=True`, falls der vorgeschaltete Webserver nicht auf HTTPS umleitet | PR #6, Qualität II 1b-1 | mit der Hosting-Entscheidung |
| `anonymise_data` überschreibt ohne Rückfrage alle Personendaten der Datenbank. Eine Sicherung gegen versehentlichen Aufruf im Echtbetrieb fehlt | Qualität II 1b-1 | technisch |
| Hosting: vorerst günstiger eigener Server, später ggf. AWS beim Verband | Gespräch | Projektverantwortlicher |
| Lizenz des Projekts | `docs/entscheidungen.md` | mit den ursprünglichen Entwicklern |
| Eingefrorene Module: `food` und `inspi` werden abgeschaltet (Qualität II 1d), ob sie später abgesichert zurückkommen, klärt die Abstimmung der Anforderungen. `messaging` und `notifications` bleiben vorerst | Phase 1, Qualität II 1b-2 | Projektverantwortlicher |

## Ideen (Phase 6)

Noch keine eigenen Ideen festgehalten. Hierarchische Stammauswahl, Adressfelder mit Bundesland und die Neugestaltung der Module sind in Phase 4 vorgezogen. Weitere Ideen sammelt der Projektverantwortliche, bevor die Anforderungsanalyse im Verband beginnt (Phase 7).
