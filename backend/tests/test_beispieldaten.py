"""Beispieldaten für die lokale Entwicklung und die Rauchtests (Befehl load_sample_data).

Die Beispieldaten sollen wie echt angelegte Daten aussehen, damit die Rauchtests
dieselben Wege gehen wie Nutzende. Sie dürfen bestehende Daten in einer lokalen
Datenbank nie verändern und im Echtbetrieb gar nicht laufen.
"""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from anmelde_tool.event.deadlines import can_change, can_register
from anmelde_tool.event.models import BookingOption, Event, EventModule
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from authentication.models import CustomUser, Person
from basic.management.commands.load_sample_data import (
    FOREIGN_TECHNICAL_NAME, SAMPLE_EVENT_NAME, SAMPLE_TECHNICAL_NAME, TRIP_TECHNICAL_NAME,
)


@pytest.fixture
def entwicklung(settings):
    """Der Befehl läuft nur mit DEBUG=True, die Testeinstellungen haben DEBUG=False."""
    settings.DEBUG = True


@pytest.fixture
def stammdaten(standardvorlage, stamm_adler, stamm_falken):
    """Was der Befehl aus den Stammdaten braucht: Vorlage, einen Stamm und den Stamm Falken."""


@pytest.fixture
def beispieldaten(entwicklung, stammdaten):
    call_command('load_sample_data', verbosity=0)
    return Event.objects.get(name=SAMPLE_EVENT_NAME)


def baustein_namen(event):
    return sorted(EventModule.objects.filter(event=event).values_list('name', flat=True))


def test_beispiellager_hat_die_bausteine_wie_eine_im_tool_angelegte_veranstaltung(
        beispieldaten, api, veranstaltungsleitung, lager):
    # Vergleich mit dem echten Weg über die Oberfläche: Weicht die Vorlage einmal
    # ab, testen die Rauchtests sonst etwas, das so nie entsteht.
    response = api(veranstaltungsleitung).post('/event/event/', {
        'name': 'Über die Oberfläche', 'price': 15, 'responsiblePersons': [],
        'startDate': lager.start_date.isoformat(), 'endDate': lager.end_date.isoformat(),
        'registrationStart': lager.registration_start.isoformat(),
        'registrationDeadline': lager.registration_deadline.isoformat(),
    }, format='json')
    assert response.status_code == 201, response.content
    ueber_oberflaeche = Event.objects.get(name='Über die Oberfläche')

    assert baustein_namen(beispieldaten) == baustein_namen(ueber_oberflaeche)
    assert 'Tshirts' in baustein_namen(beispieldaten)
    assert list(BookingOption.objects.filter(event=beispieldaten).values_list('name', flat=True)) == ['Standard']


def test_beispiellager_ist_zur_anmeldung_offen(beispieldaten):
    assert can_register(beispieldaten)
    assert can_change(beispieldaten)


def test_rollen_der_testkonten(beispieldaten, stamm_adler):
    # leitung leitet die Veranstaltung, stammesleitung hat ihren Stamm angemeldet,
    # teilnehmer hat keine Rolle und kann eine neue Anmeldung anlegen.
    assert list(beispieldaten.responsible_persons.values_list('username', flat=True)) == ['leitung']
    registration = Registration.objects.get(event=beispieldaten)
    assert list(registration.responsible_persons.values_list('username', flat=True)) == ['stammesleitung']
    assert registration.scout_organisation == stamm_adler
    assert registration.registrationparticipant_set.count() == 2
    teilnehmer = CustomUser.objects.get(username='teilnehmer')
    assert not Event.objects.filter(responsible_persons=teilnehmer).exists()
    assert not Registration.objects.filter(responsible_persons=teilnehmer).exists()


def test_fremder_ort_fuer_issue_20(beispieldaten):
    # Die Beispielfahrt teilt ihren Ort mit einem Lager, das ihre Leitung nicht
    # leitet. Diesen Ort darf sie nicht ändern (Fehlerfall der Rauchtests zu #20).
    # Den Ort des Beispiellagers nutzt dagegen nur das Beispiellager.
    fahrt = Event.objects.get(technical_name=TRIP_TECHNICAL_NAME)
    fremd = Event.objects.get(technical_name=FOREIGN_TECHNICAL_NAME)
    assert fahrt.location == fremd.location
    assert list(fahrt.responsible_persons.values_list('username', flat=True)) == ['stammesleitung']
    assert not fremd.responsible_persons.filter(username='stammesleitung').exists()
    assert list(Event.objects.filter(location=beispieldaten.location)) == [beispieldaten]
    # Nicht öffentlich, damit sie nicht unter den Einladungen der Testkonten stehen.
    assert not fahrt.is_public and not fremd.is_public


def test_fremden_ort_darf_die_leitung_der_fahrt_nicht_aendern(beispieldaten, api):
    # Gegenprobe zur Regel aus PR #22 mit genau diesen Beispieldaten: Sonst könnte
    # der Fehlerfall der Rauchtests grün sein, weil der Ort gar nicht geteilt ist.
    # Die Gegenprobe für einen nicht geteilten Ort macht der Rauchtest beim
    # Beispiellager (die Leitung dort ist im Tool Staff, im Test hier nicht).
    stammesleitung = CustomUser.objects.get(username='stammesleitung')
    fahrt = Event.objects.get(technical_name=TRIP_TECHNICAL_NAME)
    response = api(stammesleitung).patch(f'/event/event-location/{fahrt.location_id}/',
                                         {'description': 'geändert'}, format='json')
    assert response.status_code == 403
    fahrt.location.refresh_from_db()
    assert fahrt.location.description != 'geändert'


