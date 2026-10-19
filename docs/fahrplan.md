# Fahrplan

Stand 16.10.2026, neu aufgebaut nach der Aufräumrunde (Entscheidungen vom 16.10.2026 in `docs/entscheidungen.md`). **Dieses Dokument ist die einzige verbindliche Reihenfolge.** Was als Nächstes umgesetzt wird, steht hier und nirgends sonst. Das Label `geklärt` an einem Issue heißt nur: fachlich fertig geklärt. Dran ist ein Issue erst, wenn es in der Liste unten an der Reihe ist.

## Einstieg für eine neue Sitzung

1. `CLAUDE.md` und `CONTRIBUTING.md` lesen. Sie sind verbindlich.
2. `docs/entscheidungen.md` lesen. Was dort steht, ist entschieden und wird nicht still geändert.
3. `docs/architektur.md`, `docs/glossar.md` (Fachbegriffe) und `docs/qualitaet.md` überfliegen.
4. `docs/arbeitsumgebung.md` für Einrichtung, Eigenheiten der Cloud-Sitzung und das Nachstellen von Fehlern im Browser. `README.md` für die lokale Installation, `docs/lokal-starten.md` für Start mit Beispieldaten und das Ausprobieren offener Pull Requests.
5. In der Liste „Reihenfolge“ gibt es zwei Stränge mit je einer Markierung **← als Nächstes**. Ohne andere Ansage von Sebastian mit Strang 1 weitermachen, für Strang 2 sagt er, wann er Zeit für eine Abstimmung hat. Nach jedem erledigten Schritt im selben Pull Request abhaken und die Markierung weitersetzen.
6. Issues werden nur umgesetzt, wenn sie in der Reihenfolge dran sind **und** das Label `geklärt` tragen. Fehlt das Label, zuerst den Skill `grill-me` anbieten. Direkt vor dem Start die Abhängigkeiten auf GitHub prüfen.

Arbeit erfolgt auf einem eigenen Branch je Thema, Pull Requests gehen gegen `main` von `sebivtt/scout-participant-management`.

### Zusammenarbeit mit dem Projektverantwortlichen

- Sebastian ist kein Programmierer. Erklärungen sind deutsch, in Alltagssprache und ohne Fachjargon. Fachbegriffe werden beim ersten Auftreten erklärt.
- Terminal-Anleitungen gehen Schritt für Schritt: genau ein Befehl pro Schritt, dazu, was danach zu sehen sein sollte. Er arbeitet auf einem Mac, das Projekt liegt unter `~/Projekte/scout-participant-management`.
- Er prüft und übernimmt Pull Requests auf GitHub, den Code selbst liest er nicht. Die Beschreibung eines Pull Requests ist deshalb sein wichtigstes Werkzeug (siehe `CONTRIBUTING.md` Abschnitt 6).
- Er möchte ehrlich hören, was nicht funktioniert und welche Fehler die KI selbst gemacht hat.
- Fachliche Fragen und Prioritäten entscheidet er. Technische Fragen entscheidet die KI und begründet sie.

## Regeln für die Reihenfolge

