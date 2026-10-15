"""Dublettenprüfung: Ist eine Person schon für die Veranstaltung angemeldet?

Das Frontend fragt das beim Hinzufügen einer Person, damit die Meldung sofort
erscheint und nicht erst beim Abschicken (Entscheidung vom 15.10.2026).

Zwei Fälle, zwei Adressen:
- Neue Anmeldung: Es gibt noch keine Anmeldung, nur die Veranstaltung.
  Adresse /event/event/<Veranstaltung>/check-person/. Darf jede eingeloggte
  Person, solange neue Anmeldungen möglich sind, wie beim Anlegen einer
  Anmeldung selbst. Die Veranstaltungsleitung ist von Sperren ausgenommen.
- Bestehende Anmeldung: Adresse /event/registration/<Anmeldung>/check-person/,
  nur für die anmeldende Leitung und die Veranstaltungsleitung. Wird eine
  schon gespeicherte Person bearbeitet, zählt sie selbst nicht als Dublette.

Issue #19: Seit PR #3 erwartete die einzige Prüfadresse eine Anmeldung. Bei
einer neuen Anmeldung schickt das Frontend aber die Veranstaltung. Jede neue
Anmeldung mit Personen scheiterte deshalb mit „Registrierung nicht gefunden“.
"""
import pytest

from anmelde_tool.registration.models import RegistrationParticipant

GEBURTSTAG = '2012-05-01'


def person(first_name='Lena', last_name='Neu', birthday=GEBURTSTAG, **extra):
    return {'first_name': first_name, 'last_name': last_name, 'birthday': birthday, **extra}


@pytest.fixture
def kim_bei_den_falken(anmeldung_falken):
    return RegistrationParticipant.objects.create(
        registration=anmeldung_falken, first_name='Kim', last_name='Falke', birthday=GEBURTSTAG,
    )


@pytest.fixture
def mia_bei_den_adlern(anmeldung_adler):
    return RegistrationParticipant.objects.create(
        registration=anmeldung_adler, first_name='Mia', last_name='Adler', birthday=GEBURTSTAG,
    )


class TestNeueAnmeldung:
    """Prüfung über die Veranstaltung, solange es noch keine Anmeldung gibt."""

    @staticmethod
    def url(event):
        return f'/event/event/{event.id}/check-person/'

    def test_unbekannte_person_ist_keine_dublette(self, api, teilnehmer, lager):
        response = api(teilnehmer).post(self.url(lager), person(), format='json')
        assert response.status_code == 200

    def test_schon_angemeldete_person_wird_sofort_gemeldet(self, api, teilnehmer, lager, kim_bei_den_falken):
        response = api(teilnehmer).post(self.url(lager), person('Kim', 'Falke'), format='json')
        assert response.status_code == 400
        assert 'bereits' in response.data['detail']

    def test_gleicher_name_anderer_geburtstag_ist_keine_dublette(self, api, teilnehmer, lager, kim_bei_den_falken):
        response = api(teilnehmer).post(self.url(lager), person('Kim', 'Falke', '2011-01-01'), format='json')
        assert response.status_code == 200

    def test_mitgeschickte_kennung_hebt_dublette_nicht_auf(self, api, teilnehmer, lager, kim_bei_den_falken):
        # Bei einer neuen Anmeldung gibt es keine eigene gespeicherte Person,
        # die ausgenommen werden müsste. Eine Kennung im Inhalt zählt nicht.
        data = person('Kim', 'Falke', id=kim_bei_den_falken.id)
        response = api(teilnehmer).post(self.url(lager), data, format='json')
        assert response.status_code == 400

    def test_ohne_login_gesperrt(self, client, lager):
        assert client.post(self.url(lager), person(), content_type='application/json').status_code == 401

    def test_nach_manueller_sperre_gesperrt(self, api, teilnehmer, lager):
        lager.registration_closed = True
        lager.save()
        response = api(teilnehmer).post(self.url(lager), person(), format='json')
        assert response.status_code == 403

    def test_veranstaltungsleitung_trotz_sperre(self, api, veranstaltungsleitung, lager):
        lager.registration_closed = True
        lager.save()
        response = api(veranstaltungsleitung).post(self.url(lager), person(), format='json')
        assert response.status_code == 200

    def test_unbekannte_veranstaltung(self, api, teilnehmer, lager):
        url = '/event/event/00000000-0000-0000-0000-000000000000/check-person/'
        assert api(teilnehmer).post(url, person(), format='json').status_code == 404


