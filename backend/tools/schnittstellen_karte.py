"""Erzeugt docs/schnittstellen.md: welche Anfrage des Frontends welche Backend-Klasse mit welchen Rechten trifft.

Aufruf im Ordner backend/:

    DJANGO_SETTINGS_MODULE=backend.settings_test .venv/bin/python tools/schnittstellen_karte.py

Die Karte ist die Grundlage für die Abstimmung der Abläufe (docs/fahrplan.md).
tests/test_frontend_abgleich.py prüft, dass sie zum Code passt. Ändert sich
eine Anfrage oder eine Rechteklasse, das Werkzeug erneut ausführen.
"""
import collections
import inspect
import os
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = BACKEND.parent / 'docs' / 'schnittstellen.md'

HEADER = '''# Karte der Schnittstellen

Welche Anfrage des Frontends welche Klasse im Backend trifft und welche Rechteprüfung dort gilt. Erzeugt von `backend/tools/schnittstellen_karte.py`, nicht von Hand bearbeiten. `tests/test_frontend_abgleich.py` prüft, dass die Karte zum Code passt.

`{x}` steht für eine Kennung, z. B. die Nummer einer Veranstaltung. „Rechte“ nennt die Rechteklassen der Backend-Klasse. Prüft eine Klasse weitere Rechte erst beim Speichern, steht das in `backend/tests/test_schreibrechte_inventar.py`. Nicht aufgeführt sind die abgeschalteten Module Essensplanung und Programmideen.
'''


def permission_names(view_cls) -> str:
    """Lesbare Namen der Rechteklassen, kombinierte Prüfungen (A | B) als „A oder B“."""
    from rest_framework.settings import api_settings
    names = []
    for permission in getattr(view_cls, 'permission_classes', api_settings.DEFAULT_PERMISSION_CLASSES):
        names.append(describe_permission(permission))
    return ', '.join(names) or '–'


def describe_permission(permission) -> str:
    """Name einer Rechteklasse; bei einer Verknüpfung A | B beide Seiten."""
    if inspect.isclass(permission):
        return permission.__name__
    op1, op2 = getattr(permission, 'op1_class', None), getattr(permission, 'op2_class', None)
    if op1 is not None and op2 is not None:
        operator = getattr(permission, 'operator_class', None)
        joiner = ' oder ' if operator is not None and operator.__name__ == 'OR' else ' und '
        return describe_permission(op1) + joiner + describe_permission(op2)
    return type(permission).__name__


def build_rows():
    """Zeilen der Karte, gruppiert nach Frontend-Modul: (Methode, Pfad, Backend-Klasse, Rechte, Fundstellen)."""
    from django.urls import Resolver404, resolve

    sys.path.insert(0, str(BACKEND / 'tools'))
    import frontend_aufrufe

    grouped = collections.defaultdict(lambda: collections.defaultdict(list))
    for call in frontend_aufrufe.all_calls():
        if call.file.startswith('src/modules/inspi/') or call.path is None:
            continue
        module = call.file.split('/')[2] if call.file.startswith('src/modules/') else call.file
        grouped[module][(call.method, call.path)].append(f'{call.file}:{call.line}')
    rows = {}
    for module, calls in sorted(grouped.items()):
        rows[module] = []
        for (method, path), places in sorted(calls.items(), key=lambda item: (item[0][1], item[0][0])):
            try:
                match = resolve(path.replace(frontend_aufrufe.PLACEHOLDER, '00000000-0000-0000-0000-000000000001'))
                view_cls = getattr(match.func, 'cls', None) or getattr(match.func, 'view_class', None)
                target = f'`{view_cls.__module__}.{view_cls.__name__}`'
                rights = permission_names(view_cls)
            except Resolver404:
                target, rights = '**fehlt**', '–'
            rows[module].append((method, path, target, rights, places))
    return rows


def render() -> str:
    """Die vollständige Karte als Markdown."""
    lines = [HEADER]
    for module, rows in build_rows().items():
        lines.append(f'\n## {module}\n')
        lines.append('| Methode | Adresse | Backend-Klasse | Rechte | Aufgerufen in |')
        lines.append('| --- | --- | --- | --- | --- |')
        for method, path, target, rights, places in rows:
            lines.append(f'| {method} | `{path}` | {target} | {rights} | {", ".join(f"`{p}`" for p in places)} |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    sys.path.insert(0, str(BACKEND))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_test')
    import django
    django.setup()
    OUTPUT.write_text(render(), encoding='utf-8')
    print(f'geschrieben: {OUTPUT}')
