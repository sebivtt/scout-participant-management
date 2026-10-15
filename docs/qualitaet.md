# Qualitätsbericht

Stand 15.10.2026. Ausgangsmessung des übernommenen Codes nach Einführung der Regeln aus `CONTRIBUTING.md`. Dieser Bericht wird bei größeren Schritten fortgeschrieben. Die Zahlen erzeugt `backend/tools/qualitaet_messen.py`; dort steht auch, was genau gezählt wird.

## Kurzfassung

Der Code funktioniert und ist seit Phase 1 bis 3 gegen Sicherheitslücken und die wichtigsten Fehler abgesichert. Drei Schwächen bleiben:

1. **Effizienz:** Sechs zentrale Seiten lösen pro Listeneintrag neue Datenbankabfragen aus (N+1-Muster). Bei einem großen Lager wird das spürbar langsam.
2. **Verständlichkeit:** Nur 8 % der Funktionen und Klassen sind beschrieben. Vollständig beschrieben sind die Kernbereiche Rechte und Fristen (`keycloak_auth/access.py`, `anmelde_tool/event/permissions.py`, `anmelde_tool/event/deadlines.py`), der übrige übernommene Code kaum.
3. **Anmeldeablauf im Frontend:** Das Absenden besteht aus vielen Einzelanfragen, und Fehlermeldungen sind irreführend. Das ist vermutlich die Hauptursache der gefühlten Fehleranfälligkeit.

## Messwerte Backend

| Messung | Wert | Ziel | Werkzeug |
| --- | --- | --- | --- |
| Umfang | 18.360 Zeilen in 234 Dateien (ohne Migrationen und Tests) | – | – |
| Tests | 214 bestanden, 6 bekannte Probleme (`xfail`) | wächst mit jeder Änderung | pytest |
| Bekannte Sicherheitslücken in Paketen | 0 | 0 | pip-audit |
| Verstöße gegen Code-Regeln, neu | 0 | 0 (wird bei jeder Änderung geprüft) | ruff |
| Verstöße gegen Code-Regeln, Altlasten (`# noqa`) | 67 (dazu 6 gewollte Markierungen, siehe unten) | sinkt durch die Pfadfinderregel | ruff |
| Funktionen und Klassen mit Beschreibung | 184 von 1.560 (12 %) | Kernbereiche 100 %, sonst wachsend | `tools/qualitaet_messen.py` |

### Altlasten nach Art

| Regel | Anzahl | Bedeutung |
| --- | --- | --- |
| T201 | 39 | `print()` statt Protokollierung, v. a. bei der Registrierung neuer Konten und in den Keycloak-Hilfsskripten |
| F841 | 9 | Variable wird gesetzt, aber nie benutzt |
| E722 | 7 | Pauschales `except:` verschluckt jeden Fehler, auch echte Programmfehler |
| C901 | 5 | Funktion zu verschachtelt (siehe unten) |
| S110 | 2 | `try`/`except`/`pass`: dieselben Stellen wie bei E722, von der Sicherheitsregel ein zweites Mal gemeldet |
| sonstige | 5 | einzelne Importe und Kleinigkeiten (B007, 2× F401, F811, F842) |

Gewollt und keine Altlast: fünf `# noqa: F401` in den `apps.py`-Dateien, erkennbar an der Begründung nach `--`. Vier Importe registrieren Signal-Empfänger, einer meldet den Keycloak-Abgleich bei Celery an. Sie dürfen nicht entfernt werden (Test: `tests/test_signale.py`). Dazu kommt ein `# noqa: S105` in `basic/management/commands/add_users.py`: Das feste Passwort ist dort gewollt, weil der Befehl nur lokal läuft (Test: `tests/test_verwaltungsbefehle.py`).

Korrektur am 15.10.2026 (Qualität II, Schritt 1): Die erste Messung übersah 15 Markierungen ohne Regelnummer (`# noqa`). Sie schalteten auf ihrer Zeile jede Prüfung ab, auch künftig eingeschaltete. Zehn waren wirkungslos und sind entfernt. Fünf sind jetzt gezielt: vier gewollte mit Begründung und eine Altlast (`notifications/models.py`). Außerdem:
- Die Markierung in `anmelde_tool/registration/apps.py` galt bisher als gewollt, der Import meldet aber nichts an: `anmelde_tool/registration/signals.py` enthält nur auskommentierten Code. Sie zählt jetzt als Altlast.
- Eine Markierung in `notifications/apps.py` war überflüssig und ist entfernt.
- Die Markierung in den Testeinstellungen war keine Altlast und ist jetzt in `ruff.toml` geregelt.
- Zwei wirkungslose Textblöcke mit `# noqa` (Hinweise für den Editor PyCharm) sind entfernt.

