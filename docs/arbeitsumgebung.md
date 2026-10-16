# Arbeitsumgebung

Eigenheiten der Cloud-Sitzung und Rezepte, die beim Arbeiten gebraucht werden. Ausgelagert aus `docs/fahrplan.md` am 16.10.2026, damit der Fahrplan nur noch die Reihenfolge enthält. Aufbau der Rauchtests: `docs/entscheidungen.md`, Eintrag „Rauchtests: Werkzeug und Aufbau“ (16.10.2026). Anleitung für den Mac: `docs/lokal-starten.md`.

Pfade zu Tests und Backend-Code sind relativ zum Ordner `backend/` angegeben, z. B. `tests/test_abfragen.py` = `backend/tests/test_abfragen.py`.

## Cloud-Sitzung

- **Backend einrichten:**
  ```
  cd backend
  python3 -m venv .venv
  .venv/bin/pip install -r requirements-dev.txt
  ```
  Tests laufen mit `DJANGO_SETTINGS_MODULE=backend.settings_test`. Das steht auch in `pytest.ini`. Immer die Werkzeuge aus `.venv` aufrufen (`.venv/bin/ruff`, `.venv/bin/pytest`). In der Cloud liegen sonst andere Versionen bereit.
- **Frontend:**
  - Installieren mit `CYPRESS_INSTALL_BINARY=0 yarn install --frozen-lockfile`.
  - `yarn build` braucht die Umgebungsvariablen `VITE_APP_API`, `VITE_APP_URL`, `VITE_APP_KEYCLOAK_URL`, `VITE_APP_KEYCLOAK_REALM` und `VITE_APP_KEYCLOAK_CLIENT_ID` (Werte wie in `.github/workflows/ci.yml`).
  - Der Build ändert `frontend/components.d.ts` (eine Zeile `StepperNav`). Diese Änderung ist älter und gehört nicht in fremde Pull Requests: mit `git checkout frontend/components.d.ts` zurücksetzen.
- **Livetest gegen Keycloak ist in der Cloud möglich** (Korrektur vom 16.10.2026). Docker lässt sich mit `dockerd` starten, aber alle Abbilder sind gesperrt (`quay.io` und `docker.io`, auch `postgres`). Keycloak selbst lässt sich dagegen als Programmpaket von GitHub laden und läuft mit dem vorhandenen Java 21. Postgres 16 und Redis sind installiert. Rezept: Abschnitt „Ganzes Tool in der Cloud starten“. Vorher stand hier, Livetests gingen nur auf Sebastians Mac: Geprüft wurden nur die Docker-Abbilder.
- **GitHub:** `gh pr …` geht nicht (GraphQL gesperrt). Stattdessen die REST-Schnittstelle, z. B. `gh api repos/sebivtt/scout-participant-management/pulls -f title=… -f head=… -f base=main -F body=@datei.md`. Den Stand der automatischen Prüfungen zeigt `gh api repos/…/commits/<sha>/check-runs`.
- **Branches:** Die Kopie des Repositorys ist flach und kennt nur `main`. Neue Branches mit `git push -u origin <branch>` hochladen. Meldet ein Hinweis „unpushed commits“, obwohl gepusht wurde, mit `git ls-remote origin <branch>` prüfen.
- **Nach dem Ändern von Adressen oder Rechten** die Karte neu erzeugen: `.venv/bin/python tools/schnittstellen_karte.py` im Ordner `backend/`. Sonst schlägt ein Test an.

## Ganzes Tool in der Cloud starten

Erprobt am 16.10.2026: Keycloak 26.7.5, Postgres, Redis, Backend und Frontend laufen in der Cloud-Sitzung, Login mit den Testkonten über die echte Keycloak-Anmeldeseite.

- **Lang laufende Dienste** (Keycloak, `runserver`, `yarn dev`) mit der Hintergrund-Option des Bash-Werkzeugs starten (`run_in_background`), nicht mit `&` oder `nohup`. So gestartete Prozesse beendet die Sitzung nach einigen Minuten wieder, Keycloak war dann plötzlich weg.
- **Keycloak** (Programmpaket von GitHub, etwa 170 MB, startet in rund 20 Sekunden):
  ```
  mkdir -p ~/kc && cd ~/kc
  curl -sSL -o kc.tgz https://github.com/keycloak/keycloak/releases/download/26.7.5/keycloak-26.7.5.tar.gz
  tar xzf kc.tgz
  # im Hintergrund (run_in_background):
  cd ~/kc/keycloak-26.7.5 && KC_BOOTSTRAP_ADMIN_USERNAME=admin KC_BOOTSTRAP_ADMIN_PASSWORD=admin exec bin/kc.sh start-dev --http-port=8180
  # danach einrichten, im Ordner dev/:
  KCADM=~/kc/keycloak-26.7.5/bin/kcadm.sh ./keycloak-setup.sh
  ```
  `start-dev` speichert seine Daten in einer Datei im Keycloak-Ordner, ein Neustart behält Realm und Testkonten.
