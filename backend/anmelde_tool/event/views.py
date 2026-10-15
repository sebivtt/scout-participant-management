from django.utils.dateparse import parse_datetime
from copy import deepcopy
from queue import Queue

from django.db.models import Q, QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound, MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.attributes.models import AttributeModule
from anmelde_tool.event import api_exceptions as event_api_exceptions
from anmelde_tool.event import helper as event_helper
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event import serializers as event_serializers
from anmelde_tool.event.models import StandardEventTemplate, Event, EventModule, EventLocation
from anmelde_tool.event.permissions import EventRole, check_event_permission
from basic.helper.get_property_ids import get_zipcode
from keycloak_auth.access import member_group_ids
from keycloak_auth.models import KeycloakGroup


def add_event_attribute(attribute_module: AttributeModule, event_module: EventModule) -> AttributeModule:
    new_attribute_module: AttributeModule = deepcopy(attribute_module)
    new_attribute_module.pk = None
    new_attribute_module.id = None
    new_attribute_module.standard = False
    new_attribute_module.event_module = event_module
    new_attribute_module.save()
    return new_attribute_module


def add_event_module(module: EventModule, event: Event) -> EventModule:
    new_module: EventModule = deepcopy(module)
    new_module.pk = None
    new_module.standard = False
    new_module.event = event
    new_module.save()
    for attribute_module in module.attributemodule_set.all():
        add_event_attribute(attribute_module, new_module)
    return new_module


class EventLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    queryset = EventLocation.objects.all()
    serializer_class = event_serializers.EventLocationSerializer

    def create(self, request, *args, **kwargs) -> Response:
        get_zipcode(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        get_zipcode(request)
        return super().update(request, *args, **kwargs)


class EventModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EventModule.objects.all()
    serializer_class = event_serializers.EventModuleSerializer


class EventReadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.EventReadSerializer

    def get_queryset(self):
        technical_name = self.request.query_params.get('technical_name', None)
        if technical_name is None:
            return Event.objects.all()
        return Event.objects.filter(technical_name=technical_name)


class MyInvitationsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.MyInvitationsSerializer

    def get_queryset(self):
        child_ids = list(member_group_ids(self.request))
        if self.request.user.person.scout_group and self.request.user.person.scout_group.keycloak:
            child_ids += [self.request.user.person.scout_group.keycloak.keycloak_id]
        child_groups = KeycloakGroup.objects.filter(keycloak_id__in=child_ids).prefetch_related('parent')

        q = Queue()
        for group in child_groups:
            q.put(group)

        parent_ids = set()
        while not q.empty():
            group = q.get()
            parent_ids.add(group.id)
            if group.parent:
                q.put(group.parent)

        return Event.objects \
            .filter((Q(invited_groups__in=parent_ids) | Q(invited_groups=None)) & Q(is_public=True)) \
            .distinct()


class EventDateValidationMixin:
    """Gemeinsame Datumsprüfung für Anlegen und Ändern von Veranstaltungen."""

    # Reihenfolge-Regeln für die Daten einer Veranstaltung (Fristregeln vom 14.10.2026):
    # (früheres Datum, späteres Datum, Fehler, falls das spätere vor dem früheren liegt)
    DATE_ORDER_RULES = (
        ('start_date', 'end_date', event_api_exceptions.EndBeforeStart),
        ('registration_start', 'registration_deadline',
         event_api_exceptions.RegistrationDeadlineBeforeRegistrationStart),
        ('registration_start', 'registration_closes_at',
         event_api_exceptions.RegistrationDeadlineBeforeRegistrationStart),
        # Änderungen enden spätestens mit Veranstaltungsbeginn
        ('last_possible_update', 'start_date', event_api_exceptions.StartBeforeLastChange),
    )

    def check_event_dates(self, request, event) -> bool:
        """Prüft, ob die Daten zueinander passen. Wirft den passenden Fehler, sonst True.

        event ist eine gespeicherte Veranstaltung oder ein dict mit validierten
        Daten (beim Anlegen). Geprüft wird nur, wenn die Anfrage ein Datum ändert.
        """
        fields = {field for rule in self.DATE_ORDER_RULES for field in rule[:2]}
        if all(request.data.get(field) is None for field in fields):
            return True

        def value(field):
            raw = request.data.get(field)
            if raw is None:
                raw = event.get(field) if isinstance(event, dict) else getattr(event, field, None)
            return parse_datetime(raw) if isinstance(raw, str) else raw

        for earlier, later, error in self.DATE_ORDER_RULES:
            earlier_value, later_value = value(earlier), value(later)
            if earlier_value and later_value and later_value < earlier_value:
                raise error
        return True


class EventViewSet(EventDateValidationMixin, viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsEventSuperResponsiblePerson]
    queryset = Event.objects.all()
    serializer_class = event_serializers.EventCompleteSerializer


    def create(self, request, *args, **kwargs) -> Response:

        price = request.data.get('price', str(15.00))
        del request.data['price']

        if (request.data.get('responsible_persons') is None) | (request.data.get('responsible_persons', []) == []):
            request.data['responsible_persons'] = [request.user.email, ]

        serializer: event_serializers.EventPostSerializer = event_serializers.EventPostSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.check_event_dates(request, serializer.validated_data)

        event: Event = serializer.save()
        event.responsible_persons.add(request.user)

        if price:
            event_models.BookingOption.objects.create(
                name='Standard',
                price=float(str(price).replace(",", ".")),
                event=event,
            )

        standard_event: StandardEventTemplate = event_helper.custom_get_or_404(
            event_api_exceptions.SomethingNotFound('Standard Event 1'),
            event_models.StandardEventTemplate,
            pk=1
        )

        add_event_module(standard_event.introduction, event)
        add_event_module(standard_event.participants, event)
        add_event_module(standard_event.letter, event)
        add_event_module(standard_event.summary, event)

        for mapper in standard_event.other_required_modules.all():
            add_event_module(mapper, event)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        event: Event = self.get_object()
        self.check_event_dates(request, event)

        return super().update(request, *args, **kwargs)


class EventPartialUpdateViewSet(EventDateValidationMixin, viewsets.ModelViewSet):
    '''
    You just need to provide the field which is to be modified.
    '''
    # Früher ohne Rechteprüfung: jede Person, auch ohne Login, konnte
    # beliebige Veranstaltungen ändern.
    permission_classes = [event_permissions.IsEventSuperResponsiblePerson]
    queryset = Event.objects.all()
    serializer_class = event_serializers.EventCompleteSerializer

    def update(self, request, *args, **kwargs):
        # PUT und PATCH ändern hier immer nur die mitgeschickten Felder
        self.check_event_dates(request, self.get_object())
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BookingOptionViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubEventResponsiblePersonOrReadOnly]
    serializer_class = event_serializers.BookingOptionSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        if not event_helper.is_valid_uuid(event_id):
            raise event_api_exceptions.NoUUID(event_id)

        is_leader = check_event_permission(event_id, self.request) == EventRole.ADMIN_ROLE
        today = timezone.now()

        # handle bookable range
        if is_leader:
            booking_item = event_models.BookingOption.objects.filter(event=event_id)
        else:
            booking_item = event_models.BookingOption.objects.filter(
                Q(event=event_id)
                & (Q(bookable_from__lte=today) | Q(bookable_from__isnull=True))
                & (Q(bookable_till__gte=today) | Q(bookable_till__isnull=True))
            ).order_by(
                "bookable_from"
            )
        return booking_item

    def create(self, request, *args, **kwargs) -> Response:
        if request.data.get('name', None) is None:
            request.data['name'] = 'Standard'
        event_id = self.kwargs.get("event_pk", None)

        if event_id is None:
            raise NotFound()

        event = event_helper.get_event(event_id)

        request.data['event'] = event_id

        if request.data.get('bookable_till', None) is None:
            request.data['bookable_till'] = event.start_date

        request.data["price"] = float(str(request.data["price"]).replace(",", "."))

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        if request.data.get('name', None) is None:
            request.data['name'] = self.get_object().name
        request.data['event'] = self.get_object().event.id
        if request.data.get("price"):
            if isinstance(request.data["price"], str):
                request.data["price"] = float(request.data["price"].replace(",", "."))
            else:
                request.data["price"] = float(request.data["price"])
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        if self.get_queryset().count() > 1:
            return super().destroy(request, *args, **kwargs)
        else:
            raise MethodNotAllowed(
                method='delete',
                detail='delete not allowed, because there must be at least one booking option'
            )


class AvailableEventModulesViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [event_permissions.IsSubEventSuperResponsiblePerson]
    serializer_class = event_serializers.EventModuleSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        mapper = EventModule.objects.filter(event=event_id).values_list('name', flat=True)
        return EventModule.objects.exclude(name__in=mapper).exclude(event__isnull=False).order_by('ordering')


class AssignedEventModulesViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubEventResponsiblePersonOrReadOnly]
    serializer_class = event_serializers.EventModuleSerializer

    def get_queryset(self) -> QuerySet:
        event_id = self.kwargs.get("event_pk", None)
        return EventModule.objects.filter(event=event_id).order_by('ordering')


class EventOverviewViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = event_serializers.EventOverviewSerializer

    def get_queryset(self) -> QuerySet:
        child_ids = list(member_group_ids(self.request))

        queryset = Event.objects.filter(
            Q(admin_group__keycloak_id__in=child_ids)
            | (Q(view_group__keycloak_id__in=child_ids) & Q(is_public=True))
            | Q(responsible_persons=self.request.user)
            | (Q(invited_groups=None) & Q(is_public=True))
            | Q(view_allow_subgroup=True)
        ).distinct()

        return queryset
