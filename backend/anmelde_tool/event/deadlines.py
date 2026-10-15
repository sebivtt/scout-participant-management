"""Fristregeln für Anmeldungen (entschieden am 14.10.2026).

Neue Anmeldungen
- frühestens ab registration_start
- der offizielle Anmeldeschluss (registration_deadline) sperrt NICHT;
  im Ehrenamt sind späte Anmeldungen üblich
- gesperrt, wenn registration_closed gesetzt ist (manuell)
- gesperrt ab registration_closes_at, falls gesetzt (technische Sperre)
- gesperrt, sobald keine Änderungen mehr möglich sind (siehe unten)

Änderungen an bestehenden Anmeldungen (auch Personen hinzufügen/entfernen)
- möglich bis last_possible_update; ist das leer, bis Veranstaltungsbeginn
- gesperrt, wenn changes_closed gesetzt ist (manuell)

Die Veranstaltungsleitung ist von allen Sperren ausgenommen.
"""
from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from anmelde_tool.event.models import Event


def _now(now: datetime | None) -> datetime:
    """Zeitpunkt der Prüfung; in Tests übergebbar."""
    return now or timezone.now()


def registration_started(event: Event, now: datetime | None = None) -> bool:
    """Hat die Anmeldephase begonnen? Ohne Anmeldestart gilt: ja."""
    return event.registration_start is None or _now(now) >= event.registration_start


def changes_until(event: Event) -> datetime | None:
    """Bis wann Anmeldungen geändert werden können: letzte Änderung, sonst Veranstaltungsbeginn."""
    return event.last_possible_update or event.start_date


def can_change(event: Event, now: datetime | None = None) -> bool:
    """Dürfen anmeldende Leitungen bestehende Anmeldungen noch ändern (auch Personen hinzufügen)?"""
    if event.changes_closed:
        return False
    until = changes_until(event)
    return until is None or _now(now) < until


def can_register(event: Event, now: datetime | None = None) -> bool:
    """Sind neue Anmeldungen möglich? Endet spätestens, wenn keine Änderungen mehr möglich sind."""
    now = _now(now)
    if not registration_started(event, now) or event.registration_closed:
        return False
    if event.registration_closes_at and now >= event.registration_closes_at:
        return False
    return can_change(event, now)


def phase(event: Event, now: datetime | None = None) -> str:
    """Kurzstatus für die Oberfläche.

    upcoming       Anmeldung hat noch nicht begonnen
    pending        neue Anmeldungen möglich
    just_editable  keine neuen Anmeldungen, Änderungen noch möglich
    expired        keine Änderungen mehr, Veranstaltung noch nicht vorbei
    archived       Veranstaltung ist vorbei
    """
    now = _now(now)
    if event.end_date and now >= event.end_date:
        return 'archived'
    if not registration_started(event, now):
        return 'upcoming'
    if can_register(event, now):
        return 'pending'
    if can_change(event, now):
        return 'just_editable'
    return 'expired'
