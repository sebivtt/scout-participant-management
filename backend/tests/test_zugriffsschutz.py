"""Zugriffsschutz für Endpunkte, die Qualität II (Schritt 1b-2) als offen gefunden hat.

Regeln (docs/entscheidungen.md, 14.10.2026): Die Veranstaltungsleitung darf
alles an ihrer Veranstaltung. Die anmeldende Leitung sieht und bearbeitet nur
die eigene Anmeldung. Wer weder das eine noch das andere ist, darf fremde
Anmeldungen und Veranstaltungen nicht sehen oder ändern.
"""
import pytest

from anmelde_tool.attributes.models import AttributeModule, StringAttribute
from anmelde_tool.event.models import EventLocation, EventModule

pytestmark = pytest.mark.django_db


@pytest.fixture
def baustein(lager):
    return EventModule.objects.create(name='Gesundheit', event=lager)


@pytest.fixture
def zusatzfeld(baustein):
    return AttributeModule.objects.create(title='Allergien', event_module=baustein, field_type='StA')


@pytest.fixture
def antwort_adler(anmeldung_adler, zusatzfeld):
    return StringAttribute.objects.create(
        registration=anmeldung_adler, attribute_module=zusatzfeld, string_field='Nüsse')


@pytest.fixture
def lagerort(lager):
    location = EventLocation.objects.create(name='Zeltplatz Waldwiese')
    lager.location = location
    lager.save()
    return location


# --- Antworten auf Zusatzfelder (/event/<typ>-attribute/) ----------------------
# Die Antworten gehören zu einer Anmeldung, z. B. Allergien oder Freitext.

class TestAntwortenAufZusatzfelder:

    def url(self, antwort=None):
        return '/event/string-attribute/' + (f'{antwort.id}/' if antwort else '')

    # Lesen und Löschen gibt es hier nicht mehr (405), das Frontend braucht nur Ändern.
    def test_fremde_leitung_sieht_fremde_antworten_nicht(self, api, fremde_leitung, antwort_adler):
        response = api(fremde_leitung).get(self.url())
        assert response.status_code in (403, 404, 405)

    def test_fremde_leitung_liest_fremde_antwort_nicht(self, api, fremde_leitung, antwort_adler):
        assert api(fremde_leitung).get(self.url(antwort_adler)).status_code in (403, 404, 405)

    def test_fremde_leitung_aendert_fremde_antwort_nicht(self, api, fremde_leitung, antwort_adler):
        response = api(fremde_leitung).put(self.url(antwort_adler), {'string_field': 'Gekapert'}, format='json')
        assert response.status_code in (403, 404)
        antwort_adler.refresh_from_db()
        assert antwort_adler.string_field == 'Nüsse'

    def test_fremde_leitung_loescht_fremde_antwort_nicht(self, api, fremde_leitung, antwort_adler):
        assert api(fremde_leitung).delete(self.url(antwort_adler)).status_code in (403, 404, 405)
        assert StringAttribute.objects.filter(id=antwort_adler.id).exists()

    def test_anmeldende_leitung_aendert_nach_aenderungsfrist_nicht(self, api, anmeldende_leitung, antwort_adler, lager):
        lager.changes_closed = True
        lager.save()
        response = api(anmeldende_leitung).put(self.url(antwort_adler), {'string_field': 'Keine'}, format='json')
        assert response.status_code != 200
        antwort_adler.refresh_from_db()
        assert antwort_adler.string_field == 'Nüsse'

    def test_anmeldende_leitung_aendert_eigene_antwort(self, api, anmeldende_leitung, antwort_adler):
        response = api(anmeldende_leitung).put(self.url(antwort_adler), {'string_field': 'Keine'}, format='json')
        assert response.status_code == 200
        antwort_adler.refresh_from_db()
        assert antwort_adler.string_field == 'Keine'


# --- Zusatzfelder selbst (/event/attribute-module/) ----------------------------
# Sie legen fest, was bei der Anmeldung gefragt wird.