- **Zwei Stränge laufen parallel:** Strang 1 (Technik, Issues) und Strang 2 (Abstimmung der Abläufe). Je Strang ist höchstens ein Pull Request gleichzeitig offen. Innerhalb eines Strangs beginnt der nächste Pull Request erst, wenn der vorige in `main` ist. Pull Requests werden nie aufeinander aufgebaut (PR #12 landete sonst im falschen Branch). Pull Requests aus Strang 2 ändern nur `docs/ablaeufe/`, `docs/entscheidungen.md` und in diesem Dokument ihren eigenen Haken unter „Strang 2“ sowie die Liste „Schon gesammelte Fragen“.
- **Neue Fehler:** Ein Fehler kommt direkt nach dem laufenden Pull Request dran (nach `grill-me`), wenn er eine dieser Bedingungen erfüllt: Auswirkung „Blockiert“, er liegt im Bereich des nächsten Updates, oder er könnte durch eine KI-Änderung entstanden sein. Alle anderen neuen Issues gehören in Schritt 6 und werden dort nach Auswirkung bzw. Wichtigkeit einsortiert.
- **Anforderungen warten auf die Abstimmung ihres Ablaufs** (Entscheidung „Abstimmung aller Funktionen und Abläufe vor Phase 4“ vom 15.10.2026, genauer gefasst am 16.10.2026). Bei jeder Anforderung in Schritt 6 steht, auf welchen Ablauf sie wartet. Ist er noch nicht abgestimmt, wird sie übersprungen und kommt dran, sobald er es ist. Fehler warten nicht, außer bei ihnen steht ausdrücklich, dass sie eine fachliche Frage aus der Abstimmung brauchen. Die Pop-ups (#38 bis #42) ändern nur die Darstellung, nicht Funktionen oder Inhalte, und warten deshalb nicht.
- **Rauchtests:** Macht ein Pull Request einen vorher grünen Rauchtest rot, wird das vor der Übernahme behoben oder im Pull Request begründet. Rotes, das schon vorher rot war, wird ein Issue. GitHub sperrt die Übernahme nicht automatisch.
- **Fehler und Anforderungen stehen nur als Issue auf GitHub,** nicht in diesem Dokument (Skill `issue-anlegen`). Technische Schritte ohne sichtbare Wirkung für Nutzende (Updates, Prüfregeln, Aufräumen) stehen hier. Die Liste „Vor dem ersten Echtbetrieb“ wird zu Issues, sobald sie nach vorne rückt.

## Reihenfolge

### Strang 1: Technik und Issues

1. **Rauchtests für das Frontend.** Rauchtests sind automatische Klicktests in einem echten Browser: Jede Seite einmal öffnen und den wichtigsten Ablauf einmal durchklicken, um grobe Brüche sofort zu sehen. Ohne sie lässt sich nach den riskanten Versionssprüngen nicht prüfen, ob noch alles geht. Das Frontend hat heute keinen einzigen Test. Werkzeug und Aufbau sind abgestimmt (Entscheidung „Rauchtests: Werkzeug und Aufbau“ vom 16.10.2026). Drei Pull Requests:
   - [x] 1a. Beispieldaten und Anleitung „Tool lokal mit Beispieldaten starten“ (dieselben Beispieldaten nutzen die Rauchtests) (PR #59)
   - [x] 1b. Jede Seite lädt ohne Programmfehler, dazu die Prüfung auf GitHub (PR #61)
   - [x] 1c. Anmeldeablauf mit allen Pflichtpunkten (siehe „Vorarbeit für die Rauchtests“), alles in einem Pull Request (Entscheidung vom 17.10.2026) (PR #62)
2. [x] **#37** „Mich selbst anmelden“ und Reise-Dialog erscheinen mittig, geklärt mit `grill-me` am 17.10.2026 (PR #65).
3. **Riskante Versionssprünge im Frontend** (Updates von Bausteinen, auf denen die Oberfläche aufbaut), einzeln, je ein Pull Request mit Rauchtests und Klickliste, in dieser Reihenfolge (siehe „Vorgehen für künftige Updates“):
   - [x] `quill`, der Texteditor in Formularen (über `@vueup/vue-quill`, ggf. Ersatz). Zuerst, weil es die einzige verbliebene Sicherheitslücke in Code ist, der im Browser läuft. (PR #68)
   - [x] Vite 2.9 → 8, das Werkzeug, das die Oberfläche baut und lokal startet. Dabei die unbenutzten Pakete `@vue-leaflet/vue-leaflet` und Vitest entfernt (Entscheidung vom 19.10.2026). (PR #82)
   - [x] `yarn dev` installiert vor dem Start selbst die passenden Pakete. Eingeschoben am 19.10.2026: Nach PR #68 lief auf Sebastians Mac neuer Code mit dem alten Quill 1, weil nach `git pull` niemand `yarn install` aufrief (daraus entstanden #79 und #81). Das soll bei den folgenden Updates nicht wieder passieren (Entscheidung vom 19.10.2026). (PR #83)
   - [ ] **← als Nächstes:** Pinia, der Zwischenspeicher der Oberfläche für geladene Daten
   - [ ] vue-router, die Navigation zwischen den Seiten
   - [ ] Tailwind, die Gestaltungsregeln (Farben, Abstände, Schriften). Zuletzt, weil es das Aussehen ändert: Sebastian prüft das Aussehen, und direkt danach folgen die Pop-ups, sodass er das neue Aussehen einmal statt zweimal anschauen muss.
4. **Technik nach den Updates**, je ein Pull Request, in dieser Reihenfolge (Entscheidung vom 19.10.2026):
   - [ ] **Tests für einzelne Funktionen der Oberfläche** mit einer aktuellen Fassung von Vitest, dem Testwerkzeug von Vite. Bisher prüfen im Frontend nur die Rauchtests im Browser. So lassen sich Regeln wie die Berechnung des Enddatums beim Anlegen einer Veranstaltung (#80) in Sekunden prüfen, wie mit `pytest` im Backend. Zuerst, damit die Behebungen beim eslint-Schritt nach `CONTRIBUTING.md` Abschnitt 3 eigene Tests bekommen können. Dabei das alte, nie benutzte Cypress entfernen (Entscheidung „Rauchtests: Werkzeug und Aufbau“ vom 16.10.2026), samt der dann überflüssigen Angabe `CYPRESS_INSTALL_BINARY=0` (im Skript `predev`, in `README.md`, `docs/lokal-starten.md`, `docs/arbeitsumgebung.md` und den Abläufen auf GitHub). Vitest ist ein neues Paket, also mit Begründung (Abschnitt 5).
   - [ ] **eslint in die automatische Prüfung auf GitHub** (eslint prüft den Code der Oberfläche auf typische Fehler, so wie ruff im Backend), dazu:
     - **#43** (drei Fenster stürzen ab), entdeckt mit der Regel `no-undef`. Die Regel für `.vue`-Dateien einschalten.
     - Technisches Aufräumen, je mit Klickprüfung. Die Einzelheiten sind für die umsetzende KI:
       - `views/newRegister/Container.vue`: `nextLink` liefert als Rückfall den ungültigen Seitennamen „Custom“, `console.log(routeObj)` läuft bei jeder Änderung.
       - `components/stepper/StepperNavSmall.vue`: `:key="step.name"` ist bei mehreren Zusatzschritten doppelt (alle heißen „Custom“), besser die Kennung des Schritts.
       - `src/router.ts` (Wache vor jedem Seitenwechsel): Ohne Login ruft sie die Anmeldung auf, ohne den Seitenwechsel abzuschließen. vue-router meldet dann im Entwicklungsmodus „Invalid navigation guard“ (nur in der Fehlerkonsole, gefunden am 16.10.2026). Die Prüfung auf `landing` greift nie, weil im `some` das `return` fehlt.
       - Drei Stellen aus dem übernommenen Code (2023/2024), gefunden als Vue-Warnungen der Rauchtests am 17.10.2026. Sie sind vermutlich sichtbar und stehen auf Sebastians Wunsch hier statt als Issue. Danach müssen die Warnungen in `rauchtests/results/pages.jsonl` fehlen:
         - `group/views/detail/tabs/Requests.vue`: lädt den Baustein für die leere Liste als `ListItemEmpty`, benutzt ihn aber als `PersonListItemEmpty`. Bei leerer Liste fehlt vermutlich der Hinweis.
         - `event/components/statistic/summary/RegSearchList.vue`: benutzt `PlusIcon` und `FolderOpenIcon`, ohne sie zu laden (Seite „Auswertung“, Reiter „Anmeldungen“).
         - `landing/views/MapMain.vue` und `event/components/statistic/map/DetailList.vue`: rufen `useRoute()` in `mounted()` auf statt in `setup`. Vue warnt „inject() can only be used inside setup()“.
       - `components/stepper/StepFrame.vue`: `isLoading` ist zugleich Prop und eigener Wert `ref(false)`. Die Knöpfe zeigen deshalb nie den Ladezustand, obwohl neun Seiten ihn übergeben. Den eigenen Wert entfernen.
       - Tote Dateien löschen: `modules/event/views/newRegister/module/Person.vue`, `modules/help/store/index.ts`.
       - Ungenutzter Code mit fehlender Variable `eventData` in `event/components/statistic/payments/CashItem.vue`.
       - Im eingefrorenen Modul `message` fehlen vier Symbole (`views/tabs/AllMessages.vue`): nur so weit, dass die Prüfung läuft.
     - Nach PR #26: 260 Fehler und 2.795 Warnungen (`yarn lint`, Aufschlüsselung in `docs/qualitaet.md`). Zuerst die Fehler, Warnungen schrittweise. Die vorübergehend gelockerten Stufen in `eslint.config.mjs` bewusst einzeln schärfer stellen. Die Regel `comma-dangle` fällt mit eslint 11 weg. Dazu eine automatische Prüfung der Frontend-Pakete auf Sicherheitslücken wie `pip-audit` im Backend, `CONTRIBUTING.md` Abschnitt 5 dann ergänzen.
5. **Pop-ups** (Sammel-Issue #35), der Reihe nach: [ ] #38 → [ ] #39 → [ ] #40 → [ ] #41 → [ ] #42. #41 und #42 warten zusätzlich auf #43. #41 braucht vorher eine kurze Nachklärung mit `grill-me`: Wohin kommt man nach dem Anlegen einer Gruppe? Die Frage stand im alten Fahrplan und wurde bei der Klärung von #35 nicht gestellt.
6. **Fehler und Anforderungen aus den Issues.** Erst Fehler, dann Anforderungen „Wichtig“, dann „Wäre schön“. Innerhalb einer Gruppe in dieser Reihenfolge:
   - Fehler: [ ] #69 ungefiltertes HTML in Texten (Sicherheitslücke, vor dem ersten Echtbetrieb nötig) → [ ] #48 abgelaufener Login → [ ] #47 Knopf „zusammenfassen“ → [ ] #44 Fehler als Erfolgsmeldung → [ ] #45 Bausteinposition → [ ] #34 nur Zahlen in Mengenfeldern → [ ] #46 Zahlung ohne Betrag → [ ] #64 Rückreise-Uhrzeit → [ ] #66 Speichern direkt nach der Postleitzahl → [ ] #63 Fehlanfrage im Dialog „Stammesmitglied anmelden“ → [ ] #70 Listen ohne Punkte und Nummern (vermutlich Tailwind, spätestens mit dem Tailwind-Update in Schritt 3 erledigen) → [ ] #51 „bestätigt“ (wartet auf die Abstimmung „Anmelden“) → [ ] #60 verantwortliche Person hinzufügen (wartet auf die Klärung der Rollen)
   - Wichtig: [ ] #49 Absenden ganz oder gar nicht (wartet auf „Anmelden“) → [ ] #50 verständliche Fehlermeldungen (wartet auf „Anmelden“ und #49) → [ ] #53 Orientierung im Anmeldeablauf (wartet auf „Anmelden“) → [ ] #52 Fristen im Frontend (wartet auf „Veranstaltung anlegen“) → [ ] #32 eindeutige technische Namen (wartet auf „Veranstaltung anlegen“)
   - Wäre schön: [ ] #54 Texte als Fragen (wartet auf „Anmelden“) → [ ] #55 Stammauswahl (wartet auf „Anmelden“) → [ ] #57 Adressfelder (wartet auf „Anmelden“) → [ ] #30 Mengen begrenzen (wartet auf „Anmelden“) → [ ] #33 Namen für Datentypen (wartet auf „Veranstaltung anlegen“) → [ ] #56 Hinweis E-Mail-Feld (wartet auf „Konto und persönliche Daten“) → [ ] #71 weitere Formatierungen im Texteditor, vor allem Bilder (wartet auf „Veranstaltung anlegen“ und #69) → [ ] #84 Tool wie eine App auf den Startbildschirm legen (wartet auf „Konto und persönliche Daten“; dort mitklären, was auf dem Handy gespeichert bleiben darf, siehe „Browserspeicher“ unter „Vor dem ersten Echtbetrieb“) → [ ] #85 schneller laden (wartet auf keinen Ablauf, ändert nur die Geschwindigkeit)
7. **Qualität II, Rest** (siehe Abschnitt „Qualität II“): [ ] 2b Feldnamen → [ ] 1c Prüfregeln → [ ] 3 Keycloak-Abgleich → [ ] 4a/4b (nach der Abstimmung) → [ ] N+1 auf sechs Seiten → [ ] 5 Abschluss.

### Strang 2: Abstimmung der Funktionen und Abläufe

Beginnt jetzt, parallel zu Strang 1 (Entscheidung vom 16.10.2026). Ein Ablauf pro Sitzung, je Ablauf ein Pull Request. Vorgehen im Abschnitt „Abstimmung der Funktionen und Abläufe“.

1. [ ] **← als Nächstes: Rollen und Rechte** (Entscheidung „Rollen klären, bevor Rechte geändert werden“ vom 17.10.2026): welche Rollen es gibt, was jede darf, wer sie wann und wie erhält, wie die Oberfläche dazu passt (z. B. was Suchen und Auswahllisten zeigen). Ergebnis ist die Grundlage für die Tabellen „wer darf was“ in den folgenden Abläufen. Betrifft #60.
2. [ ] Anmelden (inkl. T-Shirts und Lunch Pakete als Standard, Buchungsoption, „bestätigt“ für #51, offene Fragen aus #30)
3. [ ] Veranstaltung anlegen (inkl. Reiter „Module“ und #33)
4. [ ] Anmeldung ändern
5. [ ] Kasse und Auswertung
6. [ ] Gruppen verwalten
7. [ ] Konto und persönliche Daten

### Vor dem ersten Echtbetrieb

Es gibt keinen festen Termin (Entscheidung vom 16.10.2026). Diese Punkte kommen vor dem ersten Einsatz mit echten Anmeldungen und werden dann zu Issues.

Datenschutz:
- Namensansicht für Teilnehmende: Sie sehen von ihrer Gruppenanmeldung nur die Namen (Entscheidung „Wer sieht welche Anmeldungen“).
- Zusatzfelder pro Veranstaltung, z. B. die Ausweisnummer, statt fester Felder (Entscheidung „Zusatzfelder pro Veranstaltung“).
- Browserspeicher: Die Eingaben der Anmeldung, auch Daten von Kindern, liegen bis zum Absenden dauerhaft im Browser (`frontend/src/modules/event/store/register.ts` mit `persist: true`). Nach dem Absenden oder Abmelden löschen oder gar nicht dauerhaft speichern.
- API-Logger: Er speichert jede Anfrage samt Inhalt dauerhaft in der Datenbank. Inhalte nicht speichern oder nach kurzer Frist löschen.
- Löschfristen für Anmeldungen nach Veranstaltungsende (fachliche Entscheidung nötig).

Betrieb:
- Hosting: vorerst günstiger eigener Server, später ggf. AWS beim Verband (Projektverantwortlicher).
- Dockerfile für den Echtbetrieb. Das alte Setup in `backend/` (Dockerfile, docker-compose.yml, start.sh) ist ungeprüft. `manage.py check --deploy` verlangt dort `SECURE_SSL_REDIRECT=True`, falls der vorgeschaltete Webserver nicht auf HTTPS umleitet.
- Begrenzung der Anfragen pro Minute für die öffentlichen Adressen: Registrierung, Kontaktformular, Prüfung von Benutzername und E-Mail (verraten, ob eine Adresse registriert ist).
- `anonymise_data` überschreibt ohne Rückfrage alle Personendaten. Sicherung gegen versehentlichen Aufruf im Echtbetrieb.
- Kleinste nötige Rollen für das Keycloak-Dienstkonto (getestet nur mit `realm-admin`), mit dem Verbands-Admin.
- Lizenz des Projekts, mit den ursprünglichen Entwicklern.

### Irgendwann, ohne festen Platz

- TypeScript 7: erst, wenn `typescript-eslint` es unterstützt (Stand 15.10.2026: nur bis 6.0). `moduleResolution: bundler` in `tsconfig.json` ist vorbereitet.
- `django-stdimage` ist veraltet, Nachfolger `django-pictures`.
- Fachliche Fragen für die Abstimmung, die keinem Ablauf zugeordnet sind: Beim Anmelden kann man jeden Stamm wählen, nicht nur den eigenen (PR #3). Feinabstimmung der Rechte des Anmeldeteams, Staff hat heute überall Admin (PR #2). Zentrale Verwaltung der Veranstaltungsorte (Entscheidung „Veranstaltungsorte“).
- Eingefrorene Module: `food` und `inspi` sind abgeschaltet, `messaging` und `notifications` bleiben vorerst. Ob sie abgesichert zurückkommen, klärt die Abstimmung (Projektverantwortlicher).
- Phase 6: eigene Ideen des Projektverantwortlichen. Phase 7: andere im Verband nach ihrem Bedarf fragen.

### Bewusst nicht

- „Zu komplexe Funktionen aufteilen“ als eigener Schritt: Das regelt schon die Pfadfinderregel (`CONTRIBUTING.md` Abschnitt 7).
- Weiterleitung nach dem Speichern im eingefrorenen Kontaktformular-Modul (steht in `docs/qualitaet.md`): Funde in eingefrorenen Modulen werden nur dort festgehalten, nicht behoben (Entscheidung vom 15.10.2026).
- Die offenen Fragen „Klicktest zu PR #11“ und „Person aus einer Anmeldung löschen“: gestrichen am 16.10.2026. Das prüfen künftig die Rauchtests und die Abstimmung. Fällt etwas fälschlich gesperrt auf, wird es ein Issue.

## Vorarbeit für die Rauchtests

- **Rahmen (entschieden am 16.10.2026):** Docker ist auf Sebastians Mac vorhanden. Wichtigster Ablauf ist die Standard-Anmeldung über alle Schritte bis zum Absenden. Rote Rauchtests sperren die Übernahme nicht automatisch, siehe „Regeln für die Reihenfolge“.
- **Werkzeug Playwright, eine Stufe mit echtem Backend und Keycloak 26.7,** in der Cloud und auf GitHub (Entscheidung „Rauchtests: Werkzeug und Aufbau“ vom 16.10.2026). Playwright ist ein neues Paket, also mit Begründung (`CONTRIBUTING.md` Abschnitt 5). Die Version an die in der Cloud installierte anpassen (1.56, Browser unter `/opt/pw-browsers`). Liste der Seiten und ihrer Anfragen: `docs/schnittstellen.md`. Ganzes Tool in der Cloud starten: `docs/arbeitsumgebung.md`.
- **Stand nach 1c:** Die Rauchtests liegen in `rauchtests/` (Anleitung dort in `README.md`): `tests/seiten.spec.ts` öffnet jede Seite, `tests/anmeldeablauf.spec.ts` klickt die Abläufe mit allen Pflichtpunkten unten durch und räumt seine Daten selbst auf. GitHub lädt das Keycloak-Abbild. Auf GitHub laufen sie nur mit dem Label `rauchtests` (Entscheidung „Rauchtests: nur bei Bedarf auf GitHub“ vom 17.10.2026).
- **Pflichtpunkte** aus Fehlern, die nur durch Klicken auffielen, alle abgedeckt mit 1c:
  - Neue Anmeldung mit „Mich selbst anmelden“ und einem Stammesmitglied (Issue #19), eine schon angemeldete Person wird sofort gemeldet, eine gespeicherte Person bearbeiten ohne Dublettenmeldung.
  - Lagerbeitrag anlegen und ändern sowie Ort ändern, danach auf der Veranstaltung bleiben. Fehlerfall: Ort ändern, der auch von einer fremden Veranstaltung genutzt wird, zeigt eine Fehlermeldung und lädt nicht neu (Issue #20).
  - Im Anmeldeablauf zwei Personen hinzufügen, jede über „ändern“ öffnen (der Dialog zeigt die richtige Person), eine umbenennen (sie steht danach einmal mit neuem Namen da), beide löschen, eine neue hinzufügen (sie erscheint sofort) (Issue #23).
  - Mit einer Veranstaltung aus der Standardvorlage den ganzen Anmeldeablauf durchklicken, über Anreise, Rückreise, T-Shirts, Anmerkungen und Lunch Pakete bis zur Zusammenfassung, dazu der Reise-Dialog mit fehlender Angabe (zeigt „Bitte Felder überprüfen“, übernimmt nichts) (Issue #25).
  - Über die Schrittanzeige von „Lunch Pakete“ zurück zu „T-Shirts“ springen, die Antworten sind noch da und werden alle abgeschickt. Das gilt, solange die Standardvorlage beide Schritte enthält, sonst mit einer Veranstaltung, die sie zusätzlich wählt.
  - Testdaten wie eine echt angelegte Veranstaltung: erledigt mit `python manage.py load_sample_data` (PR #59, Rollen der Testkonten in `docs/lokal-starten.md`). 1c hat ergänzt: „Beispielfahrt“ und „Fremdes Lager“ an einem gemeinsamen Ort (#20), zwei Stammesmitglieder für `teilnehmer` und dessen Stamm „Falken“ als Gruppenbaum in Keycloak (`dev/keycloak-setup.sh`).

## Vorgehen für künftige Updates

Für alle Versionssprünge im Frontend (Entscheidungen vom 15.10.2026):

- Direkte Pakete gezielt einzeln (`yarn upgrade axios@1.20.0`), nie pauschal `yarn upgrade`, nie `npm audit fix --force`, kein Wechsel auf npm.
- Mitgelieferte Pakete über `resolutions` in `package.json`, jeweils auf die niedrigste behobene Version innerhalb der Hauptversion. Vorher prüfen, ob das übergeordnete Paket die behobene Version schon selbst verlangt: Dann ist keine Vorgabe nötig.
- Was ein aktualisiertes Paket zwingend mitbringt, darf seine Hauptversion verlassen. Neue Hauptversionen und neue Pakete werden im Pull Request genannt und begründet.
- Zwangsvorgaben (`resolutions`) bei jedem Update der übergeordneten Pakete prüfen, sonst verletzen sie deren Anforderungen still. (Die Vorgaben aus PR #16 sind mit PR #26 entfernt, weil sie Vue 3.5 eine zu alte `postcss`-Fassung aufgezwungen hätten.)
- Prüfen: `yarn build`, eslint und `npx tsc --noEmit` vorher und nachher vergleichen, Backend-Tests, `yarn audit --groups dependencies --summary`, Änderungsprotokoll des Pakets gegen unsere Aufrufe lesen.
- Im Browser vorher und nachher vergleichen: Rauchtests vor und nach dem Update laufen lassen (`rauchtests/README.md`). Die Datei `rauchtests/results/pages.jsonl` enthält je Seite auch Vue-Warnungen, beide Fassungen vergleichen. Dazu die betroffenen Abläufe von Hand. Pull Requests mit riskanten Updates tragen immer das Label `rauchtests`.

Stand der Versionen am 16.10.2026: Vite 2.9 (aktuell 8), Vue 3.5 (3.5), vue-router 4.0 (5), Pinia 2 (4), Tailwind 3 (4), TypeScript 6.0 (7), eslint 10 (10). Bekannte Sicherheitslücken nach PR #26: 169, davon 1 in den Programmpaketen (`quill`), der Rest in Entwicklungswerkzeugen (Verlauf in `docs/qualitaet.md`). Nach dem Update von `quill` am 17.10.2026 (`@vueup/vue-quill` 1.5.5, `quill` 2.0.2): 168, davon 0 in den Programmpaketen. `quill` 2.0.3 hat eine eigene, unbehobene Lücke und ist von `@vueup/vue-quill` ausgeschlossen. Erst eine neue Fassung von `@vueup/vue-quill` oder `quill` 2.0.4 hebt diese Grenze auf. Nach dem Update von Vite auf 8.3 am 19.10.2026 (mit `@vitejs/plugin-vue` 6, ohne Vitest): 125, davon 0 in den Programmpaketen.

## Abstimmung der Funktionen und Abläufe

Vereinbart am 15.10.2026. Ziel: Für jeden Ablauf ist abgestimmt, wer was darf und wann. Ohne diese Grundlage muss die KI bei Rechten und Fristen raten oder einzeln nachfragen.

**Vorgehen:**
1. Die KI erstellt den Ist-Stand aus dem Code, ein Dokument pro Ablauf in `docs/ablaeufe/`. Jedes Dokument enthält:
   - ein Ablaufdiagramm,
   - eine Tabelle „wer darf was in welcher Phase“, also vor dem Anmeldestart, während der Anmeldung, nach dem Anmeldeschluss und nach der Änderungsfrist,
   - eine Liste der Stellen, die vermutlich nicht so gewollt sind.
2. Sebastian geht die Abläufe einzeln durch und entscheidet pro Zeile: so lassen oder ändern. Das Ergebnis steht als Soll im Dokument und in `docs/entscheidungen.md`.
3. Jede abgestimmte Regel bekommt einen Test, sobald sie umgesetzt wird. Weicht das Soll vom Ist ab, wird daraus ein Issue.

**Schon gesammelte Fragen:**
- Rollen und Rechte (erster Punkt in Strang 2): Sebastian hat Änderungswünsche am ganzen Rollenaufbau. Dazu gehören die schon gesammelten Fragen zu Rechten weiter unten, die Feinabstimmung der Rechte des Anmeldeteams (Abschnitt „Irgendwann“) und die Suche in #60.
- Anmelden: Welche Schritte und Abfragen bekommt jede neue Veranstaltung standardmäßig, welche wählt die Veranstaltungsleitung zusätzlich? Heute gibt die Standardvorlage „T-Shirts“ und „Lunch Pakete“ immer mit, das soll nicht so bleiben (Entscheidung vom 16.10.2026).
- Anmelden: Wann soll die Buchungsoption gesperrt sein? Heute ist die Sperre im Anmeldeablauf immer aus (`views/newRegister/module/Participants.vue`, `blockBookingOption.value && …` im Template), und Stammesmitglieder landen ohne Buchungsoption in der Liste.
- Anmelden: Wann gilt eine Anmeldung als bestätigt (#51)?
- Anmelden: offene Fragen aus #30 (welche Personen zählen, Verhalten beim nachträglichen Entfernen).
- Veranstaltung anlegen: Der Reiter „Module“ ist unverständlich und soll grundlegend überarbeitet werden (Rückmeldung vom 14.10.2026), zusammen mit #33.
- Wer darf welche Veranstaltung sehen? Heute liefert `/event/event-read/` jeder eingeloggten Person jede Veranstaltung.
- Wer darf in der geplanten zentralen Ortsverwaltung Orte verwalten? Was passiert mit Orten, die angelegt, aber keiner Veranstaltung zugeordnet wurden?
- Darf die Ansichtsgruppe Excel-Listen erzeugen? Heute ja, weil das eine Form der Auswertung ist.
- Sollen beim Zusammenlegen zweier Anmeldungen auch deren Bewertungen (und Workshops, falls das Modul wieder eingebunden wird) übernommen werden? Heute gehen sie mit der gelöschten Anmeldung verloren.

## Qualität II: Prüfung auf typische KI-Fehler

**Auftrag:** Den gesamten Code, den übernommenen und den von KI geänderten, auf typische Fehler von KI-generiertem Code prüfen. Grundlage ist der Artikel <https://scand.de/unternehmen/blog/why-ai-generated-code-doesnt-work-and-how-to-fix-it/>. Gefundene Probleme werden als Tests oder als automatische Prüfung festgehalten. Noch offene Fehler werden als `xfail(strict=True, raises=…)` mit genau der erwarteten Fehlerart markiert (Vorbild: `tests/test_abfragen.py`). Was sich nicht automatisch prüfen lässt, kommt als Regel in `CONTRIBUTING.md`. Ein Ergebnisabschnitt kommt in `docs/qualitaet.md`.

Die Tabelle fasst die Fehlerarten des Artikels vollständig zusammen und übersetzt sie auf dieses Projekt. Der Artikel muss nicht erneut gelesen werden.

| Fehlerart laut Artikel | Was hier konkret zu prüfen ist | Heute schon abgedeckt? |
| --- | --- | --- |
| Nur der Normalfall ist bedacht | Leere Listen, fehlende Felder, doppelte Anfragen, gleichzeitige Änderungen, Keycloak oder Mail nicht erreichbar, Fristen genau auf der Grenze | teilweise (Fristen-Grenzen, Keycloak-Ausfall bei Rechten) |
| Fehlende Fehlerbehandlung, stille Fehler | `except: pass`, verschluckte Fehler, Rückgabe `None` statt Fehlermeldung, Frontend-Meldungen, die den echten Fehler verdecken | teilweise (ruff E722; 7 Altlasten mit `# noqa: E722` sind ein konkreter Startpunkt) |
| Fehlende Eingabeprüfung | Serializer ohne Prüfung, Datei-Uploads (Excel-Import), Längen und Formate, Rechte nur im Frontend | teilweise (Datumsreihenfolge, Rechte-Tests) |
| Sicherheitslücken | SQL über `raw()` oder `extra()`, Zugangsdaten im Code oder in `.env.example`, offene Endpunkte (`AllowAny`), Massenzuweisung über `fields = '__all__'`, fehlende Begrenzung öffentlicher Endpunkte | teilweise (pip-audit, Login-Pflicht als Standard, alle `fields = '__all__'` bewertet in 1b-2) |
| Erfundene Funktionen oder falsche Versionen | Aufrufe von Bibliotheksfunktionen, die es in der installierten Version nicht gibt (v. a. python-keycloak, DRF), Frontend-Pakete | nein (nur indirekt über Tests) |
| Falsche Annahmen über Datenstrukturen | Antworten von Keycloak (Felder optional?), Frontend erwartet andere Feldnamen als das Backend liefert, `None` vs. leere Liste | nein |
| Lokal richtig, passt nicht ins Ganze | Doppelte Logik an mehreren Stellen (z. B. Rechteprüfung, Datumsprüfung), Regeln aus `docs/entscheidungen.md` nicht überall umgesetzt | teilweise (zwei Fälle in PR #7 gefunden) |
| Zu einfach oder zu kompliziert | Übersprungene Details, unnötige Abstraktionen, tote oder doppelte Funktionen | teilweise (ruff C901) |
| Schwer nachvollziehbar | Annahmen nicht dokumentiert, keine Docstrings | teilweise (Docstring-Quote siehe `docs/qualitaet.md`) |

**Schritte**, jeweils ein eigener Pull Request (Prüftiefe und Abgrenzung siehe `docs/entscheidungen.md`, 15.10.2026):
- [x] 1a. Pauschale `# noqa` aufgeräumt (PR #9).
- [x] 1b-1. Sicherheitsregeln (ruff `S`) eingeschaltet, Funde behoben (PR #10).
- [x] 1b-2. Alle `fields = '__all__'`, schreibenden Schnittstellen und öffentlichen Adressen bewertet, 20 Lücken geschlossen (PR #11).
- [x] 1d. Essensplanung und Programmideen abgeschaltet (PR #12/#13).
- [x] 2a. Frontend-Aufrufe mit Backend-Adressen abgleichen, automatisch (PR #14).
- [ ] 1c. Weitere Regelgruppen (`DJ`, `PERF`, `RET`, `W605`, pauschales `except Exception`) mit Zählung und Bewertung, dazu die 7 Altlasten mit `except:`. Bekannte Treffer: `authentication/views.py` Passwortprüfung (`W605`, ungültige Escape-Sequenz, funktioniert heute noch); `anmelde_tool/registration/signals.py` besteht nur aus auskommentiertem Code (klären, ob die Mail „Anmeldung angelegt“ fehlt oder anderswo verschickt wird). Noch aus 1b: `add_state` bricht bei einem unbekannten Bundesland mit einem unverständlichen Fehler ab.
- [ ] 2b. Feldnamen abgleichen: Liest das Frontend Felder, die das Backend nicht liefert? Achtung: Das Backend wandelt Feldnamen automatisch um (`first_name` ↔ `firstName`, Paket `djangorestframework-camel-case`). Nach den Rauchtests, weil diese viele Feldfehler direkt zeigen.
- [ ] 3. Genutzte python-keycloak-Methoden mit der installierten Version (7.1.1) abgleichen, mit Livetest gegen Keycloak 26.7.
- [ ] 4a. Randfälle und Fehlerbehandlung beim Anmelden und Ändern mit Tests absichern. Erst nach der Abstimmung „Anmelden“ und „Anmeldung ändern“.
- [ ] 4b. Dasselbe für Rechte und Gruppen, dazu doppelte Logik an mehreren Stellen. Erst nach der Abstimmung aller Abläufe, weil Rechte in jedem Ablauf vorkommen.
- [ ] N+1-Abfragen auf sechs Seiten beheben: Auswertung, Meine Anmeldungen, Kassenliste, Gruppenliste, Veranstaltungsübersicht, Meine Einladungen. Ist eine Seite behoben, meldet `tests/test_abfragen.py` das, und die `xfail`-Markierung wird entfernt.
- [ ] 5. Abschluss: Tabelle oben vollständig beantworten, Ergebnisabschnitt in `docs/qualitaet.md`, neue Review-Regeln in `CONTRIBUTING.md`. Dabei die Docstring-Quote in `docs/qualitaet.md` angleichen: Die Kurzfassung nennt 8 %, die Tabelle 13 %.

**Fertig ist die Phase**, wenn jede Zeile der Tabelle mit „abgedeckt“ oder „bewusst nicht, weil …“ beantwortet ist und `docs/qualitaet.md` einen Ergebnisabschnitt hat.

**Hinweise:** Erst reproduzieren, dann isolieren und Annahmen prüfen, erst danach ändern. Neue Werkzeuge nur mit Begründung (`CONTRIBUTING.md` Abschnitt 5). Kleine, thematische Pull Requests.

## Erledigt

| Phase oder Schritt | Pull Requests |
| --- | --- |
| Fundament: gemeinsames Repository, Backend ohne Keycloak startfähig, Testgerüst | Vorarbeit, #1 |
| Rechte: Gruppenrechte im Tool statt in Keycloak | #2 |
| Sicherheit und Fehler: Login-Pflicht als Standard | #3, #4 |
| Fristen und Sperren (nur Backend, Bedienelemente fehlen: #52) | #5 |
| Modernisierung Backend: Django 5.2, pip-audit | #6 |
| Qualität: Regeln, ruff, Dokumentation, Messung | #7 |
| Qualität II, Schritte 1a, 1b-1, 1b-2, 1d, 2a | #9 bis #14 |
| Frontend: Sicherheitsupdates innerhalb der Hauptversionen, TypeScript 6 und eslint 10, `uuid` 14, Vue 3.5 | #16, #17, #18, #26 |
| Frontend, riskante Updates: `quill` 2 (Texteditor), Vite 8; Pakete automatisch beim Start | #68, #82, #83 |
| Fehler aus Issues: #19, #20, #23, #25, #37 | #21, #22, #24, #27, #65 |
| Arbeitsweise: Vorlagen für Issues, Skills `issue-anlegen` und `grill-me` | #31, #36 |
| Rauchtests 1a: Beispieldaten, Anleitung „lokal starten“, Keycloak in der Cloud | #59 |
| Rauchtests 1b: jede Seite lädt, Prüfung auf GitHub per Label | #61 |
| Rauchtests 1c: Anmeldeablauf mit allen Pflichtpunkten | #62 |
| Doku und Übergaben | #8, #15, #28 |

Einzelheiten stehen in den Beschreibungen der Pull Requests und in `docs/qualitaet.md`.
