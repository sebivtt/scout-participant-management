"""Tests für die Rechteregeln aus der Ist-Stand-Analyse (Stand 14.10.2026).

| Rolle                    | darf                                              | darf nicht                     |
| Veranstaltungsleitung    | alle Anmeldungen sehen und auswerten              | -                              |
| Anmeldende Leitung       | eigene Anmeldung sehen und bis zur Frist ändern   | fremde Anmeldungen sehen       |
| Teilnehmende             | eigene Daten sehen                                | fremde Anmeldungen sehen       |

Tests mit `xfail(strict=True)` beschreiben bekannte Fehler: Sie schlagen heute
erwartungsgemäß fehl. Sobald jemand den Fehler behebt, meldet pytest den Test
als "XPASS" und der Lauf wird rot. Dann die Markierung entfernen.
"""
from datetime import timedelta

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


def reg_url(registration, suffix=''):
    return f'/event/registration/{registration.id}/{suffix}'


def summary_url(event, suffix=''):
    return f'/event/event/{event.id}/summary/{suffix}'


# --- Veranstaltungsleitung ---------------------------------------------------

class TestVeranstaltungsleitung:

    def test_sieht_auswertung(self, api, veranstaltungsleitung, lager, anmeldung_adler, anmeldung_falken):
        response = api(veranstaltungsleitung).get(summary_url(lager))
        assert response.status_code == 200

    def test_sieht_jede_anmeldung_im_detail(self, api, veranstaltungsleitung, anmeldung_adler, anmeldung_falken):
        client = api(veranstaltungsleitung)
        for anmeldung in (anmeldung_adler, anmeldung_falken):
            assert client.get(f'/event/registration-read/{anmeldung.id}/').status_code == 200

    def test_mitglied_der_leitungsgruppe_sieht_auswertung(
            self, api, fake_keycloak, teilnehmer, lager, leitungsgruppe, anmeldung_adler):
        lager.admin_group = leitungsgruppe
        lager.save()
        fake_keycloak.user_groups[teilnehmer.keycloak_id] = [leitungsgruppe.keycloak_id]
        assert api(teilnehmer).get(summary_url(lager)).status_code == 200

    def test_nur_lesegruppe_sieht_auswertung(
            self, api, fake_keycloak, teilnehmer, lager, leitungsgruppe, anmeldung_adler):
        lager.view_group = leitungsgruppe
        lager.save()
        fake_keycloak.user_groups[teilnehmer.keycloak_id] = [leitungsgruppe.keycloak_id]
        assert api(teilnehmer).get(summary_url(lager)).status_code == 200

    def test_fremde_veranstaltung_bleibt_gesperrt(self, api, veranstaltungsleitung, lager, stamm_level, anmeldung_adler):
        from anmelde_tool.event.models import Event
        anderes_lager = Event.objects.create(name='Winterlager', registration_level=stamm_level, theme=None)
        assert api(veranstaltungsleitung).get(summary_url(anderes_lager)).status_code == 403


# --- Anmeldende Leitung ------------------------------------------------------

