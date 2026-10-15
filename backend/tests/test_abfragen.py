"""Effizienz: Listen dürfen nicht pro Eintrag neue Datenbankabfragen auslösen.

Jeder Test misst eine Seite mit 1 und mit 10 Einträgen. Bleibt die Zahl der
Abfragen gleich, skaliert die Seite. Wächst sie mit, liegt ein N+1-Muster vor:
Bei einem Bundeslager mit 100 Gruppen würde die Seite dann hunderte bis
tausende Abfragen auslösen. Siehe CONTRIBUTING.md, Abschnitt 4.

Gemessen am 15.10.2026 (Abfragen bei 1 → 10 Einträgen):
  Veranstaltungsübersicht      9 →  45
  Meine Einladungen            5 →  23
  Auswertung Anmeldungen      17 → 116
  Kassenliste                 15 → 105
  Meine Anmeldungen           12 → 111
  Gruppenliste                 8 →  71
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from anmelde_tool.event.models import Event
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from basic.models import ScoutHierarchy
from keycloak_auth.models import KeycloakGroup

pytestmark = pytest.mark.django_db

# Kleine Schwankungen (z. B. eine zusätzliche Abfrage für Seitennummern) sind erlaubt
TOLERANCE = 2


class DoesNotScale(AssertionError):
    """Die Seite braucht bei 10 Einträgen mehr Abfragen als bei einem.

    Nur dieser Fehler gilt bei den bekannten Problemen als "erwartet". Andere
    Fehler (Seite antwortet nicht mit 200, Verschlechterung) lassen den Test
    trotzdem scheitern.
    """


def query_count(client, url) -> int:
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200, (url, response.status_code)
    return len(ctx.captured_queries)


def add_events(n, template, manager):
    for _ in range(n):
        event = Event.objects.create(
            name=f'Lager {Event.objects.count()}', is_public=True, theme=None,
            registration_level=template.registration_level,
            registration_start=template.registration_start, registration_deadline=template.registration_deadline,
            last_possible_update=template.last_possible_update,
            start_date=template.start_date, end_date=template.end_date,
        )
        event.responsible_persons.add(manager)


def add_registrations(n, event, leader, participants_each=3):
    for _ in range(n):
        stamm = ScoutHierarchy.objects.create(name=f'Stamm {ScoutHierarchy.objects.count()}',
                                              level=event.registration_level)
        registration = Registration.objects.create(event=event, scout_organisation=stamm)
        registration.responsible_persons.add(leader)
        RegistrationParticipant.objects.bulk_create(
            RegistrationParticipant(registration=registration, first_name=f'P{j}', last_name='Test')
            for j in range(participants_each)
        )


def add_groups(n):
    start = KeycloakGroup.objects.count()
    KeycloakGroup.objects.bulk_create(
        KeycloakGroup(keycloak_id=f'00000000-0000-0000-0000-{start + i + 1:012d}', name=f'Gruppe {start + i}')
        for i in range(n)
    )


def assert_scales(client, url, grow, known_with_ten=None):
    """Misst die Seite mit 1 und 10 Einträgen.

    known_with_ten: gemessener Wert eines bekannten Problems. Wird er
    überschritten, hat sich die Seite verschlechtert, und der Test scheitert
    hart, auch wenn das Problem als bekannt markiert ist.
    """
    grow(1)
    with_one = query_count(client, url)
    grow(9)
    with_ten = query_count(client, url)
    if known_with_ten is not None and with_ten > known_with_ten + TOLERANCE:
        raise AssertionError(f'{url}: verschlechtert, {with_ten} Abfragen bei 10 Einträgen (bekannt: {known_with_ten})')
    if with_ten > with_one + TOLERANCE:
        raise DoesNotScale(f'{url}: {with_one} Abfragen bei 1 Eintrag, {with_ten} bei 10')


def n_plus_one(page):
    return pytest.mark.xfail(strict=True, raises=DoesNotScale,
                             reason=f'Bekanntes N+1-Muster: {page} (Messung 15.10.2026)')


@n_plus_one('Veranstaltungsübersicht')
def test_veranstaltungsuebersicht(api, veranstaltungsleitung, lager):
    assert_scales(api(veranstaltungsleitung), '/event/event-overview/',
                  lambda n: add_events(n, lager, veranstaltungsleitung), known_with_ten=45)


@n_plus_one('Meine Einladungen')
def test_meine_einladungen(api, veranstaltungsleitung, lager):
    assert_scales(api(veranstaltungsleitung), '/event/my-invitations/',
                  lambda n: add_events(n, lager, veranstaltungsleitung), known_with_ten=23)


@n_plus_one('Auswertung der Anmeldungen')
def test_auswertung_anmeldungen(api, veranstaltungsleitung, anmeldende_leitung, lager):
    assert_scales(api(veranstaltungsleitung), f'/event/event/{lager.id}/summary/',
                  lambda n: add_registrations(n, lager, anmeldende_leitung), known_with_ten=116)


@n_plus_one('Kassenliste')
def test_kassenliste(api, veranstaltungsleitung, anmeldende_leitung, lager):
    assert_scales(api(veranstaltungsleitung), f'/event/event/{lager.id}/summary/cash-list/',
                  lambda n: add_registrations(n, lager, anmeldende_leitung), known_with_ten=105)


@n_plus_one('Meine Anmeldungen')
def test_meine_anmeldungen(api, anmeldende_leitung, lager):
    assert_scales(api(anmeldende_leitung), '/event/my-registrations/',
                  lambda n: add_registrations(n, lager, anmeldende_leitung), known_with_ten=111)


@n_plus_one('Gruppenliste')
def test_gruppenliste(api, veranstaltungsleitung):
    assert_scales(api(veranstaltungsleitung), '/keycloak/group/', add_groups, known_with_ten=71)
