"""Misst die Kennzahlen für docs/qualitaet.md. Aufruf im Ordner backend/:

    .venv/bin/python tools/qualitaet_messen.py

Zählweise: Anwendungscode = alle .py-Dateien ohne .venv, migrations/ und tests/.
Beschrieben = Funktion, Methode oder Klasse mit Docstring; Namen mit doppeltem
Unterstrich (z. B. __str__) zählen nicht mit.
"""
import ast
import collections
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


def app_files():
    for path in sorted(ROOT.rglob('*.py')):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(('.venv/', 'tests/')) or '/migrations/' in rel:
            continue
        yield path


def count_noqa(files):
    """Zählt die noqa-Markierungen je Regel, getrennt nach Altlast und gewollt.

    Gewollt ist eine Markierung, hinter deren Regelnummer nach "--" eine
    Begründung steht (Beispiele in den apps.py-Dateien). Alle anderen sind
    Altlasten. Markierungen ohne Regelnummer verbietet ruff (PGH004), sie
    kommen hier deshalb nicht vor.
    """
    legacy, intended = collections.Counter(), collections.Counter()
    for path in files:
        for match in re.finditer(r'# noqa: ([A-Z0-9, ]+)(\s*--)?', path.read_text()):
            target = intended if match.group(2) else legacy
            for code in match.group(1).replace(' ', '').split(','):
                target[code] += 1
    return legacy, intended


def main():
    files = list(app_files())
    lines = sum(len(p.read_text().splitlines()) for p in files)
    total = documented = 0
    for path in files:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith('__'):
                total += 1
                documented += bool(ast.get_docstring(node))
    legacy, intended = count_noqa(files)
    print(f'Anwendungscode: {len(files)} Dateien, {lines} Zeilen')
    print(f'Beschrieben: {documented} von {total} ({100 * documented / total:.1f} %)')
    print(f'noqa-Altlasten: {sum(legacy.values())} {dict(sorted(legacy.items()))}')
    print(f'noqa gewollt (mit Begründung): {sum(intended.values())} {dict(sorted(intended.items()))}')
    tests = subprocess.run(['.venv/bin/pytest', '-q', '-p', 'no:warnings'], cwd=ROOT, capture_output=True, text=True)
    print('Tests:', tests.stdout.strip().splitlines()[-1])


if __name__ == '__main__':
    main()