ruff lässt Markierungen ohne Nummer nicht mehr zu.

### Zu komplexe Funktionen

| Funktion | Datei | Komplexität (Grenze 12) | Aufgabe |
| --- | --- | --- | --- |
| `MyMembersUploadViewSet.create` | `authentication/views.py` | 22 | Mitglieder per Excel-Datei hochladen |
| `MyOIDCAB.set_user_info` | `backend/OIDCAuthentication.py` | 16 | Kontodaten beim Login aus Keycloak übernehmen |
| `SyncKeycloakGroups.run` | `basic/helper/sync_keycloak_groups.py` | 15 | Gruppen mit Keycloak abgleichen |
| `generate_file` | `anmelde_tool/event/file_generator/file_generators.py` | 13 | Excel-Listen erzeugen |
| `recursive_group_initialisation` | `basic/helper/initialize_keycloak_scout_hierarchies.py` | 13 | Pfadfinderstruktur in Keycloak anlegen |

## Effizienz: Datenbankabfragen pro Seite

Gemessen mit `tests/test_abfragen.py`. Alle sechs Seiten sind als bekanntes Problem markiert. Wird eine repariert, meldet der Test das. Wird eine schlechter als die Werte unten, schlägt der Test sofort fehl.

| Seite | 1 Eintrag | 10 Einträge | Hochgerechnet auf 100 |
| --- | --- | --- | --- |
| Auswertung der Anmeldungen | 17 | 116 | ca. 1.100 |
| Meine Anmeldungen | 12 | 111 | ca. 1.100 |
| Kassenliste | 15 | 105 | ca. 1.000 |
| Gruppenliste | 8 | 71 | ca. 700 |
| Veranstaltungsübersicht | 9 | 45 | ca. 400 |
| Meine Einladungen | 5 | 23 | ca. 200 |

Ziel: gleich viele Abfragen bei 1 und 100 Einträgen. Die Lösung ist meist, zugehörige Daten mit einer Abfrage vorab zu laden (`select_related`, `prefetch_related`).

Keycloak wird in den aktiven Modulen jetzt höchstens einmal pro Seitenaufruf gefragt. Vorher geschah das bei jeder Rechteprüfung, also oft einmal pro Listeneintrag.

## Weitere Befunde

| Befund | Auswirkung | Vorschlag |
| --- | --- | --- |
| Das Absenden einer Anmeldung besteht aus vielen Einzelanfragen. Scheitert eine, löscht die Oberfläche die halbe Anmeldung, und klappt das nicht, bleibt sie halb bestehen. | Halbe oder doppelte Anmeldungen | Phase 4: Absenden als eine Anfrage, im Backend „ganz oder gar nicht“ |
| Fehlermeldungen beim Absenden sind fest verdrahtet („Ein Pflichtfeld fehlt“, „Stamm nicht gefunden“) und verdecken die Meldung des Backends. | Nutzende suchen den Fehler an der falschen Stelle | Phase 4 |
| Das Feld „Anmeldung bestätigt“ wird nie gesetzt. Rundmails an „bestätigte Anmeldungen“ erreichen deshalb niemanden. | Stiller Funktionsausfall | Phase 4: beim Absenden setzen, Test dazu |
| Eingaben der Anmeldung liegen bis zum Absenden im Browserspeicher, auch Daten von Kindern. | Datenschutz auf gemeinsam genutzten Geräten | Phase 5 |
| Der API-Logger speichert jede Anfrage samt Inhalt dauerhaft in der Datenbank. | Datenschutz, wachsende Datenbank | Phase 5 |
| Signal-Empfänger werden nur über unbenutzte Importe registriert. Ein Aufräumwerkzeug hatte sie beim Einführen der Regeln entfernt. | Keycloak-Abgleich und Benachrichtigungen wären still weggefallen | Behoben, Test `tests/test_signale.py` |
| Wer Veranstaltungsleitung ist und zugleich in der Ansichtsgruppe, wurde bei den Buchungsoptionen nur als Betrachter erkannt. | Leitung sah nicht alle Buchungsoptionen | Behoben, Test in `tests/test_rechte.py` |
| Das alte Startskript für den Server (`backend/start.sh`, genutzt von `backend/docker-compose.yml`) legte bei jedem Start ein Administratorkonto mit festem, öffentlich bekanntem Passwort an. Über die Verwaltung unter `/admin/` hätte sich damit jeder als Administrator anmelden können. | Vollzugriff für Fremde, falls jemand mit dem alten Startskript betreibt | Behoben (Qualität II, 1b-1): Startskript legt kein Konto mehr an, `add_users` läuft nur lokal. **Auf einer bestehenden Installation, die mit dem alten Startskript lief, existiert das Konto weiter: dort das Konto `admin` löschen oder sein Passwort ändern.** Tests in `tests/test_verwaltungsbefehle.py` |
| Der Abruf der Bundesländer zu Postleitzahlen (`add_state`) schaltete die Zertifikatsprüfung ab. | Gefälschte Antworten hätten falsche Bundesländer in die Datenbank geschrieben | Behoben (Qualität II, 1b-1), Test in `tests/test_verwaltungsbefehle.py` |
| Anmeldungen zusammenlegen: Mit sich selbst zusammengelegt wurde die Anmeldung samt Teilnehmenden gelöscht. Zahlungseingänge zogen nicht mit um und verschwanden beim Löschen aus der Kasse. Fehlende Angaben führten zu einem Serverfehler. | Datenverlust, Zahlungen nicht mehr auffindbar | Behoben (Qualität II, 1b-2): Eingabeprüfung, Zahlungen ziehen mit um, alles in einem Schritt (ganz oder gar nicht). Tests in `tests/test_zugriffsschutz.py` |
| Die Reihenfolge der Daten (Ende nach Beginn, Anmeldeschluss nach Anmeldestart, letzte Änderung vor Beginn) wurde beim Bearbeiten nur an einer von zwei Stellen geprüft. | Widersprüchliche Fristen möglich | Behoben, Tests in `tests/test_fristen.py` |

