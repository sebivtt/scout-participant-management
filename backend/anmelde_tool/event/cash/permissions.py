from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.generics import get_object_or_404
from anmelde_tool.event.cash.models import CashIncome
from anmelde_tool.event.permissions import check_event_permission, EventRole
from anmelde_tool.registration.models import Registration


class IsCashResponsiblePerson(permissions.BasePermission):
    """Veranstaltungsleitung der Veranstaltung, zu der ein Zahlungseingang gehört.

    Geprüft werden die bestehende Zahlung (pk aus der URL) und die Anmeldung
    aus dem Inhalt der Anfrage, falls angegeben. Beide müssen zu einer
    Veranstaltung gehören, die die Person leitet. Sonst ließe sich eine
    fremde Zahlung in die eigene Veranstaltung umbuchen.
    """

    message = 'Du darfst diese Überweisung nicht bearbeiten'

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # Eine Zahlung ohne Anmeldung gehört zu keiner Veranstaltung mehr und
        # verschwände aus der Kasse. Das Feld darf deshalb nicht geleert werden.
        if 'registration' in request.data and request.data['registration'] is None:
            return False
        events = []
        registration_id: str = request.data.get('registration', None)
        if registration_id is not None:
            events.append(get_object_or_404(Registration, id=registration_id).event)
        pk: str = view.kwargs.get("pk", None)
        if pk is not None:
            cash_income: CashIncome = get_object_or_404(CashIncome, id=pk)
            if cash_income.registration is None:
                return False
            events.append(cash_income.registration.event)
        # Ohne Bezug zu einer Veranstaltung (z. B. Liste aller Zahlungen) kein Zugriff.
        return bool(events) and all(
            check_event_permission(event, request, admin_only=True) != EventRole.NONE for event in events)
