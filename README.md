# Scout Participant Management

Anmeldetool für Pfadfinder-Veranstaltungen: Gruppen- und Stammesleitungen melden ihre Leute zu Lagern und Fahrten an, die Veranstaltungsleitung sieht und verwaltet alle Anmeldungen.

Das Projekt baut auf dem archivierten DPV-Tool auf ([scout-tool-backend](https://github.com/dpvonline/scout-tool-backend), [scout-tool-frontend](https://github.com/dpvonline/scout-tool-frontend)), mit Erlaubnis der ursprünglichen Entwickler. Die vollständige Git-Historie beider Projekte ist erhalten.

| Ordner | Inhalt | Ursprung |
| --- | --- | --- |
| `backend/` | Django REST API (Python 3.11) | `scout-tool-backend`, Zweig `main` (451ace1, 12.03.2025) |
| `frontend/` | Vue 3 + Vite + Tailwind | `scout-tool-frontend`, Commit `ce97a2d` (23.03.2025), der letzte lauffähige Stand |
| `dev/` | Lokale Entwicklungsumgebung | neu |

Neben dem Anmeldetool enthält das Backend weitere Module (Essensplanung, Inspi, Nachrichten, Gruppenverwaltung). Sie bleiben lauffähig, werden aber vorerst nicht weiterentwickelt.

## Lokal starten

Voraussetzungen: Docker, Python 3.11, Node.js 20 oder neuer, Yarn.

### 1. Hilfsdienste starten (Datenbank, Redis, Keycloak)

```bash
cd dev
docker compose up -d
# Warten, bis Keycloak bereit ist (ca. 30 Sekunden), dann Login-Server einrichten:
./keycloak-setup.sh
```

Das Skript legt den Realm `dpv`, die Clients und zwei Testkonten an:

| Benutzer | Passwort | Rolle |
| --- | --- | --- |
| `leitung` | `leitung123` | Anmeldeteam |
| `teilnehmer` | `teilnehmer123` | normale Person |

Keycloak-Verwaltung: http://localhost:8180 (admin / admin)

Hinweis: `leitung` hat die Rolle „Anmeldeteam“ und ist damit im Tool Staff. Staff darf alle Gruppen verwalten. Zum Ausprobieren normaler Rechte ein weiteres Konto ohne diese Rolle anlegen.

### 2. Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../dev/backend.env.example backend/.env
python manage.py migrate
python manage.py loaddata data/main/*.json   # Stammdaten: Bünde, Stämme, PLZ
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

## Tests

Die Backend-Tests brauchen weder Datenbankserver noch Keycloak:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

`tests/test_rechte.py` prüft die Rechteregeln (wer sieht und bearbeitet welche Anmeldung). Tests mit der Markierung `xfail` beschreiben bekannte Fehler, die noch offen sind. Bei jeder Änderung auf GitHub laufen die Backend-Tests und der Frontend-Build automatisch (`.github/workflows/ci.yml`).

## Bekannte Einschränkungen

- **SSL zur Datenbank** ist im Code fest vorgeschrieben. Lokal nutzt Postgres dafür ein Testzertifikat.
- Die Docker-Variante der Hilfsdienste ist noch nicht auf einem echten Rechner erprobt. Der gleiche Aufbau ohne Docker (Postgres 16, Redis, Keycloak 26.7.5) wurde am 14.10.2026 vollständig getestet.

## Lizenz

Noch offen, wird mit den ursprünglichen Entwicklern abgestimmt.