## Zugriffsschutz und Datenfreigabe (Qualität II, Schritt 1b-2)

Geprüft am 15.10.2026: alle 70 Serializer mit `fields = '__all__'` (sie geben alle Felder einer Tabelle zum Lesen und Schreiben frei), alle schreibenden Schnittstellen und alle öffentlichen Adressen. Ergebnis: Viele Schnittstellen erlaubten Ändern oder Löschen, prüften aber nur, ob jemand eingeloggt ist.

### Behobene Lücken

Alle mit Tests in `tests/test_zugriffsschutz.py` bzw. `tests/test_gruppenrechte.py`, die vor der Behebung fehlschlugen. Dazu kommen Gegenproben, dass erlaubte Zugriffe weiter funktionieren, auch für eine Veranstaltungsleitung, die nur über die Leitungsgruppe Leitung ist.

| Was war möglich | Wer | Behebung |
| --- | --- | --- |
| Antworten aller Anmeldungen (z. B. Allergien, Freitext) lesen, ändern, löschen (`/event/<typ>-attribute/`) | jede eingeloggte Person | Nur noch Ändern, nur mit Recht auf die Anmeldung und bis zur Änderungsfrist |
| Fragen (Zusatzfelder) jeder Veranstaltung ändern und löschen (`/event/attribute-module/`) | jede eingeloggte Person | Nur Veranstaltungsleitung, Vorlagen nur Anmeldeteam |
| Jede Veranstaltung ändern oder löschen (`/event/event-read/`) | jede eingeloggte Person | Nur noch lesen (das Frontend lädt darüber Veranstaltungen) |
| Bausteine jeder Veranstaltung ändern und löschen (`/event/event/<id>/event-module/`) | jede eingeloggte Person | Nur Veranstaltungsleitung, Veranstaltung immer aus der Adresse |
| Bausteine in eine fremde Veranstaltung verschieben (`assigned-event-modules`) | Veranstaltungsleitung | Veranstaltung immer aus der Adresse |
| Zahlungserinnerungen an alle Anmeldungen jeder Veranstaltung auslösen | jede eingeloggte Person | Nur Veranstaltungsleitung |
| Zahlungseingang einer fremden Veranstaltung in die eigene umbuchen | Veranstaltungsleitung | Recht auf alte und neue Anmeldung |
| Teilnehmende in eine fremde Anmeldung verschieben | anmeldende Leitung | Anmeldung immer aus der Adresse |
| Preisstufe einer anderen Veranstaltung wählen (z. B. eine günstigere) | anmeldende Leitung | Preisstufe muss zur Veranstaltung gehören |
| Bewertung an eine fremde Anmeldung hängen | anmeldende Leitung | Anmeldung immer aus der Adresse |
| Veranstaltungsorte ändern und löschen | jede eingeloggte Person | Nur wer alle Veranstaltungen am Ort leitet, unbenutzte Orte nur Anmeldeteam |
| Eigene Gruppe umbenennen oder löschen (`/auth/my-groups/`) | jedes Gruppenmitglied | Nur lesen |
| Beliebige Benutzerkonten ändern oder löschen (`/keycloak/members/`) | jede Gruppenleitung | Nur lesen |
| Farbschemata ändern und löschen (`/basic/theme/`) | jede eingeloggte Person | Nur Anmeldeteam |
| Antworten aller Anmeldungen lesen, mitgeliefert in der Bausteinliste (`assigned-event-modules`) | jede eingeloggte Person | Antworten nur für Leitung, Ansichtsgruppe sowie Bundes- und Ringführung (eigener Bund/Ring) |
| Konten aller Gruppenmitglieder ändern oder löschen (`/keycloak/group/<id>/members/`) | jedes Gruppenmitglied | Nur lesen |
| Anmeldungen zusammenlegen, auch mit Anmeldungen fremder Veranstaltungen, dabei die zweite löschen | Ansichtsgruppe, Bundes- und Ringführung, Veranstaltungsleitung | Nur Veranstaltungsleitung, beide Anmeldungen müssen zur Veranstaltung gehören |
| Antworten an Zusatzfelder fremder Veranstaltungen hängen (tauchen dort in der Auswertung auf) | anmeldende Leitung | Zusatzfeld muss zur Veranstaltung der Anmeldung gehören |
| Zahlungseingang von seiner Anmeldung lösen (verschwindet aus der Kasse) | Veranstaltungsleitung | Anmeldung darf nicht geleert werden |
| Bausteine und Preisstufen ändern | Ansichtsgruppe | Nur Veranstaltungsleitung (Entscheidung vom 15.10.2026) |

