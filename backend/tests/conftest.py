"""Gemeinsame Testdaten für die Backend-Tests.

Keycloak wird durch FakeKeycloak ersetzt. Jeder Aufruf, den die Fälschung nicht
kennt, lässt den Test scheitern. So fällt sofort auf, wenn Code unerwartet mit
Keycloak spricht.
"""
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from anmelde_tool.event.models import Event
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from authentication.models import CustomUser, Person
from backend import settings as project_settings
from basic.models import ScoutHierarchy, ScoutOrgaLevel
from keycloak_auth.models import KeycloakGroup


class FakeKeycloak:
    """Ersetzt den Keycloak-Admin-Client. Kennt nur Gruppenmitgliedschaften."""

    def __init__(self):
        self.user_groups: dict[str, list[str]] = {}

    def get_user_groups(self, user_id, brief_representation=True, **kwargs):
        return [{'id': group_id} for group_id in self.user_groups.get(user_id, [])]

    def __getattr__(self, name):
        raise AssertionError(f'Unerwarteter Keycloak-Aufruf im Test: keycloak_admin.{name}')


@pytest.fixture(autouse=True)
def fake_keycloak():
    fake = FakeKeycloak()
    previous = project_settings.keycloak_admin._wrapped
    project_settings.keycloak_admin._wrapped = fake
    yield fake
    project_settings.keycloak_admin._wrapped = previous


def make_user(username: str) -> CustomUser:
    user = CustomUser.objects.create_user(
        username=username,
        email=f'{username}@example.org',
        password='x',
        keycloak_id=f'kc-{username}',
    )
    Person.objects.create(user=user, first_name=username.capitalize(), last_name='Test')
    return user


@pytest.fixture
def stamm_level(db):
    return ScoutOrgaLevel.objects.create(id=5, name='Stamm')


@pytest.fixture
def stamm_adler(stamm_level):
    return ScoutHierarchy.objects.create(name='Adler', level=stamm_level)


@pytest.fixture
def stamm_falken(stamm_level):
    return ScoutHierarchy.objects.create(name='Falken', level=stamm_level)


@pytest.fixture
def veranstaltungsleitung(db):
    return make_user('lagerleitung')


@pytest.fixture
def anmeldende_leitung(db):
    """Stammesleitung der Adler, hat ihren Stamm angemeldet."""
    return make_user('adlerleitung')


@pytest.fixture
def fremde_leitung(db):
    """Stammesleitung der Falken, hat ihren eigenen Stamm angemeldet."""
    return make_user('falkenleitung')


@pytest.fixture
def teilnehmer(db):
    """Normales Mitglied ohne eigene Anmeldung."""
    return make_user('teilnehmer')


@pytest.fixture
def leitungsgruppe(db):
    # bulk_create umgeht das Speichersignal, das sonst Keycloak aufruft.
    # Die Gruppe gilt damit als "existiert bereits in Keycloak".
    (group,) = KeycloakGroup.objects.bulk_create(
        [KeycloakGroup(keycloak_id='00000000-0000-0000-0000-00000000aaaa', name='Lagerteam')]
    )
    return group


@pytest.fixture
def lager(stamm_level, veranstaltungsleitung):
    now = timezone.now()
    event = Event.objects.create(
        name='Sommerlager',
        is_public=True,
        registration_level=stamm_level,
        theme=None,
        registration_start=now - timedelta(days=1),
        registration_deadline=now + timedelta(days=30),
        last_possible_update=now + timedelta(days=40),
        start_date=now + timedelta(days=45),
        end_date=now + timedelta(days=48),
    )
    event.responsible_persons.add(veranstaltungsleitung)
    return event


def make_registration(event, stamm, leitung) -> Registration:
    registration = Registration.objects.create(event=event, scout_organisation=stamm)
    registration.responsible_persons.add(leitung)
    RegistrationParticipant.objects.create(
        registration=registration, first_name='Kim', last_name=f'Aus {stamm.name}',
        address='Lagerweg 1', phone_number='0123',
    )
    return registration


@pytest.fixture
def anmeldung_adler(lager, stamm_adler, anmeldende_leitung):
    return make_registration(lager, stamm_adler, anmeldende_leitung)


@pytest.fixture
def anmeldung_falken(lager, stamm_falken, fremde_leitung):
    return make_registration(lager, stamm_falken, fremde_leitung)


@pytest.fixture
def api():
    def client_for(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    return client_for
