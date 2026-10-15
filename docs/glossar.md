# Glossar

Im Code stehen englische Begriffe, in Oberfläche und Dokumentation deutsche. Diese Tabelle ordnet sie einander zu.

## Veranstaltungen und Anmeldungen

| Deutsch | Im Code | Wo | Bedeutung |
| --- | --- | --- | --- |
| Veranstaltung | `Event` | `anmelde_tool/event/models.py` | Lager, Fahrt, Treffen; hat Termine, Fristen, Preise und Rechte |
| Veranstaltungsleitung | `responsible_persons`, `admin_group` | `Event` | Personen oder Gruppe mit vollem Zugriff auf alle Anmeldungen |
| Ansichtsgruppe | `view_group` | `Event` | Gruppe, die Auswertungen sehen, aber nichts ändern darf |
| Einladende Gruppe | `inviting_group` | `Event` | In wessen Namen eingeladen wird |
| Eingeladene Gruppen | `invited_groups` | `Event` | Wer die Einladung sieht; leer = alle |
| Anmeldeebene | `registration_level` | `Event` | Auf welcher Ebene angemeldet wird, meist Stamm |
| Ort | `EventLocation` | `anmelde_tool/event/models.py` | Veranstaltungsort mit Adresse |
| Buchungsoption | `BookingOption` | `anmelde_tool/event/models.py` | Preisstufe, z. B. „Standard 25 €“ oder „nur Wochenende“ |
| Baustein / Schritt | `EventModule` | `anmelde_tool/event/models.py` | Ein Schritt im Anmeldeablauf, z. B. „Teilnehmende“ oder „Anreise“ |
| Zusatzfeld | `AttributeModule` | `anmelde_tool/attributes/models.py` | Frage innerhalb eines Bausteins, z. B. „T-Shirt-Größe“ |
| Antwort auf ein Zusatzfeld | `BooleanAttribute`, `StringAttribute`, `TravelAttribute`, … | `anmelde_tool/attributes/models.py` | Antwort einer Anmeldung, je nach Feldtyp |
| Anmeldung | `Registration` | `anmelde_tool/registration/models.py` | Die Anmeldung einer Gruppe oder eines Stamms zu einer Veranstaltung |
| Anmeldende Leitung | `Registration.responsible_persons` | `Registration` | Wer die Anmeldung angelegt hat und sie bearbeiten darf |
| Teilnehmende Person | `RegistrationParticipant` | `anmelde_tool/registration/models.py` | Eine angemeldete Person innerhalb einer Anmeldung |
| Bestätigt | `is_confirmed` | `Registration` | Die Leitung hat die Anmeldung im letzten Schritt abgeschickt |

## Fristen

Regeln: `docs/entscheidungen.md`, Logik: `anmelde_tool/event/deadlines.py`.

| Deutsch | Im Code | Bedeutung |
| --- | --- | --- |
| Anmeldestart | `registration_start` | Ab wann angemeldet werden kann |
| Offizieller Anmeldeschluss | `registration_deadline` | Wird angezeigt, sperrt aber nichts |
| Technische Sperre | `registration_closes_at` | Ab hier keine neuen Anmeldungen (optional) |
| Neue Anmeldungen gesperrt | `registration_closed` | Manueller Schalter |
| Letzte Änderung möglich | `last_possible_update` | Bis wann Anmeldungen geändert werden können; leer = Veranstaltungsbeginn |
| Änderungen gesperrt | `changes_closed` | Manueller Schalter |
| Phase | `phase` | Status für die Oberfläche: `upcoming`, `pending`, `just_editable`, `expired`, `archived` |

## Personen, Gruppen, Rechte

| Deutsch | Im Code | Wo | Bedeutung |
| --- | --- | --- | --- |
| Benutzerkonto | `CustomUser` | `authentication/models.py` | Login-Konto, verbunden mit Keycloak über `keycloak_id` |
| Person | `Person` | `authentication/models.py` | Persönliche Daten (Adresse, Geburtstag, Stamm); gehört zu einem Konto oder wurde von einer Leitung angelegt |
| Fahrtenname | `scout_name` | `Person`, `RegistrationParticipant` | Pfadfindername |
| Pfadfinderstruktur | `ScoutHierarchy` | `basic/models.py` | Verband → Bund → Ring → Stamm → Gruppe, als Baum über `parent` |
| Ebene | `ScoutOrgaLevel`, `level_choice` | `basic/models.py` | Verband, Bund, Ring, Stamm, Gruppe |
| Gruppe (Keycloak) | `KeycloakGroup` | `keycloak_auth/models.py` | Abbild einer Keycloak-Gruppe im Tool; Stämme und Bünde haben je eine |
| Gruppenrecht | `GroupPermission` | `keycloak_auth/models.py` | Wer eine Gruppe verwalten (`admin`) oder einsehen (`view`) darf |
| Führungsgruppe | z. B. „Stammesführung“, „Bundesführung“ | Untergruppe in Keycloak | Ihre Mitglieder verwalten die Gruppe darüber |
| Beitrittsanfrage | `RequestGroupAccess` | `authentication/models.py` | Anfrage, in eine Gruppe aufgenommen zu werden |
| Anmeldeteam / Staff | `is_staff`, Rolle `anmelde_tool_team` | `CustomUser` | Hat überall Admin-Recht |

## Technik

| Begriff | Bedeutung |
| --- | --- |
| Keycloak | Gemeinsamer Login-Server des Verbands; liefert Login und Gruppenmitgliedschaften |
| Realm `dpv` | Der Bereich in Keycloak, in dem Konten und Gruppen des Verbands liegen |
| Endpunkt | Eine Adresse der Schnittstelle, z. B. `/event/registration/`; das Frontend ruft sie auf |
| Migration | Datei, die die Datenbank an ein geändertes Datenmodell anpasst |
| N+1-Muster | Eine Liste löst pro Eintrag eine neue Datenbankabfrage aus; wird bei vielen Einträgen langsam |
| `xfail` | Test für einen bekannten, noch offenen Fehler |
