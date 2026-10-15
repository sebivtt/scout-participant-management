from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from anmelde_tool.email_services.services import send_payment_reminder_mail, send_single_payment_reminder_mail
from anmelde_tool.event.cash import permissions as cash_permissions
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.helper import get_event, get_registration
from anmelde_tool.event.cash import serializers as cash_serializers
from anmelde_tool.event.cash import models as cash_models


class CashIncomeViewSet(viewsets.ModelViewSet):
    permission_classes = [cash_permissions.IsCashResponsiblePerson]
    serializer_class = cash_serializers.CashIncomeSerializer
    queryset = cash_models.CashIncome.objects.all()

    def create(self, request, *args, **kwargs):
        request.data["transfer_person"] = request.user.id

        request.data["amount"] = float(request.data["amount"].replace(",", "."))
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data["amount"] = float(request.data["amount"].replace(",", "."))
        return super().update(request, *args, **kwargs)


class MailReminderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Verschickt Zahlungserinnerungen an alle Anmeldungen einer Veranstaltung (nur Veranstaltungsleitung)."""

    # Die Veranstaltung steht im Inhalt der Anfrage, nicht in der URL. Eine
    # Rechteklasse, die auf die URL schaut, prüft hier deshalb nichts.
    permission_classes = [IsAuthenticated]
    serializer_class = cash_serializers.MailReminderSerializer

    def create(self, request, *args, **kwargs):
        """Prüft das Recht auf die Veranstaltung aus der Anfrage und stößt den Versand an."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = serializer.data["event_id"]
        if not event_permissions.is_event_manager(request, get_event(str(event_id))):
            raise PermissionDenied('Nur die Veranstaltungsleitung kann Zahlungserinnerungen verschicken.')
        send_payment_reminder_mail(event_id)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MailSingleReminderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Verschickt eine Zahlungserinnerung an eine Anmeldung (nur Veranstaltungsleitung)."""

    permission_classes = [IsAuthenticated]
    serializer_class = cash_serializers.MailSingleReminderSerializer

    def create(self, request, *args, **kwargs):
        """Prüft das Recht auf die Veranstaltung der Anmeldung und stößt den Versand an."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration_id = serializer.data["registration_id"]
        registration = get_registration(str(registration_id))
        if not event_permissions.is_event_manager(request, registration.event):
            raise PermissionDenied('Nur die Veranstaltungsleitung kann Zahlungserinnerungen verschicken.')
        send_single_payment_reminder_mail(registration_id)
        return Response(serializer.data, status=status.HTTP_200_OK)
