"""Zugriffsschutz für Endpunkte, die früher ohne Prüfung erreichbar waren.

Grundregel seit Phase 3a: Jeder Endpunkt verlangt einen Login, außer er ist
ausdrücklich öffentlich (Registrierung, Auswahllisten, Kontaktformular).
"""
import pytest

pytestmark = pytest.mark.django_db


# --- Veranstaltungen ---------------------------------------------------------

class TestVeranstaltungAendern:

    def url(self, lager):
        return f'/event/event-update-partial/{lager.id}/'

    def test_ohne_login_gesperrt(self, client, lager):
        response = client.patch(self.url(lager), {'name': 'Gekapert'}, content_type='application/json')
        assert response.status_code == 401
        lager.refresh_from_db()
        assert lager.name == 'Sommerlager'

    def test_teilnehmer_gesperrt(self, api, teilnehmer, lager):
        response = api(teilnehmer).patch(self.url(lager), {'name': 'Gekapert'}, format='json')
        assert response.status_code == 403
        lager.refresh_from_db()
        assert lager.name == 'Sommerlager'

    def test_veranstaltungsleitung_darf(self, api, veranstaltungsleitung, lager):
        response = api(veranstaltungsleitung).patch(self.url(lager), {'name': 'Herbstlager'}, format='json')
        assert response.status_code == 200
        lager.refresh_from_db()
        assert lager.name == 'Herbstlager'


class TestKassenuebersicht:

    def url(self, lager):
        return f'/event/event/{lager.id}/summary/cash/'

    def test_ohne_login_gesperrt(self, client, lager, anmeldung_adler):
        assert client.get(self.url(lager)).status_code == 401

    def test_teilnehmer_gesperrt(self, api, teilnehmer, lager, anmeldung_adler):
        assert api(teilnehmer).get(self.url(lager)).status_code == 403

    def test_veranstaltungsleitung_darf(self, api, veranstaltungsleitung, lager, anmeldung_adler):
        assert api(veranstaltungsleitung).get(self.url(lager)).status_code == 200


# --- Anmeldungen -------------------------------------------------------------

class TestFremdeAnmeldung:
    """Eine andere Stammesleitung darf an der Adler-Anmeldung nichts tun."""

    @pytest.mark.parametrize('pfad', [
        'check-person/',
        'registration-rating/',
        'boolean-attribute/',
        'string-attribute/',
        'integer-attribute/',
        'float-attribute/',
        'date-time-attribute/',
        'travel-attribute/',
    ])
    def test_schreiben_gesperrt(self, api, fremde_leitung, anmeldung_adler, pfad):
        url = f'/event/registration/{anmeldung_adler.id}/{pfad}'
        assert api(fremde_leitung).post(url, {}, format='json').status_code == 403

    def test_bewertungen_lesen_gesperrt(self, api, fremde_leitung, anmeldung_adler):
        url = f'/event/registration/{anmeldung_adler.id}/registration-rating/'
        assert api(fremde_leitung).get(url).status_code == 403

    def test_bewertungen_ohne_login_gesperrt(self, client, anmeldung_adler):
        url = f'/event/registration/{anmeldung_adler.id}/registration-rating/'
        assert client.get(url).status_code == 401


# --- Vorlagen und Nachrichten ------------------------------------------------

def test_mailvorlagen_nur_staff_aendert(api, teilnehmer):
    assert api(teilnehmer).post('/event/email-sets/', {'name': 'X'}, format='json').status_code == 403


def test_mailvorlagen_ohne_login_gesperrt(client):
    assert client.get('/event/email-sets/').status_code == 401


def test_nachrichten_ohne_login_nicht_lesbar(client):
    assert client.get('/message/issue-init-create/').status_code in (401, 403)


def test_nachrichten_teilnehmer_nicht_lesbar(api, teilnehmer):
    assert api(teilnehmer).get('/message/issue-init-create/').status_code == 403


def test_nachrichtentypen_nur_staff_aendert(api, teilnehmer):
    assert api(teilnehmer).post('/message/issue-type/', {'name': 'X'}, format='json').status_code == 403


# --- Standard: Login nötig, Ausnahmen öffentlich -----------------------------

@pytest.mark.parametrize('pfad', ['/food/recipe/', '/inspi/activity/', '/basic/search/'])
def test_standard_verlangt_login(client, pfad):
    assert client.get(pfad).status_code == 401


@pytest.mark.parametrize('methode,pfad,daten', [
    ('post', '/auth/check-username/', {'username': 'neu'}),
    ('post', '/auth/check-email/', {'email': 'neu@example.org'}),
    ('post', '/auth/check-password/', {'password': 'Ein-langes-Passwort-2026'}),
    ('get', '/basic/gender/', None),
    ('get', '/event/choices/scout-level-types/', None),
    ('get', '/message/issue-type-read-short/', None),
])
def test_oeffentliche_endpunkte_ohne_login(client, methode, pfad, daten):
    if methode == 'post':
        response = client.post(pfad, daten, content_type='application/json')
    else:
        response = client.get(pfad)
    assert response.status_code not in (401, 403)