Neu ist eine automatische Prüfung (`tests/test_schreibrechte_inventar.py`). Sie meldet jede schreibende Schnittstelle der aktiven Module, die nur den Login prüft, solange nicht begründet ist, wo das Recht stattdessen geprüft wird. Gegen den alten Stand hätte sie fünf der Lücken oben gefunden. Ihre Grenze: Schnittstellen mit einer schwachen, aber anderen Rechteprüfung (z. B. „Mitglied der Gruppe“) erkennt sie nicht. Dafür bleibt die Prüfung von Hand nötig.

### Bewertung der `fields = '__all__'`-Stellen

| Gruppe | Anzahl | Bewertung |
| --- | --- | --- |
| Aktive Module, nicht über eine Adresse erreichbar | 2 | unkritisch: `CashSummarySerializer` (ungenutzt), `WorkshopSerializer` (Modul nicht eingebunden) |
| Aktive Module, in diesem Schritt behoben | 14 | Zusatzfelder, Zahlungseingang, Veranstaltungsort, Baustein, Veranstaltung (`event-read`), Teilnehmende, Bewertung, Farbschema, Antworten in der Auswertung (6); siehe Tabelle oben |
| Aktive Module, Schreiben geschützt | 10 | Veranstaltung anlegen und ändern, Preisstufen, Dateierzeugung, Beitrittsanfragen (2), Mailvorlagen, Stammdaten (Essgewohnheiten, Pfadfinderstruktur, Ebenen) nur Anmeldeteam |
| Aktive Module, nur lesend erreichbar | 13 | Antworten in Anmeldungen (5), Auswertungen (2), Veranstaltung in der Essensplanung, Übersicht, Kassenansicht, Gruppen, Postleitzahlen, eigene Anmeldung zu einer Veranstaltung |
| Eingefrorene Module (`food` 21, `inspi` 4, `messaging` 6) | 31 | nicht einzeln bewertet, siehe unten |

Hinweis: In der Kasse lässt sich beim Ändern eines Zahlungseingangs die Person „überwiesen von“ frei setzen. Das betrifft nur die eigene Veranstaltung und ist kein Rechteproblem.

### Offen: eingefrorene Module

