from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from keycloak_auth.permissions import IsStaffOrReadOnly
from . import models
from . import serializers

class StandardEmailViewSet(viewsets.ModelViewSet):
    # Lesen für Eingeloggte (Auswahl beim Anlegen einer Veranstaltung), Ändern nur Staff
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    queryset = models.StandardEmailRegistrationSet.objects.all()
    serializer_class = serializers.StandardEmailRegistrationSetSerializer
