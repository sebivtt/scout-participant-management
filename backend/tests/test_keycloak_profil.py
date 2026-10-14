"""Speichern persönlicher Daten darf das Keycloak-Konto nicht beschädigen.

Früher schickte das Backend beim Speichern nur die Zusatzfelder (Fahrtenname,
Stamm, ...) an Keycloak. Keycloak ab Version 24 behandelt das als vollständiges
Profil und löschte E-Mail, Vor- und Nachnamen. Danach lehnte das Backend jeden
Login dieser Person ab (fehlende E-Mail im Login-Token).
"""
import copy

import pytest

from authentication.signals import update_keycloak_profile

pytestmark = pytest.mark.django_db


class KeycloakKonto:
    """Spielt ein Keycloak-Konto nach, das Aktualisierungen als ganzes Profil ersetzt."""

    def __init__(self, fake, user):
        self.user = {
            'id': user.keycloak_id, 'username': user.username, 'email': user.email,
            'firstName': 'Sina', 'lastName': 'Stamm', 'enabled': True, 'emailVerified': True,
            'attributes': {'telefon': ['0123']},
        }
        fake.get_user = lambda keycloak_id: copy.deepcopy(self.user)
        fake.update_user = self.update_user

    def update_user(self, keycloak_id, payload):
        # Verhalten von Keycloak 26: fehlende Profilfelder werden geleert
        replaced = {key: payload.get(key) for key in ('username', 'email', 'firstName', 'lastName')}
        replaced['attributes'] = payload.get('attributes', {})
        self.user.update(replaced)


@pytest.fixture
def konto(fake_keycloak, anmeldende_leitung):
    return KeycloakKonto(fake_keycloak, anmeldende_leitung)


def test_attribute_aendern_behaelt_profil(konto, anmeldende_leitung):
    update_keycloak_profile(anmeldende_leitung.keycloak_id, attributes={'fahrtenname': 'Eule'})
    assert konto.user['email'] == anmeldende_leitung.email
    assert konto.user['firstName'] == 'Sina'
    assert konto.user['lastName'] == 'Stamm'
    assert konto.user['attributes'] == {'telefon': ['0123'], 'fahrtenname': ['Eule']}


def test_leerer_wert_entfernt_nur_dieses_attribut(konto, anmeldende_leitung):
    update_keycloak_profile(anmeldende_leitung.keycloak_id, attributes={'telefon': None})
    assert konto.user['attributes'] == {}
    assert konto.user['email'] == anmeldende_leitung.email


def test_persoenliche_daten_speichern_behaelt_email(api, konto, anmeldende_leitung, stamm_adler):
    response = api(anmeldende_leitung).put('/auth/personal-data/', {
        'firstName': 'Sina', 'lastName': 'Stamm', 'scoutName': 'Eule', 'scoutGroup': stamm_adler.id,
        'bundespost': 'nothing', 'leader': 'N', 'scoutLevel': 'N', 'gender': 'N',
    }, format='json')
    assert response.status_code == 200, response.content
    assert konto.user['email'] == anmeldende_leitung.email
    assert konto.user['firstName'] == 'Sina'
    assert konto.user['attributes']['fahrtenname'] == ['Eule']
    assert konto.user['attributes']['stamm'] == ['Adler']