class TestZusatzfelder:

    def url(self, feld):
        return f'/event/attribute-module/{feld.id}/'

    def test_teilnehmer_aendert_zusatzfeld_nicht(self, api, teilnehmer, zusatzfeld):
        response = api(teilnehmer).patch(self.url(zusatzfeld), {'title': 'Gekapert'}, format='json')
        assert response.status_code in (403, 404)
        zusatzfeld.refresh_from_db()
        assert zusatzfeld.title == 'Allergien'

    def test_teilnehmer_loescht_zusatzfeld_nicht(self, api, teilnehmer, zusatzfeld):
        assert api(teilnehmer).delete(self.url(zusatzfeld)).status_code in (403, 404)
        assert AttributeModule.objects.filter(id=zusatzfeld.id).exists()

    def test_veranstaltungsleitung_aendert_zusatzfeld(self, api, veranstaltungsleitung, zusatzfeld):
        response = api(veranstaltungsleitung).patch(self.url(zusatzfeld), {'title': 'Allergien und Unverträglichkeiten'}, format='json')
        assert response.status_code == 200


# --- Veranstaltungsorte (/event/event-location/) -------------------------------

class TestVeranstaltungsorte:

    def url(self, ort):
        return f'/event/event-location/{ort.id}/'

    def test_teilnehmer_aendert_fremden_ort_nicht(self, api, teilnehmer, lagerort):
        response = api(teilnehmer).patch(self.url(lagerort), {'name': 'Gekapert'}, format='json')
        assert response.status_code in (403, 404)
        lagerort.refresh_from_db()
        assert lagerort.name == 'Zeltplatz Waldwiese'

    def test_teilnehmer_loescht_fremden_ort_nicht(self, api, teilnehmer, lagerort):
        api(teilnehmer).delete(self.url(lagerort))
        assert EventLocation.objects.filter(id=lagerort.id).exists()


# --- Zahlungserinnerungen (/event/cash/mail-reminder/) -------------------------
# Lösen Mails an alle Anmeldungen einer Veranstaltung aus.

class TestZahlungserinnerungen:

    @pytest.fixture
    def versand(self, monkeypatch):
        calls = []
        monkeypatch.setattr('anmelde_tool.event.cash.views.send_payment_reminder_mail', calls.append)
        monkeypatch.setattr('anmelde_tool.event.cash.views.send_single_payment_reminder_mail', calls.append)
        return calls

    def test_teilnehmer_verschickt_keine_erinnerung_an_alle(self, api, teilnehmer, lager, versand):
        response = api(teilnehmer).post('/event/cash/mail-reminder/', {'event_id': str(lager.id)}, format='json')
        assert response.status_code == 403
        assert versand == []

    def test_fremde_leitung_verschickt_keine_einzelerinnerung(self, api, fremde_leitung, anmeldung_adler, versand):
        response = api(fremde_leitung).post(
            '/event/cash/mail-single-reminder/', {'registration_id': str(anmeldung_adler.id)}, format='json')
        assert response.status_code == 403
        assert versand == []

    def test_veranstaltungsleitung_verschickt_erinnerung(self, api, veranstaltungsleitung, lager, versand):
        response = api(veranstaltungsleitung).post('/event/cash/mail-reminder/', {'event_id': str(lager.id)}, format='json')
        assert response.status_code == 200
        assert versand == [str(lager.id)]


# --- Bausteine einer Veranstaltung (/event/event/<id>/assigned-event-modules/) --

