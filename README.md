# Scout Participant Management

Anmeldetool für Pfadfinder-Veranstaltungen: Gruppen- und Stammesleitungen melden ihre Leute zu Lagern und Fahrten an, die Veranstaltungsleitung sieht und verwaltet alle Anmeldungen.

Das Projekt baut auf dem archivierten DPV-Tool auf ([scout-tool-backend](https://github.com/dpvonline/scout-tool-backend), [scout-tool-frontend](https://github.com/dpvonline/scout-tool-frontend)), mit Erlaubnis der ursprünglichen Entwickler. Die vollständige Git-Historie beider Projekte ist erhalten.

| Ordner | Inhalt | Ursprung |
| --- | --- | --- |
| `backend/` | Django 5.2 LTS REST API (Python 3.11 bis 3.13) | `scout-tool-backend`, Zweig `main` (451ace1, 12.03.2025) |
| `frontend/` | Vue 3 + Vite + Tailwind | `scout-tool-frontend`, Commit `ce97a2d` (23.03.2025), der letzte lauffähige Stand |
| `dev/` | Lokale Entwicklungsumgebung | neu |

Neben dem Anmeldetool enthält das Backend weitere Module (Essensplanung, Inspi, Nachrichten, Gruppenverwaltung). Sie bleiben lauffähig, werden aber vorerst nicht weiterentwickelt.

## Dokumentation

| Datei | Inhalt |
| --- | --- |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Regeln für die Entwicklung |
| [`docs/fahrplan.md`](docs/fahrplan.md) | **Einstieg:** Reihenfolge der nächsten Schritte (verbindlich), Stand |
| [`docs/lokal-starten.md`](docs/lokal-starten.md) | Tool lokal mit Beispieldaten starten, offenen Pull Request ausprobieren (Schritt für Schritt) |
| [`docs/arbeitsumgebung.md`](docs/arbeitsumgebung.md) | Einrichtung der Cloud-Sitzung, Fehler im Browser nachstellen |
| [`docs/architektur.md`](docs/architektur.md) | Aufbau des Systems, Ablauf einer Anmeldung, wo was liegt |
| [`docs/entscheidungen.md`](docs/entscheidungen.md) | Fachliche und technische Entscheidungen mit Begründung |
| [`docs/glossar.md`](docs/glossar.md) | Deutsche Fachbegriffe und ihre Namen im Code |
| [`docs/qualitaet.md`](docs/qualitaet.md) | Messwerte, bekannte Schwächen, Prioritäten |

## Lokal starten

Schritt-für-Schritt-Anleitung mit Beispieldaten: [`docs/lokal-starten.md`](docs/lokal-starten.md). Hier die Kurzfassung.

Voraussetzungen: Docker, Python 3.11 bis 3.13, Node.js 20.19 oder neuer bzw. 22.13 oder neuer (verlangt eslint 10), Yarn.

### 1. Hilfsdienste starten (Datenbank, Redis, Keycloak)

```bash
cd dev
docker compose up -d
# Warten, bis Keycloak bereit ist (ca. 30 Sekunden), dann Login-Server einrichten:
./keycloak-setup.sh
```

Das Skript legt den Realm `dpv`, die Clients und drei Testkonten an:

| Benutzer | Passwort | Rolle |
| --- | --- | --- |
| `leitung` | `leitung123` | Anmeldeteam (Staff) |
| `stammesleitung` | `stamm123` | normale Leitung ohne Sonderrechte |
| `teilnehmer` | `teilnehmer123` | normale Person |

`leitung` und `stammesleitung` sind Mitglied der Gruppe „Testgruppe Lagerteam“. Diese Gruppe beim Anlegen einer Veranstaltung als Leitungs- und Ansichtsgruppe wählen.

Keycloak-Verwaltung: http://localhost:8180 (admin / admin)

Hinweis: `leitung` hat die Rolle „Anmeldeteam“ und ist damit im Tool Staff. Staff darf alle Gruppen verwalten. Normale Rechte lassen sich mit `stammesleitung` ausprobieren.

### 2. Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp ../dev/backend.env.example backend/.env
python manage.py migrate
python manage.py loaddata data/main/*.json   # Stammdaten: Bünde, Stämme, PLZ, Vorlagen
python manage.py sync_keycloak_groups        # Gruppen aus Keycloak übernehmen
python manage.py load_sample_data            # Beispieldaten: Veranstaltung „Beispiellager“ mit einer Anmeldung
python manage.py runserver
```

Das Backend läuft auf http://localhost:8000.

Optional die Bund- und Stammstruktur in Keycloak anlegen und die Standardrechte vergeben (dauert einige Minuten, kann mehrfach laufen):

```bash
python manage.py initialize_scout_hierarchies_in_keycloak
```

### 3. Frontend

```bash
cd frontend
cp ../dev/frontend.env.example .env.local
CYPRESS_INSTALL_BINARY=0 yarn install --frozen-lockfile
yarn dev
```

Das Frontend läuft auf http://localhost:8080.

## Rechte

Wer welche Gruppe verwalten oder einsehen darf, steht in der Tabelle **Gruppenrechte** (Django-Verwaltung unter `/admin/`, Modell `keycloak_auth.GroupPermission`). Keycloak liefert nur Login und Gruppenmitgliedschaften.

- Ein Recht gilt für eine Person oder für alle Mitglieder einer Gruppe (z. B. „Stammesführung“ verwaltet den Stamm).
- Rechte gelten auch für alle Untergruppen. Admin schließt Ansicht ein.
- Löschen einer Gruppe braucht Admin-Recht auf die Obergruppe.
- Staff (Rolle „Anmeldeteam“) hat überall Admin-Recht.
- `python manage.py grant_hierarchy_permissions` vergibt die Standardrechte für vorhandene Gruppen, ohne Keycloak zu fragen.

Die veraltete Keycloak-Funktion `admin-fine-grained-authz` wird nicht mehr benötigt. Der Service-Account des Backends kommt mit Standard-Rollen des Clients `realm-management` aus. Voraussichtlich reichen `view-users`, `query-groups`, `manage-users`, `manage-realm` und `manage-clients`. Getestet ist bisher nur mit `realm-admin`, die Prüfung der kleineren Rollenauswahl folgt.

## Fristen

Regeln vom 14.10.2026, umgesetzt in `backend/anmelde_tool/event/deadlines.py`:

| Einstellung der Veranstaltung | Wirkung |
| --- | --- |
| Anmeldestart (`registration_start`) | vorher keine Anmeldung möglich |
| Offizieller Anmeldeschluss (`registration_deadline`) | wird angezeigt, sperrt nichts |
| Technische Sperre ab (`registration_closes_at`, optional) | danach keine neuen Anmeldungen |
| Neue Anmeldungen gesperrt (`registration_closed`) | manuell, sofort |
| Letzte Änderung möglich (`last_possible_update`, optional) | danach keine Änderungen; leer = Veranstaltungsbeginn |
| Änderungen gesperrt (`changes_closed`) | manuell, sofort; sperrt auch neue Anmeldungen |

Die Veranstaltungsleitung ist von allen Sperren ausgenommen. Die neuen Schalter lassen sich vorerst über die API und die Django-Verwaltung setzen, die Oberfläche folgt in Phase 4.

## Pakete aktualisieren

`backend/requirements.in` enthält nur die direkt genutzten Pakete, `requirements.txt` wird daraus erzeugt und hält alle Versionen fest:

```bash
cd backend
pip install pip-tools
pip-compile --upgrade --strip-extras requirements.in   # alle Pakete auf den neuesten Stand
pip install -r requirements-dev.txt && pytest           # prüfen
```

Bei jeder Änderung prüft GitHub die Pakete zusätzlich auf bekannte Sicherheitslücken.

## Tests

Die Backend-Tests brauchen weder Datenbankserver noch Keycloak:

```bash
cd backend
pip install -r requirements-dev.txt
ruff check .   # Code-Regeln
pytest         # Tests
```

`tests/test_rechte.py` prüft die Rechteregeln (wer sieht und bearbeitet welche Anmeldung). Tests mit der Markierung `xfail` beschreiben bekannte Fehler, die noch offen sind. Bei jeder Änderung auf GitHub laufen die Backend-Tests und der Frontend-Build automatisch (`.github/workflows/ci.yml`).

## Bekannte Einschränkungen

- Die Docker-Variante der Hilfsdienste ist auf dem Mac des Projektverantwortlichen in Gebrauch. Der gleiche Aufbau ohne Docker (Postgres 16, Redis, Keycloak 26.7.5) läuft auch in der Cloud-Sitzung (`docs/arbeitsumgebung.md`).

## Lizenz

Noch offen, wird mit den ursprünglichen Entwicklern abgestimmt.