def test_stammesmitglieder_des_teilnehmers(beispieldaten, stamm_falken):
    # „Stammesmitglied anmelden“ zeigt Personen, die man selbst angelegt hat. Mia
    # Beispiel ist schon im Beispiellager angemeldet, Ben Probe noch nicht.
    teilnehmer = CustomUser.objects.get(username='teilnehmer')
    mitglieder = Person.objects.filter(created_by=teilnehmer)
    assert sorted(mitglieder.values_list('first_name', flat=True)) == ['Ben', 'Mia']
    assert {person.scout_group for person in mitglieder} == {stamm_falken}
    mia = mitglieder.get(first_name='Mia')
    assert RegistrationParticipant.objects.filter(
        registration__event=beispieldaten, first_name=mia.first_name, last_name=mia.last_name,
        birthday__date=mia.birthday,
    ).exists()


def test_zweiter_aufruf_legt_nichts_doppelt_an(beispieldaten):
    vorher = zaehlung()
    call_command('load_sample_data', verbosity=0)
    assert zaehlung() == vorher


def zaehlung():
    return (Event.objects.count(), Registration.objects.count(), RegistrationParticipant.objects.count(),
            BookingOption.objects.count(), EventModule.objects.count(), CustomUser.objects.count(),
            Person.objects.count())


def test_eigene_veranstaltung_gleichen_namens_bleibt_bei_reset(entwicklung, stammdaten, lager):
    # Eine selbst angelegte Veranstaltung „Beispiellager“ ist nicht das Beispiellager
    # des Befehls und darf beim Zurücksetzen nicht verschwinden.
    lager.name = SAMPLE_EVENT_NAME
    lager.save()
    call_command('load_sample_data', verbosity=0)
    call_command('load_sample_data', '--reset', verbosity=0)
    assert Event.objects.filter(id=lager.id).exists()
    assert Event.objects.filter(name=SAMPLE_EVENT_NAME).count() == 2


def test_belegte_email_verstaendliche_meldung(entwicklung, stammdaten):
    CustomUser.objects.create_user(username='jemand', email='leitung@example.org')
    with pytest.raises(CommandError, match='gehört schon einem anderen Konto'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_erster_login_uebernimmt_vorab_angelegtes_konto(beispieldaten):
    # Der Befehl legt die Testkonten vorab an. Der erste Login über Keycloak muss
    # dieses Konto finden und ergänzen, statt ein zweites anzulegen.
    from backend.OIDCAuthentication import MyOIDCAB
    claims = {'sub': 'kc-stammesleitung', 'preferred_username': 'stammesleitung',
              'email': 'stammesleitung@example.org', 'given_name': 'Stamm', 'family_name': 'Leitung'}
    backend = MyOIDCAB()
    (konto,) = backend.filter_users_by_claims(claims)
    backend.update_user(konto, claims)
    konto.refresh_from_db()
    assert konto.keycloak_id == 'kc-stammesleitung'
    assert Registration.objects.get(event=beispieldaten).responsible_persons.get() == konto


def test_neu_anlegen_ersetzt_nur_die_beispieldaten(beispieldaten, anmeldung_adler):
    alte_id = beispieldaten.id
    vorher = zaehlung()
    call_command('load_sample_data', '--reset', verbosity=0)
    neu = Event.objects.get(name=SAMPLE_EVENT_NAME)
    assert neu.id != alte_id
    # Eigene Daten in der lokalen Datenbank bleiben unberührt, und es entsteht
    # nichts doppelt.
    assert Registration.objects.filter(id=anmeldung_adler.id).exists()
    assert Event.objects.exclude(
        technical_name__in=[SAMPLE_TECHNICAL_NAME, TRIP_TECHNICAL_NAME, FOREIGN_TECHNICAL_NAME]
    ).get() == anmeldung_adler.event
    assert zaehlung() == vorher


def test_aeltere_beispieldaten_hinweis_auf_reset(beispieldaten, capsys):
    # Wer die Beispieldaten vor den Rauchtests zum Anmeldeablauf angelegt hat,
    # bekommt einen Hinweis statt stiller Lücken.
    Event.objects.filter(technical_name__in=[TRIP_TECHNICAL_NAME, FOREIGN_TECHNICAL_NAME]).delete()
    call_command('load_sample_data')
    assert '--reset' in capsys.readouterr().out


def test_bestehende_konten_bleiben_unveraendert(entwicklung, stammdaten):
    vorhanden = CustomUser.objects.create_user(username='stammesleitung', email='eigene@example.org')
    call_command('load_sample_data', verbosity=0)
    vorhanden.refresh_from_db()
    assert vorhanden.email == 'eigene@example.org'
    assert CustomUser.objects.filter(username__iexact='stammesleitung').count() == 1


def test_im_echtbetrieb_verweigert(stammdaten):
    with pytest.raises(CommandError, match='DEBUG'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_ohne_stammdaten_verstaendliche_meldung(entwicklung, stamm_adler, stamm_falken):
    with pytest.raises(CommandError, match='Vorlage für Veranstaltungen fehlt'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_ohne_stamm_verstaendliche_meldung(entwicklung, standardvorlage):
    with pytest.raises(CommandError, match='Es gibt keinen Stamm'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_ohne_stamm_falken_verstaendliche_meldung(entwicklung, standardvorlage, stamm_adler):
    with pytest.raises(CommandError, match='Stamm „Falken“ fehlt'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()
