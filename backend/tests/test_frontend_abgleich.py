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
    """Alle Aufrufe des Frontends, außer denen im abgeschalteten Modul Programmideen (inspi)."""
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


def test_frontend_nutzt_nur_erkannte_aufrufarten():
    """Das Werkzeug erkennt nur axios.get/post/put/patch/delete. Andere Schreibweisen fielen still durch."""
    import re
    other = re.compile(r'\bfetch\(|\baxios\(|\baxios\.(request|create)\b')
    found = []
    for path in frontend_aufrufe.FRONTEND_SRC.rglob('*'):
        if path.suffix not in ('.ts', '.vue') or 'modules/inspi/' in path.as_posix():
            continue
        text = frontend_aufrufe.strip_comments(frontend_aufrufe.script_part(path, path.read_text(encoding='utf-8')))
        found += [f'{path.relative_to(frontend_aufrufe.FRONTEND_SRC.parent)}: {m.group(0)}' for m in other.finditer(text)]
    assert not found, 'Neue Aufrufart, tools/frontend_aufrufe.py erweitern:\n' + '\n'.join(found)


def test_kommentarzeichen_in_zeichenketten_verschlucken_keine_aufrufe(tmp_path):
    """Ein "/*" in einer Zeichenkette ist kein Kommentar, die Aufrufe danach müssen erkannt werden."""
    source = 'const GLOB = "/*";\naxios.get(`${BASE_URL}/basic/gender/`);\nconst END = "*/";\n'
    assert '/basic/gender/' in frontend_aufrufe.strip_comments(source)


def test_importierte_konstante_gilt_als_unbekannt():
    """Eine nicht in der Datei definierte Konstante wird nicht zum Platzhalter, sondern als unbekannt gemeldet."""
    assert frontend_aufrufe.resolve_path('`${BASE_URL}/event/${IMPORTED}/`', {}) is None
    assert frontend_aufrufe.resolve_path('`${BASE_URL}/event/${id}/`', {}) == '/event/{x}/'


@pytest.mark.parametrize('source,expected', [
    ("// it's\nconst G = '/*';\naxios.get('/a/');\nconst E = '*/';", '/a/'),
    ("const r = /[\"']/g;\naxios.get('/b/');", '/b/'),
    ("const x = `${a ? \"x\" : 'y'}`;\naxios.get('/c/');", '/c/'),
    ("function t(p) { return /^\\/*$/.test(p) }\naxios.get('/d/');", '/d/'),
    ("const r = /\\[/.test(a) && axios.get('/e/') && x[0];", '/e/'),
])
def test_apostroph_oder_ausdruck_verschluckt_keine_aufrufe(source, expected):
    """Ein Apostroph im Kommentar, ein regulärer Ausdruck oder ${…} bringen das Lesen nicht durcheinander."""
    assert expected in frontend_aufrufe.strip_comments(source)


def test_vue_vorlagentext_wird_nicht_gelesen():
    """In .vue-Dateien zählt nur der <script>-Teil. Ein Apostroph im Seitentext ist keine Zeichenkette."""
    source = "<template><p>Gib's ein</p></template>\n<script>\nconst G = '/*';\naxios.get('/e/');\n</script>"
    text = frontend_aufrufe.strip_comments(frontend_aufrufe.script_part(pathlib.Path('x.vue'), source))
    assert '/e/' in text and "Gib's" not in text


@pytest.mark.parametrize('source', [
    "const a = 'offen;\naxios.get('/f/');",
    "const a = `offen ${b};\naxios.get('/f/');",
    "/* offen\naxios.get('/f/');",
])
def test_verlesen_wird_gemeldet(source):
    """Endet eine Datei in einer offenen Zeichenkette oder einem offenen Kommentar, meldet das Werkzeug das laut."""
    with pytest.raises(frontend_aufrufe.UnreadableSource):
        frontend_aufrufe.strip_comments(source)


def test_karte_zeigt_rechte_je_aktion():
    """Legt eine Klasse ihre Rechte je Aktion fest, zeigt die Karte die Rechte genau dieser Anfrageart."""
    karte_text = (pathlib.Path(__file__).resolve().parents[2] / 'docs' / 'schnittstellen.md').read_text(encoding='utf-8')
    assert '| POST | `/message/issue-init-create/` | `messaging.views.IssueInitCreateViewSet` | AllowAny |' in karte_text
    assert '| GET | `/keycloak/group/{x}/requests/` | `keycloak_auth.views.RequestGroupAccessViewSet` | IsAuthenticated, IsGroupAdmin |' in karte_text


def test_karte_meldet_unklare_rechte_statt_zu_raten():
    """Braucht get_permissions mehr als die Aktion, steht ein Hinweis in der Karte statt falscher Rechte."""
    spec = importlib.util.spec_from_file_location(
        'schnittstellen_karte', pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'schnittstellen_karte.py')
    karte = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(karte)

    class NeedsRequest:
        def get_permissions(self):
            return [] if self.request.user else []

    class Callback:
        actions = {'get': 'list'}

    assert karte.permissions_for(NeedsRequest, Callback, 'GET') == 'abhängig von der Aktion, siehe Code'
