# Regeln für die Entwicklung

Diese Regeln gelten für jede Änderung, egal ob von Menschen oder KI. Sie sollen sicherstellen, dass der Code verständlich, getestet und effizient bleibt, auch wenn ihn niemand Zeile für Zeile prüfen kann. Vereinbart am 15.10.2026.

Was ein Programm prüfen kann, prüft GitHub bei jeder Änderung automatisch (`.github/workflows/ci.yml`). Die übrigen Regeln sind mit „(Review)“ markiert.

## 1. Sprache

- **Code auf Englisch:** Namen von Variablen, Funktionen, Klassen, Dateien und Feldern.
- **Erklärungen auf Deutsch:** Kommentare, Docstrings, Dokumentation, Commit-Nachrichten, Pull Requests, Fehlermeldungen für Nutzer.
- Fachbegriffe folgen dem Glossar (`docs/glossar.md`): im Code `registration`, im Text „Anmeldung“.

## 2. Verständlichkeit

- **Kommentare erklären das Warum, nicht das Was.** „Neue Anmeldungen enden mit der Änderungsfrist, sonst gäbe es Anmeldungen, die niemand mehr ändern kann“ ist hilfreich. „Prüft das Datum“ ist es nicht. (Review)
- **Jede öffentliche Funktion und Klasse in neuem oder geändertem Code hat einen Docstring**: ein Satz, was sie tut, dazu die Regeln oder Grenzfälle, die nicht offensichtlich sind. (Review)
- **Funktionen bleiben überschaubar:** zyklomatische Komplexität höchstens 12. Grob heißt das: nicht mehr als etwa zehn Verzweigungen. Wird es mehr, wird aufgeteilt. (automatisch, `ruff` C901)
- **Kein auskommentierter Code.** Alte Fassungen stehen in der Git-Historie. (Review)
- **Kein `print()`** im Anwendungscode, stattdessen `logging`. Ausnahme: Management-Befehle und Werkzeuge in `backend/tools/`. (automatisch, `ruff` T20)
- Fehler werden gezielt abgefangen (`except KeycloakError`), nie pauschal (`except:` oder `except Exception: pass`). (automatisch für `except:`, sonst Review)

## 3. Korrektheit

- **Jede fachliche Regel hat einen Test**, der sie in Alltagssprache benennt, z. B. `test_nach_offiziellem_anmeldeschluss_weiter_moeglich`. (Review)
- **Jeder behobene Fehler bekommt einen Test**, der ohne den Fix fehlschlägt. (Review)
- Bekannte, noch offene Fehler werden als `@pytest.mark.xfail(strict=True, raises=..., reason=...)` festgehalten. `raises` nennt genau die erwartete Fehlerart, damit nicht jeder beliebige andere Fehler als „bekannt“ durchgeht (Vorbild: `tests/test_abfragen.py`). Wird einer behoben, meldet der Testlauf das, und die Markierung muss weg. (automatisch, außer `raises`: Review)
- Bekannte unsichere Muster (abgeschaltete Zertifikatsprüfung, Passwörter im Code, verschluckte Fehler, unsichere Aufrufe) meldet ruff. Ein festes Passwort ist nur in Code erlaubt, der im Echtbetrieb verweigert wird, mit Test. (automatisch, `ruff` S)
- **Schreibende Schnittstellen prüfen das Recht auf das betroffene Objekt**, nicht nur den Login. Die Zugehörigkeit (Veranstaltung, Anmeldung) kommt aus der Adresse, nie aus dem Inhalt der Anfrage, sonst lässt sich ein Eintrag in eine fremde Veranstaltung schieben. Schnittstellen, die das Frontend nur liest, sind nur lesend. (automatisch für reine Login-Prüfung, `tests/test_schreibrechte_inventar.py`, sonst Review)
- Rechte werden im Backend geprüft, nie nur in der Oberfläche. Neue Endpunkte verlangen standardmäßig einen Login, öffentliche Endpunkte setzen `AllowAny` ausdrücklich und begründen das im Kommentar. (automatisch über die Standardeinstellung, sonst Review)
- Keine ungenutzten Importe oder Variablen. (automatisch, `ruff` F)

## 4. Effizienz

- **Listen dürfen nicht pro Eintrag neue Datenbankabfragen auslösen** (N+1-Muster). Zugehörige Daten werden mit `select_related` oder `prefetch_related` vorab geladen. (automatisch für die Seiten in `tests/test_abfragen.py`)
- Neue Listen-Endpunkte bekommen einen Skalierungstest in `tests/test_abfragen.py`: Die Zahl der Abfragen darf bei 10 Einträgen nicht höher sein als bei einem. (Review)
- Externe Dienste (Keycloak, Mail) werden höchstens einmal pro Anfrage gefragt, nicht pro Listeneintrag. (Review)

## 5. Abhängigkeiten

- Neue Pakete nur mit Begründung im Pull Request: Wofür, warum nicht selbst gelöst, wird es gepflegt? (Review)
- Pakete stehen in `backend/requirements.in`. `requirements.txt` wird mit `pip-compile` erzeugt, nie von Hand bearbeitet. (Review)
- Pakete mit bekannten Sicherheitslücken blockieren die Übernahme. (automatisch, `pip-audit`)

## 6. Pull Requests

- **Klein und thematisch:** ein Thema pro Pull Request. (Review)
- Die Beschreibung erklärt in Alltagssprache:
  1. was sich für Nutzende ändert,
  2. welche Regeln oder Entscheidungen umgesetzt sind,
  3. wie geprüft wurde, also Tests und Livetest,
  4. was offen bleibt.
- Änderungen am Datenmodell kommen mit Migration. (automatisch)
- **Neue Regeln und Entscheidungen** stehen in `docs/entscheidungen.md`. (Review)

## 7. Die Pfadfinderregel

> Hinterlasse den Code besser, als du ihn vorgefunden hast.

Wer eine bestehende Funktion ändert, ergänzt dabei ihren Docstring, entfernt toten Code daneben und schreibt einen Test, falls keiner existiert. So wird der übernommene Code Schritt für Schritt verständlicher, ohne ihn auf einmal umzuschreiben.

## Altlasten

Der übernommene Code erfüllt diese Regeln noch nicht überall. Bestehende Verstöße sind mit `# noqa: <Regel>` markiert, damit die automatische Prüfung nur neue Verstöße meldet. Jede Markierung ist eine Einladung zur Pfadfinderregel. Stand und Zahlen stehen in `docs/qualitaet.md`.

- **`# noqa` immer mit Regelnummer.** Eine Markierung ohne Nummer schaltet auf dieser Zeile alle Regeln ab, auch solche, die erst später eingeschaltet werden. Überflüssige Markierungen meldet ruff ebenfalls. (automatisch, `ruff` PGH004 und RUF100)
- **Gewollte Markierungen** sind keine Altlast, sondern nötig, und tragen hinter der Regelnummer nach `--` eine Begründung, z. B. Importe in `apps.py`, die Signal-Empfänger oder Hintergrundaufgaben anmelden. Jede braucht einen Test, der anschlägt, wenn die Zeile fehlt (`tests/test_signale.py`). Neuer Code bekommt sonst keine Markierungen. (Review)
