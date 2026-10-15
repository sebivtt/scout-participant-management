"""Sicherheit der Verwaltungsbefehle (python manage.py ...).

Gefunden in Qualität II, Schritt 1b-1 (15.10.2026), mit den Sicherheitsregeln
von ruff (Regelgruppe S).
"""
import io
import json
import pathlib
import ssl

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import override_settings

from basic.choices import StateChoices
from basic.management.commands import add_state
from basic.models import ZipCode

pytestmark = pytest.mark.django_db

BACKEND = pathlib.Path(__file__).resolve().parent.parent


# --- Admin-Konto mit festem Passwort -----------------------------------------
# add_users legt das Konto "admin" mit einem festen, öffentlich bekannten
# Passwort an. Das alte Startskript für den Server rief den Befehl bei jedem
# Start auf. Mit der Passwort-Anmeldung unter /admin/ hätte sich damit jeder
# als Administrator anmelden können.

def test_admin_konto_mit_festem_passwort_im_echtbetrieb_verweigert():
    with override_settings(DEBUG=False), pytest.raises(CommandError):
        call_command('add_users', stdout=io.StringIO())
    assert not get_user_model().objects.filter(username='admin').exists()


def test_admin_konto_mit_festem_passwort_lokal_moeglich():
    with override_settings(DEBUG=True):
        call_command('add_users', stdout=io.StringIO())
    assert get_user_model().objects.get(username='admin').is_superuser


def test_serverstart_legt_kein_admin_konto_an():
    commands = [line for line in (BACKEND / 'start.sh').read_text().splitlines()
                if not line.lstrip().startswith('#')]
    assert not any('add_users' in line for line in commands)


# --- Zertifikatsprüfung beim Abruf der Bundesländer ----------------------------
# add_state fragte einen externen Dienst ohne Prüfung des Zertifikats. Wer die
# Verbindung abfängt, hätte beliebige Bundesländer in die Datenbank schreiben
# können.

def test_bundeslaender_abruf_prueft_zertifikat(monkeypatch):
    ZipCode.objects.create(zip_code='99999', city='Musterstadt')
    seen_contexts = []

    class FakeResponse:
        def read(self):
            name = str(StateChoices.BE.label)
            return json.dumps({'facet_groups': [{'facets': [{'name': name}]}]}).encode()

    def fake_urlopen(url, *args, context=None, **kwargs):
        seen_contexts.append(context)
        return FakeResponse()

    monkeypatch.setattr(add_state.request, 'urlopen', fake_urlopen)
    call_command('add_state', stdout=io.StringIO())

    assert ZipCode.objects.get(zip_code='99999').state == StateChoices.BE
    assert seen_contexts, "Der Befehl hat keine Anfrage gestellt"
    # Ohne eigenen Kontext nutzt Python die sichere Standardeinstellung.
    for context in seen_contexts:
        assert context is None or (context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname)
