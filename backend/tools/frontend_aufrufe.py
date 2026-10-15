"""Liest aus dem Frontend alle Anfragen an das Backend aus (Methode und Pfad).

Aufruf im Ordner backend/:

    .venv/bin/python tools/frontend_aufrufe.py

Das Frontend setzt Pfade oft aus Bausteinen zusammen, z. B.
`${BASE_URL}/${SERVICE}-read/${id}/` mit SERVICE = "event/event". Eine
einfache Textsuche nach "event-read" findet das nicht. Dieses Werkzeug löst
die Bausteine auf: Konstanten derselben Datei werden eingesetzt, alles
andere (Kennungen, Variablen) wird zum Platzhalter {x}.

Genutzt von tests/test_frontend_abgleich.py, der prüft, ob es jede dieser
Adressen im Backend gibt.
"""
import dataclasses
import pathlib
import re

FRONTEND_SRC = pathlib.Path(__file__).resolve().parents[2] / 'frontend' / 'src'
PLACEHOLDER = '{x}'

CALL = re.compile(r'axios\.(get|post|put|patch|delete)\(\s*', re.S)
# const NAME = "…" | '…' | `…`  (auch let/var, auch ohne Semikolon)
CONST = re.compile(r'(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(`[^`]*`|"[^"\n]*"|\'[^\'\n]*\')')
INTERPOLATION = re.compile(r'\$\{([^}]*)\}')


@dataclasses.dataclass(frozen=True)
class Call:
    """Eine Anfrage des Frontends: Datei, Zeile, HTTP-Methode und aufgelöster Pfad."""

    file: str
    line: int
    method: str
    path: str | None  # None, wenn der Pfad nicht aufgelöst werden konnte
    raw: str


def first_argument(text: str, start: int) -> str:
    """Gibt das erste Argument eines Aufrufs ab start zurück (bis zum Komma oder zur Klammer auf Ebene 0)."""
    depth, i, quote = 0, start, None
    while i < len(text):
        char = text[i]
        if quote:
            if char == '\\':
                i += 2
                continue
            if char == quote:
                quote = None
            elif quote == '`' and text.startswith('${', i):
                end = text.index('}', i)
                i = end + 1
                continue
        elif char in '\'"`':
            quote = char
        elif char in '([{':
            depth += 1
        elif char in ')]}':
            if depth == 0:
                break
            depth -= 1
        elif char == ',' and depth == 0:
            break
        i += 1
    return text[start:i].strip()


def resolve(expression: str, constants: dict[str, str], seen: frozenset = frozenset()) -> str | None:
    """Wertet einen Pfad-Ausdruck aus Text, Konstanten und '+' aus. Unbekanntes wird zum Platzhalter."""
    parts = [part.strip() for part in split_plus(expression)]
    result = ''
    for part in parts:
        if part[:1] in '\'"`' and part[-1:] == part[:1]:
            result += INTERPOLATION.sub(lambda m: interpolate(m.group(1), constants, seen), part[1:-1])
        elif re.fullmatch(r'\w+', part) and part in constants and part not in seen:
            inner = resolve(constants[part], constants, seen | {part})
            if inner is None:
                return None
            result += inner
        elif re.fullmatch(r'[\w.?\[\]()]+', part):
            result += PLACEHOLDER
        else:
            return None
    return result


def interpolate(name: str, constants: dict[str, str], seen: frozenset) -> str:
    """Ersetzt ${…} durch den Wert einer Konstante, BASE_URL durch nichts, alles andere durch {x}."""
    name = name.strip()
    if name in ('BASE_URL', 'import.meta.env.VITE_APP_API'):
        return ''
    if name in constants and name not in seen:
        value = resolve(constants[name], constants, seen | {name})
        return value if value is not None else PLACEHOLDER
    return PLACEHOLDER


def split_plus(expression: str) -> list[str]:
    """Teilt einen Ausdruck an '+' außerhalb von Zeichenketten."""
    parts, current, quote, i = [], '', None, 0
    while i < len(expression):
        char = expression[i]
        if quote:
            current += char
            if char == quote:
                quote = None
        elif char in '\'"`':
            quote = char
            current += char
        elif char == '+':
            parts.append(current)
            current = ''
        else:
            current += char
        i += 1
    parts.append(current)
    return parts


def normalize(path: str) -> str:
    """Entfernt Abfrageparameter und doppelte Schrägstriche, sorgt für führenden Schrägstrich."""
    path = path.split('?')[0]
    path = re.sub(r'/{2,}', '/', path)
    return path if path.startswith('/') else '/' + path


def strip_comments(text: str) -> str:
    """Ersetzt Kommentare durch Leerzeichen, Zeilenumbrüche bleiben (für die Zeilennummern).

    Auskommentierter Code ist kein Aufruf. Entfernt werden /* … */ und ganze
    Zeilen, die mit // beginnen. Ein // mitten in einer Zeile bleibt, weil es
    auch in Adressen wie "https://…" vorkommt.
    """
    text = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text, flags=re.S)
    return re.sub(r'(?m)^[ \t]*//.*$', '', text)


def calls_in_file(path: pathlib.Path) -> list[Call]:
    """Alle axios-Aufrufe einer Datei. Konstanten werden bis zur Stelle des Aufrufs berücksichtigt."""
    text = strip_comments(path.read_text(encoding='utf-8'))
    definitions = [(m.start(), m.group(1), m.group(2)) for m in CONST.finditer(text)]
    result = []
    for match in CALL.finditer(text):
        constants = {name: value for pos, name, value in definitions if pos < match.start()}
        raw = first_argument(text, match.end())
        resolved = resolve(raw, constants)
        result.append(Call(
            file=str(path.relative_to(FRONTEND_SRC.parent)),
            line=text.count('\n', 0, match.start()) + 1,
            method=match.group(1).upper(),
            path=normalize(resolved) if resolved is not None else None,
            raw=' '.join(raw.split()),
        ))
    return result


def all_calls() -> list[Call]:
    """Alle axios-Aufrufe im Frontend (TypeScript- und Vue-Dateien)."""
    files = sorted(p for p in FRONTEND_SRC.rglob('*') if p.suffix in ('.ts', '.vue'))
    return [call for file in files for call in calls_in_file(file)]


if __name__ == '__main__':
    for call in all_calls():
        print(f'{call.method:6} {call.path or "?? " + call.raw}  ({call.file}:{call.line})')
