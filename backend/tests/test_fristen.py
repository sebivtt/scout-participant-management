"""Fristregeln für Anmeldungen (entschieden am 14.10.2026).

- Der offizielle Anmeldeschluss sperrt nichts.
- Neue Anmeldungen sperren: technisch ab Datum oder manuell.
- Änderungen sind möglich bis "letzte Änderung möglich", sonst bis
  Veranstaltungsbeginn; manuell sperrbar.
- Die Veranstaltungsleitung ist von allen Sperren ausgenommen.
"""
from datetime import timedelta

import pytest
from django.utils import timezone

from anmelde_tool.event import deadlines

pytestmark = pytest.mark.django_db

TAG = timedelta(days=1)


def jetzt():
    return timezone.now()


def neue_anmeldung(api, user, lager, stamm):
    return api(user).post(
        '/event/registration/', {'event': str(lager.id), 'scoutOrganisation': stamm.id}, format='json')


def teilnehmende_aendern(api, user, anmeldung):
    person = anmeldung.registrationparticipant_set.first()
    return api(user).put(
        f'/event/registration/{anmeldung.id}/single-participant/{person.id}/',
        {'firstName': 'Kim', 'lastName': 'Geändert', 'gender': 'N'}, format='json')


def anmeldung_loeschen(api, user, anmeldung):
    return api(user).delete(f'/event/registration/{anmeldung.id}/')


# --- Neue Anmeldungen --------------------------------------------------------

class TestNeueAnmeldung:

    def test_nach_offiziellem_anmeldeschluss_weiter_moeglich(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_deadline = jetzt() - TAG
        lager.save()
        assert neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler).status_code == 201

    def test_vor_anmeldestart_gesperrt(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_start = jetzt() + TAG
        lager.save()
        assert neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler).status_code >= 400

    def test_technische_sperre_greift(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_closes_at = jetzt() - TAG
        lager.save()
        response = neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler)
        assert response.status_code == 403
        assert 'keine neuen Anmeldungen' in response.json()['detail']

    def test_technische_sperre_in_zukunft_noch_offen(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_closes_at = jetzt() + TAG
        lager.save()
        assert neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler).status_code == 201

    def test_manuelle_sperre_greift(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.registration_closed = True
        lager.save()
        assert neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler).status_code == 403

    def test_nach_veranstaltungsbeginn_gesperrt(self, api, anmeldende_leitung, lager, stamm_adler):
        lager.start_date = jetzt() - TAG
        lager.last_possible_update = None
        lager.save()
        assert neue_anmeldung(api, anmeldende_leitung, lager, stamm_adler).status_code == 403

    def test_veranstaltungsleitung_trotz_sperre(self, api, veranstaltungsleitung, lager, stamm_adler):
        lager.registration_closed = True
        lager.save()
        assert neue_anmeldung(api, veranstaltungsleitung, lager, stamm_adler).status_code == 201


# --- Änderungen an bestehenden Anmeldungen -----------------------------------