class TestBestehendeAnmeldung:
    """Prüfung über die Anmeldung, beim Hinzufügen und Bearbeiten von Personen."""

    @staticmethod
    def url(registration):
        return f'/event/registration/{registration.id}/check-person/'

    def test_neue_person_ist_keine_dublette(self, api, anmeldende_leitung, anmeldung_adler):
        response = api(anmeldende_leitung).post(self.url(anmeldung_adler), person(), format='json')
        assert response.status_code == 200

    def test_person_einer_anderen_anmeldung_wird_gemeldet(
            self, api, anmeldende_leitung, anmeldung_adler, kim_bei_den_falken):
        response = api(anmeldende_leitung).post(
            self.url(anmeldung_adler), person('Kim', 'Falke'), format='json')
        assert response.status_code == 400

    def test_eigene_person_bearbeiten_ist_keine_dublette(
            self, api, anmeldende_leitung, anmeldung_adler, mia_bei_den_adlern):
        # Fehler seit PR #3: Die Prüfung fand die bearbeitete Person selbst.
        data = person('Mia', 'Adler', id=mia_bei_den_adlern.id)
        response = api(anmeldende_leitung).post(self.url(anmeldung_adler), data, format='json')
        assert response.status_code == 200

    def test_umbenennen_in_fremde_person_wird_gemeldet(
            self, api, anmeldende_leitung, anmeldung_adler, mia_bei_den_adlern, kim_bei_den_falken):
        data = person('Kim', 'Falke', id=mia_bei_den_adlern.id)
        response = api(anmeldende_leitung).post(self.url(anmeldung_adler), data, format='json')
        assert response.status_code == 400

    def test_kennung_einer_fremden_anmeldung_hebt_dublette_nicht_auf(
            self, api, anmeldende_leitung, anmeldung_adler, kim_bei_den_falken):
        # Ausgenommen wird nur eine Person der eigenen Anmeldung aus der Adresse.
        data = person('Kim', 'Falke', id=kim_bei_den_falken.id)
        response = api(anmeldende_leitung).post(self.url(anmeldung_adler), data, format='json')
        assert response.status_code == 400

    def test_unsinnige_kennung_ist_kein_serverfehler(
            self, api, anmeldende_leitung, anmeldung_adler, kim_bei_den_falken):
        data = person('Kim', 'Falke', id='keine-zahl')
        response = api(anmeldende_leitung).post(self.url(anmeldung_adler), data, format='json')
        assert response.status_code == 400

    def test_veranstaltungsleitung_darf_pruefen(self, api, veranstaltungsleitung, anmeldung_adler):
        response = api(veranstaltungsleitung).post(self.url(anmeldung_adler), person(), format='json')
        assert response.status_code == 200

    def test_veranstaltungsleitung_ueber_leitungsgruppe_darf_pruefen(
            self, api, teilnehmer, lager, leitungsgruppe, anmeldung_adler, fake_keycloak):
        lager.admin_group = leitungsgruppe
        lager.save()
        fake_keycloak.user_groups[teilnehmer.keycloak_id] = [leitungsgruppe.keycloak_id]
        response = api(teilnehmer).post(self.url(anmeldung_adler), person(), format='json')
        assert response.status_code == 200

    def test_fremde_leitung_gesperrt(self, api, fremde_leitung, anmeldung_adler):
        response = api(fremde_leitung).post(self.url(anmeldung_adler), person(), format='json')
        assert response.status_code == 403
