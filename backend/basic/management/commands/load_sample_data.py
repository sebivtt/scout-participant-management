"""Legt Beispieldaten für die lokale Entwicklung und die Rauchtests an.

Aufruf: `python manage.py load_sample_data` (bzw. mit `--reset`, um das
Beispiellager frisch anzulegen). Voraussetzung sind die Stammdaten aus
`data/main/` (Vorlage für Veranstaltungen, Stämme).

Angelegt wird eine Veranstaltung „Beispiellager“ so, wie sie beim Anlegen über
die Oberfläche entsteht, dazu eine Anmeldung mit zwei erfundenen Personen. Die
Rollen passen zu den Testkonten aus `dev/keycloak-setup.sh`:

- `leitung` leitet das Beispiellager und gehört zum Anmeldeteam,
- `stammesleitung` hat ihren Stamm angemeldet und leitet die „Beispielfahrt“,
- `teilnehmer` hat keine Rolle und kann eine neue Anmeldung anlegen. Für
  „Stammesmitglied anmelden“ hat er zwei selbst angelegte Personen aus seinem
  Stamm „Falken“.

Für den Fehlerfall aus Issue #20 nutzen die „Beispielfahrt“ und ein „Fremdes
Lager“, das `stammesleitung` nicht leitet, denselben Ort. Diesen Ort darf sie
deshalb nicht ändern. `leitung` dürfte es als Anmeldeteam (Staff) schon.
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
# Kennzeichen, an dem der Befehl sein Beispiellager erkennt. Am Namen allein
# nicht, sonst würde --reset eine selbst angelegte Veranstaltung „Beispiellager“
# samt Anmeldungen löschen.
SAMPLE_TECHNICAL_NAME = 'beispieldaten'
SAMPLE_LOCATION_NAME = 'Beispielzeltplatz'
STAMM_LEVEL_ID = 5

# Issue #20: Einen Ort, den auch eine fremde Veranstaltung nutzt, darf die
# Leitung nicht ändern. Dafür teilen sich die Beispielfahrt und das fremde Lager
# einen Ort. Die Beispielfahrt leitet stammesleitung, nicht leitung: leitung gehört
# zum Anmeldeteam (Staff) und darf jeden Ort ändern, der Fehlerfall träte nie ein.
TRIP_LEADER = 'stammesleitung'
SHARED_LOCATION_NAME = 'Geteilter Zeltplatz'
TRIP_EVENT_NAME = 'Beispielfahrt'
TRIP_TECHNICAL_NAME = 'beispielfahrt'
FOREIGN_EVENT_NAME = 'Fremdes Lager'
FOREIGN_TECHNICAL_NAME = 'fremdeslager'
# Leitet das fremde Lager. Ein Konto ohne Login in Keycloak genügt dafür.
FOREIGN_LEADER = 'fremde-leitung'

# Stamm des Testkontos teilnehmer, passend zum Gruppenbaum aus dev/keycloak-setup.sh.
MEMBER_STAMM_NAME = 'Falken'

# Erfundene Personen und Adresse. Keine echten Personendaten (CLAUDE.md).
SAMPLE_ADDRESS = 'Am Lagerfeuer 1'
SAMPLE_PARTICIPANTS = [
    {'first_name': 'Mia', 'last_name': 'Beispiel', 'gender': Gender.Female, 'birthday': (2012, 5, 4)},
    {'first_name': 'Leo', 'last_name': 'Muster', 'gender': Gender.Male, 'birthday': (2013, 9, 12)},
]

# Stammesmitglieder, die `teilnehmer` selbst angelegt hat. Mia Beispiel ist
# schon im Beispiellager angemeldet (gleicher Name und Geburtstag): An ihr prüfen
# die Rauchtests, dass eine schon angemeldete Person sofort gemeldet wird.
SAMPLE_MEMBERS = [
    {'first_name': 'Ben', 'last_name': 'Probe', 'gender': Gender.Male, 'birthday': (2012, 11, 23)},
    SAMPLE_PARTICIPANTS[0],
]


class Command(BaseCommand):
    """Legt die Beispieldaten an, ohne fremde Daten zu verändern."""

    help = 'Legt Beispieldaten an (nur Entwicklung, verweigert ohne DEBUG=True).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Löscht die Veranstaltungen der Beispieldaten samt ihrer Anmeldungen und legt sie neu an.',
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

        member_stamm = ScoutHierarchy.objects.filter(level_id=STAMM_LEVEL_ID, name=MEMBER_STAMM_NAME).first()
        if member_stamm is None:
            raise CommandError(
                f'Der Stamm „{MEMBER_STAMM_NAME}“ fehlt. Zuerst die Stammdaten laden: '
                'python manage.py loaddata data/main/*.json'
            )

        with transaction.atomic():
            if Event.objects.filter(technical_name=SAMPLE_TECHNICAL_NAME).exists() and not options['reset']:
                self.stdout.write(
                    f'„{SAMPLE_EVENT_NAME}“ ist schon vorhanden und bleibt unverändert. Mit --reset neu anlegen.'
                )
                if not Event.objects.filter(technical_name=TRIP_TECHNICAL_NAME).exists():
                    # Die Rauchtests zum Anmeldeablauf brauchen die Teile aus Schritt 1c.
                    self.stdout.write(self.style.WARNING(
                        'Die Beispieldaten sind älter als die Rauchtests zum Anmeldeablauf. '
                        'Bitte einmal mit --reset neu anlegen.'
                    ))
                return
            # Anmeldungen hängen an der Veranstaltung und werden mitgelöscht.
            Event.objects.filter(
                technical_name__in=[SAMPLE_TECHNICAL_NAME, TRIP_TECHNICAL_NAME, FOREIGN_TECHNICAL_NAME]
            ).delete()
            event = create_sample_event(template)
            create_sample_registration(event, stamm)
            create_shared_location_events(template)
            create_sample_members(member_stamm)

        self.stdout.write(self.style.SUCCESS(
            f'„{SAMPLE_EVENT_NAME}“ angelegt: Leitung „leitung“, '
            f'Anmeldung von „{stamm.name}“ durch „stammesleitung“ mit {len(SAMPLE_PARTICIPANTS)} Personen. '
            f'Dazu „{TRIP_EVENT_NAME}“ und „{FOREIGN_EVENT_NAME}“ am gemeinsamen Ort „{SHARED_LOCATION_NAME}“ '
            f'und {len(SAMPLE_MEMBERS)} Stammesmitglieder für „teilnehmer“.'
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
    email = f'{username}@example.org'
    # Die E-Mail muss eindeutig sein. Ohne diese Prüfung bräche der Befehl mit
    # einer unverständlichen Datenbankmeldung ab.
    if CustomUser.objects.filter(email__iexact=email).exists():
        raise CommandError(
            f'Die E-Mail {email} gehört schon einem anderen Konto als „{username}“. '
            f'Dieses Konto in der Django-Verwaltung (/admin/) umbenennen oder ihm eine andere E-Mail geben.'
        )
    user = CustomUser.objects.create_user(username=username, email=email)
    Person.objects.create(user=user, email=user.email)
    return user


def create_sample_event(template: StandardEventTemplate) -> Event:
    """Legt das Beispiellager an, offen für neue Anmeldungen und Änderungen."""
    location = get_or_create_location(SAMPLE_LOCATION_NAME, SAMPLE_ADDRESS)
    return create_event(SAMPLE_EVENT_NAME, SAMPLE_TECHNICAL_NAME, location, 'leitung', template, is_public=True)


def create_shared_location_events(template: StandardEventTemplate) -> None:
    """Legt die Beispielfahrt (Leitung `stammesleitung`) und ein fremdes Lager am selben Ort an (Issue #20).

    Beide sind nicht öffentlich, damit sie nicht unter den Einladungen der
    übrigen Testkonten erscheinen.
    """
    location = get_or_create_location(SHARED_LOCATION_NAME, 'Am Bach 2')
    create_event(TRIP_EVENT_NAME, TRIP_TECHNICAL_NAME, location, TRIP_LEADER, template, is_public=False)
    create_event(FOREIGN_EVENT_NAME, FOREIGN_TECHNICAL_NAME, location, FOREIGN_LEADER, template, is_public=False)


def get_or_create_location(name: str, address: str) -> EventLocation:
    """Liefert einen erfundenen Veranstaltungsort und legt ihn an, falls er fehlt."""
    location, _ = EventLocation.objects.get_or_create(
        name=name,
        defaults={
            'description': 'Erfundener Ort für Beispieldaten',
            'address': address,
            'zip_code': ZipCode.objects.order_by('id').first(),
        },
    )
    return location


def create_event(name: str, technical_name: str, location: EventLocation, leader: str,
                 template: StandardEventTemplate, *, is_public: bool) -> Event:
    """Legt eine Veranstaltung mit Leitung an, offen für neue Anmeldungen und Änderungen.

    Die Daten liegen relativ zu heute, damit die Anmeldung bei jedem Aufruf offen ist.
    """
    now = timezone.now()
    event = Event.objects.create(
        name=name,
        technical_name=technical_name,
        short_description='Beispielveranstaltung zum Ausprobieren',
        is_public=is_public,
        location=location,
        registration_level=ScoutOrgaLevel.objects.get(id=STAMM_LEVEL_ID),
        registration_start=now - timedelta(days=1),
        registration_deadline=now + timedelta(days=30),
        last_possible_update=now + timedelta(days=40),
        start_date=now + timedelta(days=45),
        end_date=now + timedelta(days=48),
    )
    event.responsible_persons.add(get_or_create_account(leader))
    set_up_new_event(event, template, price=15)
    return event


def create_sample_members(stamm: ScoutHierarchy) -> None:
    """Legt die Stammesmitglieder von `teilnehmer` an, soweit sie fehlen.

    Das Konto `teilnehmer` bekommt dafür keine Rolle. Es hat die Personen nur
    selbst angelegt, so wie beim dauerhaften Speichern einer Person in einer
    Anmeldung. Seinen eigenen Stamm übernimmt das Backend beim ersten Login aus
    Keycloak (Angaben stamm und bund, `dev/keycloak-setup.sh`).
    """
    account = get_or_create_account('teilnehmer')
    for member in SAMPLE_MEMBERS:
        year, month, day = member['birthday']
        if Person.objects.filter(created_by=account, first_name=member['first_name'],
                                 last_name=member['last_name']).exists():
            continue
        person = Person.objects.create(
            first_name=member['first_name'],
            last_name=member['last_name'],
            gender=member['gender'],
            birthday=datetime(year, month, day).date(),
            scout_group=stamm,
            address=SAMPLE_ADDRESS,
            zip_code=ZipCode.objects.order_by('id').first(),
        )
        person.created_by.add(account)


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
            # Adresse und Postleitzahl sind beim Bearbeiten Pflicht. Ohne sie ließe
            # sich eine Beispielperson nicht unverändert speichern.
            address=SAMPLE_ADDRESS,
            zip_code=ZipCode.objects.order_by('id').first(),
        )
    return registration
