"""Legt Beispieldaten für die lokale Entwicklung und die Rauchtests an.

Aufruf: `python manage.py load_sample_data` (bzw. mit `--reset`, um das
Beispiellager frisch anzulegen). Voraussetzung sind die Stammdaten aus
`data/main/` (Vorlage für Veranstaltungen, Stämme).

Angelegt wird eine Veranstaltung „Beispiellager“ so, wie sie beim Anlegen über
die Oberfläche entsteht, dazu eine Anmeldung mit zwei erfundenen Personen. Die
Rollen passen zu den Testkonten aus `dev/keycloak-setup.sh`:

- `leitung` leitet das Beispiellager,
- `stammesleitung` hat ihren Stamm angemeldet,
- `teilnehmer` hat keine Rolle und kann eine neue Anmeldung anlegen.
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from anmelde_tool.event.models import BookingOption, Event, EventLocation, StandardEventTemplate
from anmelde_tool.event.views import set_up_new_event
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from authentication.models import CustomUser, Person
from basic.choices import Gender
from basic.models import ScoutHierarchy, ScoutOrgaLevel, ZipCode

SAMPLE_EVENT_NAME = 'Beispiellager'
SAMPLE_LOCATION_NAME = 'Beispielzeltplatz'
STAMM_LEVEL_ID = 5

# Erfundene Personen. Keine echten Personendaten (CLAUDE.md).
SAMPLE_PARTICIPANTS = [
    {'first_name': 'Mia', 'last_name': 'Beispiel', 'gender': Gender.Female, 'birthday': (2012, 5, 4)},
    {'first_name': 'Leo', 'last_name': 'Muster', 'gender': Gender.Male, 'birthday': (2013, 9, 12)},
]


class Command(BaseCommand):
    """Legt das Beispiellager mit einer Anmeldung an, ohne vorhandene Daten zu verändern."""

    help = 'Legt Beispieldaten an (nur Entwicklung, verweigert ohne DEBUG=True).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Löscht das Beispiellager samt seiner Anmeldungen und legt es neu an.',
        )

    def handle(self, *args, **options):
        # Im Echtbetrieb würde der Befehl erfundene Konten und eine erfundene
        # Veranstaltung zwischen echte Daten mischen.
        if not settings.DEBUG:
            raise CommandError('Beispieldaten nur in der Entwicklung (DEBUG=True), nie im Echtbetrieb.')

        template = StandardEventTemplate.objects.filter(pk=1).first()
        if template is None:
            raise CommandError(
                'Die Vorlage für Veranstaltungen fehlt. Zuerst die Stammdaten laden: '
                'python manage.py loaddata data/main/*.json'
            )
        stamm = ScoutHierarchy.objects.filter(level_id=STAMM_LEVEL_ID).order_by('id').first()
        if stamm is None:
            raise CommandError(
                'Es gibt keinen Stamm. Zuerst die Stammdaten laden: python manage.py loaddata data/main/*.json'
            )

        with transaction.atomic():
            existing = Event.objects.filter(name=SAMPLE_EVENT_NAME)
            if existing.exists() and not options['reset']:
                self.stdout.write(
                    f'„{SAMPLE_EVENT_NAME}“ ist schon vorhanden, nichts geändert. Mit --reset neu anlegen.'
                )
                return
            # Anmeldungen hängen an der Veranstaltung und werden mitgelöscht.
            existing.delete()
            event = create_sample_event(template)
            create_sample_registration(event, stamm)

        self.stdout.write(self.style.SUCCESS(
            f'„{SAMPLE_EVENT_NAME}“ angelegt: Leitung „leitung“, '
            f'Anmeldung von „{stamm.name}“ durch „stammesleitung“ mit {len(SAMPLE_PARTICIPANTS)} Personen.'
        ))


def get_or_create_account(username: str) -> CustomUser:
    """Liefert das Konto zu einem Testkonto aus Keycloak und legt es an, falls es fehlt.

    Vorhandene Konten bleiben unverändert. Beim ersten Login ordnet das Backend
    das Konto über den Benutzernamen zu und ergänzt die Keycloak-Kennung selbst
    (`backend/OIDCAuthentication.py`).
    """
    user = CustomUser.objects.filter(username__iexact=username).first()
    if user is not None:
        return user
    user = CustomUser.objects.create_user(username=username, email=f'{username}@example.org')
    Person.objects.create(user=user, email=user.email)
    return user


def create_sample_event(template: StandardEventTemplate) -> Event:
    """Legt das Beispiellager an, offen für neue Anmeldungen und Änderungen.

    Die Daten liegen relativ zu heute, damit die Anmeldung bei jedem Aufruf offen ist.
    """
    now = timezone.now()
    location, _ = EventLocation.objects.get_or_create(
        name=SAMPLE_LOCATION_NAME,
        defaults={
            'description': 'Erfundener Ort für Beispieldaten',
            'address': 'Am Lagerfeuer 1',
            'zip_code': ZipCode.objects.order_by('id').first(),
        },
    )
    event = Event.objects.create(
        name=SAMPLE_EVENT_NAME,
        short_description='Beispielveranstaltung zum Ausprobieren',
        is_public=True,
        location=location,
        registration_level=ScoutOrgaLevel.objects.get(id=STAMM_LEVEL_ID),
        registration_start=now - timedelta(days=1),
        registration_deadline=now + timedelta(days=30),
        last_possible_update=now + timedelta(days=40),
        start_date=now + timedelta(days=45),
        end_date=now + timedelta(days=48),
    )
    event.responsible_persons.add(get_or_create_account('leitung'))
    set_up_new_event(event, template, price=15)
    return event


def create_sample_registration(event: Event, stamm: ScoutHierarchy) -> Registration:
    """Legt die Anmeldung eines Stamms durch die Testleitung `stammesleitung` an."""
    registration = Registration.objects.create(event=event, scout_organisation=stamm)
    registration.responsible_persons.add(get_or_create_account('stammesleitung'))
    booking_option = BookingOption.objects.get(event=event, name='Standard')
    for person in SAMPLE_PARTICIPANTS:
        year, month, day = person['birthday']
        RegistrationParticipant.objects.create(
            registration=registration,
            first_name=person['first_name'],
            last_name=person['last_name'],
            gender=person['gender'],
            birthday=timezone.make_aware(datetime(year, month, day)),
            scout_group=stamm,
            booking_option=booking_option,
        )
    return registration
