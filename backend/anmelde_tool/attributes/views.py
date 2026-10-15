from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.attributes.choices import TravelType, AttributeType
from anmelde_tool.attributes.models import AttributeModule, BooleanAttribute, IntegerAttribute, FloatAttribute, \
    StringAttribute, DateTimeAttribute, TravelAttribute
from anmelde_tool.attributes.serializers import AttributeModuleSerializer, BooleanUpdateAttributeSerializer, \
    IntegerUpdateAttributeSerializer, FloatUpdateAttributeSerializer, DateTimeUpdateAttributeSerializer, \
    TravelUpdateAttributeSerializer, StringUpdateAttributeSerializer
from anmelde_tool.event import permissions as event_permissions
from basic.helper.choice_to_json import choice_to_json


def require_attribute_module_admin(request, attribute_module) -> None:
    """Wirft PermissionDenied, wenn die Person das Zusatzfeld nicht ändern darf.

    Zusatzfelder einer Veranstaltung ändert nur deren Leitung. Vorlagen ohne
    Veranstaltung (Standardfelder) gelten für alle Veranstaltungen und sind
    deshalb dem Anmeldeteam (Staff) vorbehalten.
    """
    event_module = attribute_module.event_module if attribute_module else None
    event = event_module.event if event_module else None
    if event is None:
        if not request.user.is_staff:
            raise PermissionDenied('Vorlagen für Zusatzfelder kann nur das Anmeldeteam ändern.')
    elif not event_permissions.is_event_manager(request, event):
        raise PermissionDenied('Nur die Veranstaltungsleitung kann Zusatzfelder ändern.')


class AttributeModuleViewSet(viewsets.ModelViewSet):
    """Zusatzfelder (Fragen) einer Veranstaltung. Lesen alle Eingeloggten, ändern nur die Leitung."""

    permission_classes = [IsAuthenticated]
    serializer_class = AttributeModuleSerializer
    queryset = AttributeModule.objects.all()

    def perform_create(self, serializer):
        require_attribute_module_admin(self.request, AttributeModule(**serializer.validated_data))
        serializer.save()

    def perform_update(self, serializer):
        # Alte und neue Zuordnung prüfen: sonst ließe sich ein fremdes
        # Zusatzfeld in die eigene Veranstaltung holen oder umgekehrt.
        require_attribute_module_admin(self.request, serializer.instance)
        if 'event_module' in serializer.validated_data:
            require_attribute_module_admin(self.request, AttributeModule(**serializer.validated_data))
        serializer.save()

    def perform_destroy(self, instance):
        require_attribute_module_admin(self.request, instance)
        instance.delete()


class AttributeAnswerUpdateViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Ändert eine Antwort auf ein Zusatzfeld. Basisklasse für die Antworttypen unten.

    Nur Ändern ist möglich, denn mehr braucht das Frontend nicht: Angelegt
    werden Antworten über die Anmeldung (/event/registration/<id>/...-attribute/).
    Ändern darf, wer die Anmeldung bearbeiten darf, und nur bis zur
    Änderungsfrist (Veranstaltungsleitung ausgenommen).
    """

    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        registration = serializer.instance.registration
        if registration is None or not event_permissions.check_registration_permission(registration, self.request):
            raise PermissionDenied('Du darfst diese Anmeldung nicht bearbeiten.')
        event_permissions.require_changes_open(self.request, registration.event)
        serializer.save()


class BooleanAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = BooleanUpdateAttributeSerializer
    queryset = BooleanAttribute.objects.all()


class IntegerAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = IntegerUpdateAttributeSerializer
    queryset = IntegerAttribute.objects.all()


class FloatAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = FloatUpdateAttributeSerializer
    queryset = FloatAttribute.objects.all()


class StringAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = StringUpdateAttributeSerializer
    queryset = StringAttribute.objects.all()


class TravelAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = TravelUpdateAttributeSerializer
    queryset = TravelAttribute.objects.all()


class DateTimeAttributeViewSet(AttributeAnswerUpdateViewSet):
    serializer_class = DateTimeUpdateAttributeSerializer
    queryset = DateTimeAttribute.objects.all()


class TravelTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(TravelType.choices)
        return Response(result, status=status.HTTP_200_OK)


class AttributeTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        result = choice_to_json(AttributeType.choices)
        return Response(result, status=status.HTTP_200_OK)
