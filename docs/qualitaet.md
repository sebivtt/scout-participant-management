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
| Umfang | 17.854 Zeilen in 232 Dateien (ohne Migrationen und Tests) | – | – |
| Tests | 140 bestanden, 6 bekannte Probleme (`xfail`) | wächst mit jeder Änderung | pytest |
| Bekannte Sicherheitslücken in Paketen | 0 | 0 | pip-audit |
| Verstöße gegen Code-Regeln, neu | 0 | 0 (wird bei jeder Änderung geprüft) | ruff |
| Verstöße gegen Code-Regeln, Altlasten (`# noqa`) | 64 (dazu 6 gewollte Markierungen, siehe unten) | sinkt durch die Pfadfinderregel | ruff |
| Funktionen und Klassen mit Beschreibung | 126 von 1.533 (8 %) | Kernbereiche 100 %, sonst wachsend | `tools/qualitaet_messen.py` |

### Altlasten nach Art

| Regel | Anzahl | Bedeutung |
| --- | --- | --- |
| T201 | 39 | `print()` statt Protokollierung, v. a. bei der Registrierung neuer Konten und in den Keycloak-Hilfsskripten |
| F841 | 9 | Variable wird gesetzt, aber nie benutzt |
| E722 | 7 | Pauschales `except:` verschluckt jeden Fehler, auch echte Programmfehler |
| C901 | 5 | Funktion zu verschachtelt (siehe unten) |
| sonstige | 4 | einzelne Importe und Kleinigkeiten (B007, F401, F811, F842) |

Gewollt und keine Altlast: sechs `# noqa: F401` in den `apps.py`-Dateien, erkennbar an der Begründung nach `--`. Fünf Importe registrieren Signal-Empfänger, einer meldet den Keycloak-Abgleich bei Celery an. Sie dürfen nicht entfernt werden (Test: `tests/test_signale.py`).

Korrektur am 15.10.2026 (Qualität II, Schritt 1): Die erste Messung übersah 16 Markierungen ohne Regelnummer (`# noqa`). Sie schalteten auf ihrer Zeile jede Prüfung ab, auch künftig eingeschaltete. Zehn waren wirkungslos und sind entfernt. Fünf sind jetzt gezielt: vier gewollte mit Begründung und eine Altlast (`notifications/models.py`). Eine bereits gezielte Markierung in `notifications/apps.py` war überflüssig und ist entfernt. Die Markierung in den Testeinstellungen war keine Altlast und ist jetzt in `ruff.toml` geregelt. ruff lässt Markierungen ohne Nummer nicht mehr zu.

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
| Die Reihenfolge der Daten (Ende nach Beginn, Anmeldeschluss nach Anmeldestart, letzte Änderung vor Beginn) wurde beim Bearbeiten nur an einer von zwei Stellen geprüft. | Widersprüchliche Fristen möglich | Behoben, Tests in `tests/test_fristen.py` |

## Frontend

Gemessen am 14.10.2026, Prüfung mit eslint. Wird in Phase 4 Teil der automatischen Prüfungen.

| Messung | Wert |
| --- | --- |
| Umfang | ca. 34.000 Zeilen |
| eslint-Fehler | 198 |
| eslint-Warnungen | ca. 2.800 (v. a. ungenutzte Variablen und Formatierung) |
| Tests | keine |
| Größte Programmdatei nach dem Bauen | 1,2 MB, wird bei jedem Aufruf komplett geladen |
