"""Jede Anfrage des Frontends trifft eine Adresse, die es im Backend gibt und die die Anfrageart erlaubt.

Qualität II, Schritt 2 (15.10.2026). Anlass: In PR #11 wurde eine Adresse
entfernt, die das Frontend für fast alle Veranstaltungsseiten braucht. Das
Frontend setzt sie aus Bausteinen zusammen, deshalb fand eine Textsuche sie
nicht. Die Aufrufe liest tools/frontend_aufrufe.py aus.

Bekannte, noch nicht behobene Abweichungen stehen mit Begründung in KNOWN_GAPS.
Wird eine davon behoben, schlägt test_bekannte_luecken_noch_aktuell an, und
der Eintrag muss weg.
"""
import importlib.util
import pathlib

import pytest
from django.urls import Resolver404, resolve

_spec = importlib.util.spec_from_file_location(
    'frontend_aufrufe', pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'frontend_aufrufe.py')
frontend_aufrufe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(frontend_aufrufe)

SAMPLE_ID = '00000000-0000-0000-0000-000000000001'

# (Methode, Pfad) -> warum die Abweichung bekannt ist und wo sie behoben wird
KNOWN_GAPS: dict[tuple[str, str], str] = {}


def backend_allows(method: str, path: str) -> tuple[bool, str]:
    """Gibt es die Adresse im Backend, und erlaubt sie die Methode? Liefert (ja/nein, Grund)."""
    sample = path.replace(frontend_aufrufe.PLACEHOLDER, SAMPLE_ID)
    try:
        match = resolve(sample)
    except Resolver404:
        return False, 'Adresse gibt es im Backend nicht'
    callback = match.func
    view_cls = getattr(callback, 'cls', None) or getattr(callback, 'view_class', None)
    # Erlaubt ist, was der Router zuordnet (z. B. get -> list), und bei ViewSets
    # zusätzlich jede direkt so benannte Methode (z. B. "def put"): DRF ruft
    # sie auch ohne Zuordnung auf.
    allowed = {name.upper() for name in (getattr(callback, 'actions', None) or {})}
    allowed |= {m.upper() for m in ('get', 'post', 'put', 'patch', 'delete') if hasattr(view_cls, m)}
    if method not in allowed:
        return False, f'Methode nicht erlaubt (erlaubt: {", ".join(sorted(allowed))})'
    return True, ''


def frontend_calls():
    """Alle Aufrufe des Frontends, außer denen in abgeschalteten Modulen (food, inspi)."""
    calls = frontend_aufrufe.all_calls()
    return [call for call in calls if not call.file.startswith('src/modules/inspi/')]


def test_alle_frontend_aufrufe_aufgeloest():
    """Das Werkzeug muss jeden Pfad auflösen können, sonst prüft der Abgleich nicht alles."""
    unresolved = [f'{call.file}:{call.line} {call.raw}' for call in frontend_calls() if call.path is None]
    assert not unresolved, 'Nicht auflösbare Aufrufe:\n' + '\n'.join(unresolved)


def test_frontend_aufrufe_treffen_backend():
    problems = []
    for call in frontend_calls():
        if call.path is None or (call.method, call.path) in KNOWN_GAPS:
            continue
        ok, reason = backend_allows(call.method, call.path)
        if not ok:
            problems.append(f'{call.method} {call.path} ({call.file}:{call.line}): {reason}')
    assert not problems, 'Frontend-Aufrufe ohne passende Backend-Adresse:\n' + '\n'.join(sorted(set(problems)))


@pytest.mark.parametrize('method,path', sorted(KNOWN_GAPS))
def test_bekannte_luecken_noch_aktuell(method, path):
    """Jede bekannte Lücke muss noch bestehen und noch im Frontend vorkommen, sonst den Eintrag entfernen."""
    assert any(call.method == method and call.path == path for call in frontend_calls()), 'Aufruf gibt es nicht mehr'
    assert not backend_allows(method, path)[0], 'Lücke ist behoben, Eintrag aus KNOWN_GAPS entfernen'


def test_werkzeug_findet_zusammengesetzte_pfade():
    """Gegenprobe: Die beiden Pfade, die eine Textsuche in PR #11 übersehen hatte, werden erkannt."""
    paths = {(call.method, call.path) for call in frontend_calls()}
    assert ('GET', '/event/event-read/{x}/') in paths
    assert ('GET', '/auth/my-members-addable/') in paths


def test_karte_der_schnittstellen_aktuell():
    """docs/schnittstellen.md passt zum Code. Sonst: tools/schnittstellen_karte.py ausführen."""
    spec = importlib.util.spec_from_file_location(
        'schnittstellen_karte', pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'schnittstellen_karte.py')
    karte = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(karte)
    assert karte.OUTPUT.read_text(encoding='utf-8') == karte.render(), (
        'docs/schnittstellen.md ist veraltet. Im Ordner backend/ ausführen: '
        'DJANGO_SETTINGS_MODULE=backend.settings_test .venv/bin/python tools/schnittstellen_karte.py')