class TestBausteine:

    def url(self, lager, baustein=None):
        return f'/event/event/{lager.id}/assigned-event-modules/' + (f'{baustein.id}/' if baustein else '')

    def test_teilnehmer_legt_keinen_baustein_an(self, api, teilnehmer, lager):
        response = api(teilnehmer).post(self.url(lager), {'name': 'Fremd', 'event': str(lager.id)}, format='json')
        assert response.status_code == 403
        assert not EventModule.objects.filter(name='Fremd').exists()

    def test_leitung_verschiebt_baustein_nicht_in_fremde_veranstaltung(
            self, api, veranstaltungsleitung, fremde_leitung, lager, baustein):
        from tests.conftest import Event
        fremdes_lager = Event.objects.create(
            name='Fremdes Lager', registration_level=lager.registration_level,
            registration_start=lager.registration_start, start_date=lager.start_date, end_date=lager.end_date)
        fremdes_lager.responsible_persons.add(fremde_leitung)
        api(veranstaltungsleitung).patch(self.url(lager, baustein), {'event': str(fremdes_lager.id)}, format='json')
        baustein.refresh_from_db()
        assert baustein.event_id == lager.id


# --- Veranstaltung über /event/event-read/ ------------------------------------
# Das Frontend nutzt diese Adresse nicht. Sie erlaubte jeder eingeloggten
# Person, jede Veranstaltung zu ändern oder zu löschen.

def test_teilnehmer_aendert_veranstaltung_nicht_ueber_event_read(api, teilnehmer, lager):
    api(teilnehmer).patch(f'/event/event-read/{lager.id}/', {'name': 'Gekapert'}, format='json')
    lager.refresh_from_db()
    assert lager.name == 'Sommerlager'


def test_teilnehmer_loescht_veranstaltung_nicht_ueber_event_read(api, teilnehmer, lager):
    from tests.conftest import Event
    api(teilnehmer).delete(f'/event/event-read/{lager.id}/')
    assert Event.objects.filter(id=lager.id).exists()


# --- Bausteine über /event/event/<id>/event-module/ ----------------------------

def test_teilnehmer_aendert_baustein_nicht(api, teilnehmer, lager, baustein):
    response = api(teilnehmer).patch(
        f'/event/event/{lager.id}/event-module/{baustein.id}/', {'name': 'Gekapert'}, format='json')
    assert response.status_code in (403, 404)
    baustein.refresh_from_db()
    assert baustein.name == 'Gesundheit'


def test_teilnehmer_loescht_baustein_nicht(api, teilnehmer, lager, baustein):
    api(teilnehmer).delete(f'/event/event/{lager.id}/event-module/{baustein.id}/')
    assert EventModule.objects.filter(id=baustein.id).exists()


# --- Zahlungseingänge (/event/cash/income/) -----------------------------------

def test_leitung_bucht_fremde_zahlung_nicht_in_eigene_veranstaltung(
        api, veranstaltungsleitung, fremde_leitung, lager, anmeldung_adler, stamm_falken):
    from anmelde_tool.event.cash.models import CashIncome
    from tests.conftest import Event, make_registration
    fremdes_lager = Event.objects.create(
        name='Fremdes Lager', registration_level=lager.registration_level,
        registration_start=lager.registration_start, start_date=lager.start_date, end_date=lager.end_date)
    fremdes_lager.responsible_persons.add(fremde_leitung)
    fremde_anmeldung = make_registration(fremdes_lager, stamm_falken, fremde_leitung)
    zahlung = CashIncome.objects.create(amount=25, registration=fremde_anmeldung)

    api(veranstaltungsleitung).put(
        f'/event/cash/income/{zahlung.id}/',
        {'amount': '0', 'registration': str(anmeldung_adler.id)}, format='json')
    zahlung.refresh_from_db()
    assert zahlung.registration_id == fremde_anmeldung.id
    assert zahlung.amount == 25


# --- Teilnehmende und Bewertungen einer Anmeldung -----------------------------
# Die Serializer geben alle Felder frei, auch "registration" und
# "booking_option". Die Anmeldung muss aus der URL kommen, die Preisstufe aus
# derselben Veranstaltung.

@pytest.fixture
def fremdes_lager(lager, fremde_leitung):
    from tests.conftest import Event
    event = Event.objects.create(
        name='Fremdes Lager', registration_level=lager.registration_level,
        registration_start=lager.registration_start, start_date=lager.start_date, end_date=lager.end_date)
    event.responsible_persons.add(fremde_leitung)
    return event


