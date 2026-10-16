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
from anmelde_tool.registration.models import Registration
from authentication.models import CustomUser
from basic.management.commands.load_sample_data import SAMPLE_EVENT_NAME


@pytest.fixture
def entwicklung(settings):
    """Der Befehl läuft nur mit DEBUG=True, die Testeinstellungen haben DEBUG=False."""
    settings.DEBUG = True


@pytest.fixture
def beispieldaten(entwicklung, standardvorlage, stamm_adler):
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
    assert not CustomUser.objects.filter(username='teilnehmer').exists()


def test_zweiter_aufruf_legt_nichts_doppelt_an(beispieldaten):
    call_command('load_sample_data', verbosity=0)
    assert Event.objects.filter(name=SAMPLE_EVENT_NAME).count() == 1
    assert Registration.objects.filter(event__name=SAMPLE_EVENT_NAME).count() == 1


def test_neu_anlegen_ersetzt_nur_das_beispiellager(beispieldaten, anmeldung_adler):
    alte_id = beispieldaten.id
    call_command('load_sample_data', '--reset', verbosity=0)
    neu = Event.objects.get(name=SAMPLE_EVENT_NAME)
    assert neu.id != alte_id
    # Eigene Daten in der lokalen Datenbank bleiben unberührt.
    assert Registration.objects.filter(id=anmeldung_adler.id).exists()
    assert Event.objects.count() == 2


def test_bestehende_konten_bleiben_unveraendert(entwicklung, standardvorlage, stamm_adler):
    vorhanden = CustomUser.objects.create_user(username='stammesleitung', email='eigene@example.org')
    call_command('load_sample_data', verbosity=0)
    vorhanden.refresh_from_db()
    assert vorhanden.email == 'eigene@example.org'
    assert CustomUser.objects.filter(username__iexact='stammesleitung').count() == 1


def test_im_echtbetrieb_verweigert(standardvorlage, stamm_adler):
    with pytest.raises(CommandError, match='DEBUG'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_ohne_stammdaten_verstaendliche_meldung(entwicklung, stamm_adler):
    with pytest.raises(CommandError, match='Stammdaten'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()


def test_ohne_stamm_verstaendliche_meldung(entwicklung, standardvorlage):
    with pytest.raises(CommandError, match='Stamm'):
        call_command('load_sample_data', verbosity=0)
    assert not Event.objects.exists()
