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

### 3. Frontend

```bash
cd frontend
cp ../dev/frontend.env.example .env.local
CYPRESS_INSTALL_BINARY=0 yarn install --frozen-lockfile
yarn dev
```

Das Frontend läuft auf http://localhost:8080.

## Tests

Die Backend-Tests brauchen weder Datenbankserver noch Keycloak:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

`tests/test_rechte.py` prüft die Rechteregeln (wer sieht und bearbeitet welche Anmeldung). Tests mit der Markierung `xfail` beschreiben bekannte Fehler, die noch offen sind. Bei jeder Änderung auf GitHub laufen die Backend-Tests und der Frontend-Build automatisch (`.github/workflows/ci.yml`).

## Bekannte Einschränkungen

- **Keycloak-Schalter:** Das Backend braucht in Keycloak die veraltete Funktion `admin-fine-grained-authz:v1`. Ohne sie startet es nicht. Beim Verband (Keycloak 26.7) ist sie nicht aktiv. Lokal schaltet `dev/docker-compose.yml` sie ein. Die Ablösung ist der erste Punkt der Stabilisierung.
- **SSL zur Datenbank** ist im Code fest vorgeschrieben. Lokal nutzt Postgres dafür ein Testzertifikat.
- Die Docker-Variante der Hilfsdienste ist noch nicht auf einem echten Rechner erprobt. Der gleiche Aufbau ohne Docker (Postgres 16, Redis, Keycloak 26.7.5) wurde am 14.10.2026 vollständig getestet.

## Lizenz

Noch offen, wird mit den ursprünglichen Entwicklern abgestimmt.