class TestAnmeldendeLeitung:

    def test_sieht_eigene_anmeldung(self, api, anmeldende_leitung, anmeldung_adler):
        response = api(anmeldende_leitung).get(f'/event/registration-read/{anmeldung_adler.id}/')
        assert response.status_code == 200

    def test_sieht_eigene_teilnehmende(self, api, anmeldende_leitung, anmeldung_adler):
        response = api(anmeldende_leitung).get(reg_url(anmeldung_adler, 'single-participant/'))
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_eigene_anmeldung_in_meiner_liste(self, api, anmeldende_leitung, anmeldung_adler, anmeldung_falken):
        response = api(anmeldende_leitung).get('/event/my-registrations/')
        assert response.status_code == 200
        assert [r['id'] for r in response.json()] == [str(anmeldung_adler.id)]

    @pytest.mark.parametrize('pfad', [
        'registration-read/{id}/',
        'registration/{id}/',
        'registration/{id}/single-participant/',
        'registration/{id}/summary/',
        'registration/{id}/cash-detail/',
    ])
    def test_sieht_keine_fremde_anmeldung(self, api, anmeldende_leitung, anmeldung_falken, pfad):
        url = '/event/' + pfad.format(id=anmeldung_falken.id)
        assert api(anmeldende_leitung).get(url).status_code == 403

    def test_sieht_keine_auswertung_der_veranstaltung(self, api, anmeldende_leitung, lager, anmeldung_adler):
        assert api(anmeldende_leitung).get(summary_url(lager)).status_code == 403

    def test_kann_eigene_anmeldung_vor_frist_loeschen(self, api, anmeldende_leitung, anmeldung_adler):
        response = api(anmeldende_leitung).delete(reg_url(anmeldung_adler))
        assert response.status_code == 204

    def test_kann_eigene_anmeldung_nach_letzter_aenderung_nicht_loeschen(
            self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.last_possible_update = timezone.now() - timedelta(days=1)
        lager.registration_deadline = timezone.now() - timedelta(days=2)
        lager.save()
        response = api(anmeldende_leitung).delete(reg_url(anmeldung_adler))
        assert response.status_code >= 400

    @pytest.mark.xfail(strict=True, reason=(
        'Bekannter Fehler: Die Fristprüfung in RegistrationSingleParticipantViewSet '
        'prüft eine Klasse statt eines Rechts und greift deshalb nie.'
    ))
    def test_kann_teilnehmende_nach_letzter_aenderung_nicht_mehr_aendern(
            self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.last_possible_update = timezone.now() - timedelta(days=1)
        lager.save()
        teilnehmend = anmeldung_adler.registrationparticipant_set.first()
        response = api(anmeldende_leitung).put(
            reg_url(anmeldung_adler, f'single-participant/{teilnehmend.id}/'),
            {'firstName': 'Kim', 'lastName': 'Geändert', 'gender': 'N'},
            format='json',
        )
        assert response.status_code >= 400

    @pytest.mark.xfail(strict=True, reason=(
        'Bekannter Fehler: Neue Anmeldungen werden auch nach Anmeldeschluss angenommen.'
    ))
    def test_keine_neue_anmeldung_nach_anmeldeschluss(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_deadline = timezone.now() - timedelta(days=1)
        lager.save()
        response = api(anmeldende_leitung).post(
            '/event/registration/', {'event': str(lager.id), 'scoutOrganisation': stamm_adler.id}, format='json')
        assert response.status_code >= 400


# --- Teilnehmende ohne eigene Anmeldung -------------------------------------

class TestTeilnehmende:

    @pytest.mark.parametrize('pfad', [
        'registration-read/{reg}/',
        'registration/{reg}/',
        'registration/{reg}/single-participant/',
        'registration/{reg}/summary/',
        'registration/{reg}/cash-detail/',
        'event/{event}/summary/',
        'event/{event}/summary/detailed/',
        'event/{event}/summary/parents/',
        'event/{event}/summary/cash-list/',
        'event/{event}/summary/participant-locations/',
    ])
    def test_sieht_keine_fremden_daten(self, api, teilnehmer, lager, anmeldung_adler, pfad):
        url = '/event/' + pfad.format(reg=anmeldung_adler.id, event=lager.id)
        assert api(teilnehmer).get(url).status_code == 403

    def test_meine_anmeldungen_ist_leer(self, api, teilnehmer, anmeldung_adler):
        response = api(teilnehmer).get('/event/my-registrations/')
        assert response.status_code == 200
        assert response.json() == []

    def test_kann_fremde_anmeldung_nicht_loeschen(self, api, teilnehmer, anmeldung_adler):
        assert api(teilnehmer).delete(reg_url(anmeldung_adler)).status_code == 403


# --- Nicht angemeldet --------------------------------------------------------

@pytest.mark.parametrize('pfad', [
    '/event/my-registrations/',
    '/event/event-overview/',
    '/auth/personal-data/',
])
def test_ohne_login_kein_zugriff(client, pfad):
    assert client.get(pfad).status_code == 401


# --- Bekannte Serverfehler ---------------------------------------------------

@pytest.mark.xfail(strict=True, reason='Bekannter Fehler: Liste ohne ID führt zu Serverfehler 500 statt 403.')
@pytest.mark.parametrize('pfad', ['/event/event/', '/event/registration/'])
def test_listen_ohne_id_liefern_keinen_serverfehler(api, teilnehmer, pfad):
    assert api(teilnehmer).get(pfad).status_code in (403, 405)