class TestAenderungen:

    def test_trotz_sperre_fuer_neue_anmeldungen_moeglich(self, api, anmeldende_leitung, lager, anmeldung_adler):
        # Krankheit, Änderungen: auch wenn keine neuen Anmeldungen mehr gehen
        lager.registration_closed = True
        lager.registration_deadline = jetzt() - TAG
        lager.save()
        assert teilnehmende_aendern(api, anmeldende_leitung, anmeldung_adler).status_code == 200

    def test_nach_letzter_aenderung_gesperrt(self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.last_possible_update = jetzt() - TAG
        lager.save()
        response = teilnehmende_aendern(api, anmeldende_leitung, anmeldung_adler)
        assert response.status_code == 403
        assert 'nicht mehr möglich' in response.json()['detail']

    def test_ohne_eigene_frist_bis_veranstaltungsbeginn(self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.last_possible_update = None
        lager.start_date = jetzt() + TAG
        lager.save()
        assert teilnehmende_aendern(api, anmeldende_leitung, anmeldung_adler).status_code == 200
        lager.start_date = jetzt() - TAG
        lager.save()
        assert teilnehmende_aendern(api, anmeldende_leitung, anmeldung_adler).status_code == 403

    def test_manuelle_sperre_greift(self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.changes_closed = True
        lager.save()
        assert teilnehmende_aendern(api, anmeldende_leitung, anmeldung_adler).status_code == 403

    def test_loeschen_folgt_der_aenderungsfrist(self, api, anmeldende_leitung, lager, anmeldung_adler):
        lager.changes_closed = True
        lager.save()
        assert anmeldung_loeschen(api, anmeldende_leitung, anmeldung_adler).status_code == 403
        lager.changes_closed = False
        lager.registration_deadline = jetzt() - TAG  # sperrte früher das Löschen, jetzt nicht mehr
        lager.save()
        assert anmeldung_loeschen(api, anmeldende_leitung, anmeldung_adler).status_code == 204

    def test_veranstaltungsleitung_trotz_sperre(self, api, veranstaltungsleitung, lager, anmeldung_adler):
        lager.changes_closed = True
        lager.last_possible_update = jetzt() - TAG
        lager.save()
        assert teilnehmende_aendern(api, veranstaltungsleitung, anmeldung_adler).status_code == 200


# --- Status für die Oberfläche -----------------------------------------------

class TestPhase:

    @pytest.mark.parametrize('aenderung,erwartet', [
        ({'registration_start': +1}, 'upcoming'),
        ({}, 'pending'),
        ({'registration_deadline': -1}, 'pending'),
        ({'registration_closed': True}, 'just_editable'),
        ({'registration_closes_at': -1}, 'just_editable'),
        ({'changes_closed': True}, 'expired'),
        ({'last_possible_update': -1}, 'expired'),
        ({'start_date': -3, 'end_date': -1}, 'archived'),
    ])
    def test_phase(self, lager, aenderung, erwartet):
        for feld, wert in aenderung.items():
            setattr(lager, feld, jetzt() + wert * TAG if isinstance(wert, int) and not isinstance(wert, bool) else wert)
        assert deadlines.phase(lager) == erwartet

    def test_einladung_zeigt_fristangaben(self, api, teilnehmer, lager):
        lager.registration_closed = True
        lager.save()
        response = api(teilnehmer).get('/event/my-invitations/')
        eintrag = next(e for e in response.json() if e['id'] == str(lager.id))
        assert eintrag['registrationOpen'] is False
        assert eintrag['changesOpen'] is True
        assert eintrag['phase'] == 'just_editable'


# --- Datumsprüfung beim Ändern der Veranstaltung -----------------------------

class TestDatumspruefung:

    def url(self, lager):
        return f'/event/event-update-partial/{lager.id}/'

    def test_aenderungen_ueber_beginn_hinaus_abgelehnt(self, api, veranstaltungsleitung, lager):
        response = api(veranstaltungsleitung).patch(
            self.url(lager), {'lastPossibleUpdate': (lager.start_date + TAG).isoformat()}, format='json')
        assert response.status_code == 400

    def test_aenderungen_bis_beginn_erlaubt(self, api, veranstaltungsleitung, lager):
        response = api(veranstaltungsleitung).patch(
            self.url(lager), {'lastPossibleUpdate': lager.start_date.isoformat()}, format='json')
        assert response.status_code == 200

    def test_aenderungsfrist_vor_anmeldeschluss_erlaubt(self, api, veranstaltungsleitung, lager):
        # Früher Pflicht: letzte Änderung nach Anmeldeschluss. Jetzt egal.
        response = api(veranstaltungsleitung).patch(
            self.url(lager), {'lastPossibleUpdate': (lager.registration_deadline - TAG).isoformat()}, format='json')
        assert response.status_code == 200

    def test_sperren_setzbar(self, api, veranstaltungsleitung, lager):
        response = api(veranstaltungsleitung).patch(self.url(lager), {
            'registrationClosed': True, 'changesClosed': True,
            'registrationClosesAt': (lager.registration_start + TAG).isoformat(),
        }, format='json')
        assert response.status_code == 200
        lager.refresh_from_db()
        assert lager.registration_closed and lager.changes_closed and lager.registration_closes_at
