"""Adressen der Schnittstelle.

Essensplanung (food) und Programmideen (inspi) sind abgeschaltet: Jede
eingeloggte Person konnte dort Einträge anderer ändern oder löschen
(Entscheidung vom 15.10.2026, docs/entscheidungen.md). Die Apps bleiben in
INSTALLED_APPS, weil ihre Datenbanktabellen erhalten bleiben und die
Essensauswertung einer Veranstaltung (/event/.../summary/food/) Rechencode
aus food nutzt. Test: tests/test_abgeschaltete_module.py
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('basic/', include('basic.urls')),
    path('auth/', include('authentication.urls')),
    path('event/', include('anmelde_tool.urls')),
    path('message/', include('messaging.urls')),
    path('keycloak/', include('keycloak_auth.urls')),
]