In `food` (Essensplanung) und `inspi` (Programmideen) gibt es rund 40 Schnittstellen, über die jede eingeloggte Person Einträge anderer ändern oder löschen kann. Personenbezogene Daten sind dort kaum betroffen, aber alle Inhalte könnten von jeder eingeloggten Person verändert werden. Eine Behebung wäre aufwendig. Entscheidung vom 15.10.2026: Beide Module sind abgeschaltet (Qualität II 1d, PR #12). Ihre Adressen sind nicht mehr erreichbar. Nur die Verwaltungsseiten unter `/admin/` bleiben, und die sind dem Anmeldeteam (Staff) vorbehalten. Abgesichert werden sie gegebenenfalls nach der Abstimmung der Anforderungen.

### Öffentliche Adressen

Zehn Adressen sind ohne Login erreichbar, alle bewusst: Registrierung, Prüfungen von Benutzername, E-Mail, Passwort und Postleitzahl während der Registrierung, Auswahllisten und das Kontaktformular. Dazu kamen zwei lesend öffentliche Listen in `inspi`, die mit dem Modul abgeschaltet sind. Zwei Schwächen:
- „Benutzername frei?“ und „E-Mail frei?“ verraten Fremden, ob eine E-Mail-Adresse im Tool registriert ist.
- Registrierung und Kontaktformular haben keine Begrenzung der Anfragen pro Minute. Damit wären massenhaft Konten oder Nachrichten möglich.

Beides gehört zum offenen Punkt „Begrenzung der Anfragen“ im Fahrplan.

Weitere Beobachtungen ohne Rechteproblem, für die Abstimmung der Abläufe notiert:
- Wer welche Veranstaltung über `/event/event-read/` lesen darf, ist nicht abgestimmt: heute jede eingeloggte Person jede Veranstaltung.
- Ein neu angelegter Ort ist bis zur Zuordnung zu einer Veranstaltung nur für das Anmeldeteam änderbar. Scheitert die Zuordnung, bleibt er ohne Veranstaltung zurück.
- Ändern eines Zahlungseingangs ohne Betrag bricht mit einem Serverfehler ab (fehlendes Feld `amount`).

## Abgleich Frontend und Backend (Qualität II, Schritt 2a)

Geprüft am 15.10.2026. `backend/tools/frontend_aufrufe.py` liest alle 211 Anfragen des Frontends aus und setzt dabei zusammengesetzte Pfade wie `${SERVICE}-read` richtig zusammen. Diese Pfade hatte eine Textsuche in PR #11 übersehen. `tests/test_frontend_abgleich.py` prüft bei jeder Änderung, dass es jede Adresse im Backend gibt und dass sie die Anfrageart erlaubt. Die Ergebnisse stehen als Karte in `docs/schnittstellen.md`.

Vor der Behebung gab es 27 Abweichungen:

| Befund | Anzahl | Auswirkung | Behebung |
| --- | --- | --- | --- |
| Person aus einer Anmeldung löschen: Pfad ohne abschließenden Schrägstrich | 1 | Lokal (Entwicklungseinstellungen) Serverfehler, im Echtbetrieb abhängig von der Weiterleitung des Browsers | Schrägstrich ergänzt |
| Auswahllisten (Ebenen, Essgewohnheiten, Mailvorlagen, Orte, Personensuche): Pfad ohne Schrägstrich | 9 Aufrufe | Funktionierte über eine stille Weiterleitung, kostete eine zusätzliche Anfrage | Schrägstrich ergänzt |
| Hilfsfunktionen, die nie aufgerufen werden und Adressen nutzen, die es nicht gibt oder die nur lesen erlauben | 13 | keine, aber irreführend | entfernt |
| Vier Dateien in `help/services` und `task/services`, nirgends eingebunden | 4 | keine | entfernt |

Nebenbei gefunden: Das Werkzeug hatte zunächst auch auskommentierten Code als Anfrage gelesen. Außerdem übersah es Backend-Klassen, die Ändern und Löschen über direkt benannte Methoden verarbeiten. Beides ist korrigiert, damit der Abgleich weder Fehlalarme noch Lücken hat.

Offen ist Schritt 2b: ob das Frontend Felder liest, die das Backend nicht liefert.

## Frontend

Gemessen am 14.10.2026, Prüfung mit eslint. Wird in Phase 4 Teil der automatischen Prüfungen.

| Messung | Wert |
| --- | --- |
| Umfang | ca. 34.000 Zeilen |
| eslint-Fehler | 198 |
| eslint-Warnungen | ca. 2.800 (v. a. ungenutzte Variablen und Formatierung) |
| Tests | keine |
| Größte Programmdatei nach dem Bauen | 1,2 MB, wird bei jedem Aufruf komplett geladen |