def test_leitung_verschiebt_teilnehmende_nicht_in_fremde_anmeldung(
        api, anmeldende_leitung, anmeldung_adler, anmeldung_falken):
    person = anmeldung_adler.registrationparticipant_set.first()
    api(anmeldende_leitung).put(
        f'/event/registration/{anmeldung_adler.id}/single-participant/{person.id}/',
        {'first_name': 'Kim', 'last_name': 'Aus Adler', 'registration': str(anmeldung_falken.id)}, format='json')
    person.refresh_from_db()
    assert person.registration_id == anmeldung_adler.id


def test_preisstufe_aus_fremder_veranstaltung_nicht_waehlbar(api, anmeldende_leitung, anmeldung_adler, fremdes_lager):
    from anmelde_tool.event.models import BookingOption
    gratis = BookingOption.objects.create(name='Gratis', price=0, event=fremdes_lager)
    person = anmeldung_adler.registrationparticipant_set.first()
    api(anmeldende_leitung).put(
        f'/event/registration/{anmeldung_adler.id}/single-participant/{person.id}/',
        {'first_name': 'Kim', 'last_name': 'Aus Adler', 'booking_option': gratis.id}, format='json')
    person.refresh_from_db()
    assert person.booking_option_id != gratis.id


def test_bewertung_nicht_an_fremde_anmeldung(api, anmeldende_leitung, anmeldung_adler, anmeldung_falken):
    from anmelde_tool.registration.models import RegistrationRating
    api(anmeldende_leitung).post(
        f'/event/registration/{anmeldung_adler.id}/registration-rating/',
        {'text': 'Fremd', 'score': 1, 'registration': str(anmeldung_falken.id)}, format='json')
    assert not RegistrationRating.objects.filter(registration=anmeldung_falken).exists()


# --- Benutzerkonten über /keycloak/members/ -----------------------------------
# Die Personensuche für Gruppenleitungen erlaubte früher auch Ändern und
# Löschen beliebiger Benutzerkonten. Das Frontend liest dort nur.

@pytest.fixture
def gruppenleitung(fremde_leitung, leitungsgruppe):
    from keycloak_auth.access import grant
    from keycloak_auth.models import GroupPermission
    grant(leitungsgruppe, GroupPermission.Role.ADMIN, user=fremde_leitung)
    return fremde_leitung


def test_gruppenleitung_findet_personen(api, gruppenleitung, teilnehmer):
    response = api(gruppenleitung).get('/keycloak/members/', {'search': 'teilnehmer'})
    assert response.status_code == 200


def test_gruppenleitung_aendert_fremdes_konto_nicht(api, gruppenleitung, teilnehmer):
    api(gruppenleitung).patch(f'/keycloak/members/{teilnehmer.id}/', {'email': 'gekapert@example.org'}, format='json')
    teilnehmer.refresh_from_db()
    assert teilnehmer.email == 'teilnehmer@example.org'


def test_gruppenleitung_loescht_fremdes_konto_nicht(api, gruppenleitung, teilnehmer):
    from authentication.models import CustomUser
    api(gruppenleitung).delete(f'/keycloak/members/{teilnehmer.id}/')
    assert CustomUser.objects.filter(id=teilnehmer.id).exists()


# --- Farbschemata (/basic/theme/) ----------------------------------------------

def test_teilnehmer_aendert_farbschema_nicht(api, teilnehmer):
    from basic.models import FrontendTheme
    theme = FrontendTheme.objects.create(name='Standard')
    api(teilnehmer).patch(f'/basic/theme/{theme.id}/', {'name': 'Gekapert'}, format='json')
    api(teilnehmer).delete(f'/basic/theme/{theme.id}/')
    theme.refresh_from_db()
    assert theme.name == 'Standard'


def test_teilnehmer_liest_farbschemata(api, teilnehmer):
    assert api(teilnehmer).get('/basic/theme/').status_code == 200