- **Postgres und Redis:**
  ```
  pg_ctlcluster 16 main start
  su postgres -c "psql -c \"CREATE USER scout WITH PASSWORD 'scout' CREATEDB;\" -c \"CREATE DATABASE scout OWNER scout;\""
  redis-server --daemonize yes
  ```
- **Backend**, im Ordner `backend/` mit eingerichtetem `.venv` (siehe oben):
  ```
  cp ../dev/backend.env.example backend/.env
  .venv/bin/python manage.py migrate
  .venv/bin/python manage.py loaddata data/main/*.json
  .venv/bin/python manage.py sync_keycloak_groups
  .venv/bin/python manage.py load_sample_data
  # im Hintergrund:
  exec .venv/bin/python manage.py runserver 8000 --noreload
  ```
- **Frontend**, im Ordner `frontend/`: `cp ../dev/frontend.env.example .env.local`, installieren wie oben, dann im Hintergrund `exec yarn dev`.
- **Login im Browser** mit Playwright: http://localhost:8080 aufrufen, das Frontend leitet zur Keycloak-Anmeldeseite weiter, dort `#username`, `#password` ausfüllen und `#kc-login` klicken. Nach dem Login landet man unter „Veranstaltungen“ auf „Einladungen“, nicht auf der ursprünglich aufgerufenen Seite.

## Browser und Nachstellen von Frontend-Fehlern

- **In der Cloud-Sitzung gibt es einen Browser** (Korrektur vom 16.10.2026). Chromium mit Playwright ist vorinstalliert (`/opt/pw-browsers`, Playwright unter `/opt/npm-tools/node_modules/playwright`, `PLAYWRIGHT_BROWSERS_PATH` ist gesetzt). Am 15.10. wurde nur an den Standardorten gesucht und fälschlich „kein Browser“ festgehalten. Keycloak läuft ebenfalls, siehe „Ganzes Tool in der Cloud starten“ (nur die Docker-Abbilder und Maven sind gesperrt).
- **Bei Issue #23 erprobt** (vor dem echten Keycloak in der Cloud; für neue Arbeit lieber das ganze Tool starten): Das Frontend läuft mit `yarn dev`, Playwright beantwortet im Browser die Anfragen an Keycloak (Login mit Platzhalter-Token) und ans Backend (Testdaten) mit `page.route`. Am Tool selbst ändert sich dafür nichts, es gibt keinen Login-Ersatz im Code. Testdaten, die zum echten Backend passen, erzeugt das Backend selbst über die Testdaten aus `tests/conftest.py`. So ließ sich #23 nachstellen und die Behebung vorher und nachher prüfen. Grenze: Das Backend wird dabei nicht mitgeprüft.
- **Nachstell-Skripte vom 16.10.2026 (nicht im Repository, nur als Rezept):** Ein Node-Skript startet Chromium über `require('/opt/npm-tools/node_modules/playwright')`, ruft das Frontend auf `http://localhost:8080` auf (`yarn dev` mit den Umgebungsvariablen aus `.github/workflows/ci.yml`) und beantwortet mit `page.route`:
  - `http://localhost:8180/**` (Keycloak): `…/protocol/openid-connect/auth` mit einer Weiterleitung an `redirect_uri#state=…&code=c`, `…/token` mit einem unsignierten JWT (dem Ausweis, den Keycloak nach dem Login ausstellt), das den `nonce` aus der Anfrage enthält.
  - `http://localhost:8000/**` (Backend): Antworten aus JSON-Dateien, die das echte Backend erzeugt. Dazu vorübergehend einen Test in `backend/tests/` anlegen, der mit den Fixtures aus `conftest.py` Daten anlegt und die Antworten (`/event/event-read/<id>/`, `/event/registration-read/<id>/`, `/auth/personal-data/`, `/basic/gender/`, `/event/travel-type-choices/`) in Dateien schreibt, danach löschen. Alle übrigen Anfragen mit `[]` beantworten.
  - Gemessen wurden je Seite Programmfehler (`pageerror`, `console.error`) und Vue-Warnungen, vorher und nachher.
  - Vorsicht in der Cloud-Shell: Prozesse nicht mit `pkill -f`/`pgrep -f` auf ein Muster beenden, das in der eigenen Befehlszeile vorkommt, das beendet die eigene Shell. PIDs über `ps aux | grep -E "[v]ite --port"` ermitteln.
