# Tool lokal mit Beispieldaten starten

Schritt-für-Schritt-Anleitung für den Mac, ein Befehl pro Schritt. Das Projekt liegt unter `~/Projekte/scout-participant-management`. Die Befehle werden im Programm **Terminal** eingegeben und mit der Eingabetaste bestätigt. Entstanden am 16.10.2026 für die Rauchtests (Fahrplan, Schritt 1a).

Es gibt vier Teile:

1. [Tool starten](#1-tool-starten), jedes Mal
2. [Beispieldaten laden](#2-beispieldaten-laden), einmal, danach nur bei Bedarf
3. [Einen offenen Pull Request ausprobieren](#3-einen-offenen-pull-request-ausprobieren)
4. [Tool beenden](#4-tool-beenden)

Wer das Tool zum ersten Mal einrichtet, beginnt mit dem [Anhang](#anhang-erstmalige-einrichtung).

## Die Testkonten

Die Beispieldaten passen zu den Testkonten aus Keycloak:

| Konto | Passwort | Rolle im Beispiellager |
| --- | --- | --- |
| `leitung` | `leitung123` | leitet das Beispiellager (zugleich Anmeldeteam, darf überall alles) |
| `stammesleitung` | `stamm123` | hat ihren Stamm mit zwei Personen angemeldet |
| `teilnehmer` | `teilnehmer123` | keine Rolle, kann eine neue Anmeldung anlegen |

Tipp: Zum Wechseln zwischen den Konten ein privates Browserfenster öffnen (Safari und Chrome: Befehlstaste + Umschalttaste + N). So bleibt das eigene Konto im normalen Fenster angemeldet.

## 1. Tool starten

Das Tool besteht aus drei Teilen, die nebeneinander laufen: den Hilfsdiensten in Docker (Datenbank, Redis, Keycloak), dem Backend und dem Frontend. Backend und Frontend brauchen je ein eigenes Terminal-Fenster, weil sie laufen, bis man sie beendet.

**Docker Desktop** muss laufen (Wal-Symbol oben in der Menüleiste).

### Hilfsdienste (erstes Terminal-Fenster)

1. `cd ~/Projekte/scout-participant-management/dev`
   Keine Ausgabe.
2. `docker compose up -d`
   Drei Zeilen mit „Started“ oder „Running“ (postgres, redis, keycloak).
3. Etwa 30 Sekunden warten, bis Keycloak bereit ist.

### Backend (dasselbe Fenster)

4. `cd ../backend`
   Keine Ausgabe.
5. `source .venv/bin/activate`
   Vorne in der Zeile steht jetzt `(.venv)`.
6. `python manage.py runserver`
   Am Ende steht „Starting development server at http://127.0.0.1:8000/“. Das Fenster offen lassen.

### Frontend (zweites Terminal-Fenster)

7. Neues Fenster öffnen: Befehlstaste + N im Terminal.
8. `cd ~/Projekte/scout-participant-management/frontend`
   Keine Ausgabe.
9. `yarn dev`
   Nach einigen Sekunden steht dort „Local: http://localhost:8080/“. Das Fenster offen lassen.
10. Im Browser http://localhost:8080 öffnen und mit einem Testkonto anmelden.

## 2. Beispieldaten laden

Der Befehl legt die Veranstaltung **„Beispiellager“** an, mit dem Ort „Beispielzeltplatz“, der Buchungsoption „Standard“ (15 €) und den Schritten der Standardvorlage, genau wie beim Anlegen über die Oberfläche. Dazu kommt eine Anmeldung eines Stamms durch `stammesleitung` mit zwei erfundenen Personen (Mia Beispiel und Leo Muster). Die Anmeldung ist offen, Anmeldestart war gestern.

**Was mit deinen eigenen Daten passiert:** nichts. Der Befehl legt nur zusätzlich an und ändert oder löscht nichts, was schon da ist. Ein zweiter Aufruf legt nichts doppelt an. Im Echtbetrieb verweigert der Befehl.

Das Backend muss dafür nicht laufen, die Hilfsdienste aus Teil 1 schon.

1. Neues Terminal-Fenster öffnen: Befehlstaste + N.
2. `cd ~/Projekte/scout-participant-management/backend`
   Keine Ausgabe.
3. `source .venv/bin/activate`
   Vorne steht `(.venv)`.
4. `python manage.py load_sample_data`
   Es erscheint: „Beispiellager“ angelegt: Leitung „leitung“, Anmeldung von „…“ durch „stammesleitung“ mit 2 Personen. Statt der Punkte steht der Name eines Stamms aus den Stammdaten.
5. Im Browser als `teilnehmer` anmelden: Unter „Veranstaltungen“ erscheint das Beispiellager bei „Einladungen“.

**Beispiellager frisch anlegen:** Wurde im Beispiellager herumprobiert, oder liegen seine Termine nach einigen Wochen in der Vergangenheit, setzt dieser Befehl es zurück:

- `python manage.py load_sample_data --reset`
  Löscht nur das Beispiellager samt seiner Anmeldungen und legt es neu an. Alles andere bleibt.

**Wenn etwas nicht klappt:**

- Meldung „Die Vorlage für Veranstaltungen fehlt“ oder „Es gibt keinen Stamm“: Die Stammdaten sind nicht geladen. Einmal `python manage.py loaddata data/main/*.json` ausführen (dauert etwa eine halbe Minute), dann Schritt 4 wiederholen.
- Login mit einem Testkonto klappt nicht: Im Ordner `dev` einmal `./keycloak-setup.sh` ausführen. Das Skript legt fehlende Testkonten an und darf mehrfach laufen.

## 3. Einen offenen Pull Request ausprobieren

Ein **Branch** ist eine eigene Arbeitskopie des Codes. Jeder Pull Request hat einen, darin liegen seine Änderungen, bevor sie in `main` übernommen werden. Um einen Pull Request vor der Übernahme auszuprobieren, holt man seinen Branch auf den Mac. Den Namen des Branches und eventuell nötige Zusatzschritte nennt die Beschreibung des Pull Requests unter „So probierst du es aus“.

Laufen Backend und Frontend noch, zuerst beide mit Control + C beenden (siehe Teil 4).

1. `cd ~/Projekte/scout-participant-management`
   Keine Ausgabe.
2. `git status`
   Es sollte „nothing to commit, working tree clean“ dastehen. **Steht dort etwas anderes, hier anhalten** und nachfragen, damit keine eigenen Änderungen verloren gehen.
3. `git fetch origin`
   Lädt die neuen Branches von GitHub. Am Code auf dem Mac ändert sich dadurch noch nichts.
4. `git switch <Name des Branches>`
   Zum Beispiel `git switch rauchtests-1a-beispieldaten`. Es erscheint „Switched to a new branch …“ oder „Switched to branch …“. Jetzt liegt der Stand des Pull Requests auf dem Mac.
5. Nennt der Pull Request Zusatzschritte (neue Pakete, Änderungen an der Datenbank), diese jetzt ausführen.
6. Tool starten wie in Teil 1 und ausprobieren.

**Zurück zum normalen Stand**, wenn das Ausprobieren fertig ist (Backend und Frontend vorher beenden):

7. `git switch main`
   Es erscheint „Switched to branch 'main'“.
8. `git pull`
   Holt den neuesten Stand von `main`. Wurde der Pull Request inzwischen übernommen, ist er jetzt darin enthalten.

Hat ein Pull Request die Datenbank verändert (eine sogenannte Migration), steht in seiner Beschreibung, was beim Zurückwechseln zu tun ist.

## 4. Tool beenden

1. Im Fenster mit dem Frontend: Control + C.
2. Im Fenster mit dem Backend: Control + C.
3. `cd ~/Projekte/scout-participant-management/dev`
4. `docker compose stop`
   Die Hilfsdienste halten an. Daten und Keycloak-Einstellungen bleiben erhalten und sind beim nächsten Start wieder da.

## Anhang: Erstmalige Einrichtung

Nur einmal nötig. Voraussetzungen: Docker Desktop, Python 3.11 bis 3.13, Node.js 22, Yarn (siehe `README.md`).

**Hilfsdienste und Keycloak**

1. `cd ~/Projekte/scout-participant-management/dev`
2. `docker compose up -d`, danach etwa 30 Sekunden warten.
3. `./keycloak-setup.sh`
   Am Ende: „Keycloak-Realm 'dpv' ist eingerichtet“.

**Backend**

4. `cd ../backend`
5. `python3 -m venv .venv`
6. `source .venv/bin/activate`
7. `pip install -r requirements-dev.txt` (dauert einige Minuten)
8. `cp ../dev/backend.env.example backend/.env`
9. `python manage.py migrate`
10. `python manage.py loaddata data/main/*.json`
    Am Ende: „Installed … object(s) from 10 fixture(s)“.
11. `python manage.py sync_keycloak_groups`
    Am Ende: „Checks finished“.
12. `python manage.py load_sample_data`

**Frontend**

13. `cd ../frontend`
14. `cp ../dev/frontend.env.example .env.local`
15. `CYPRESS_INSTALL_BINARY=0 yarn install --frozen-lockfile` (dauert einige Minuten)

Danach weiter mit Teil 1, ab Schritt 4 (Backend starten).
