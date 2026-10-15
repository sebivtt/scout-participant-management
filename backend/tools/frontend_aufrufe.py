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

Bekannte Grenzen (der Test meldet die ersten beiden, wenn sie auftreten):
- Erkannt werden nur axios.get/post/put/patch/delete. fetch(), axios({...}),
  axios.request und eigene Instanzen über axios.create nicht.
- Konstanten aus anderen Dateien (import) gelten als nicht auflösbar.
- Funktionsgrenzen kennt das Werkzeug nicht: Es nimmt die letzte Definition
  einer Konstante vor dem Aufruf, auch aus einer anderen Funktion.
- Ein //-Kommentar mitten in einer Zeile und HTML-Kommentare in .vue-Dateien
  werden nicht entfernt. Das ergibt höchstens einen Fehlalarm.
"""
import dataclasses
import pathlib
import re

FRONTEND_SRC = pathlib.Path(__file__).resolve().parents[2] / 'frontend' / 'src'
PLACEHOLDER = '{x}'
# Markiert einen Baustein, der sich nicht auflösen lässt; der ganze Pfad gilt dann als unbekannt.
UNRESOLVED = '\x00'

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
    """Wertet einen Pfad-Ausdruck aus Text, Konstanten und '+' aus.

    Unbekannte Variablen werden zum Platzhalter {x}, unbekannte Konstanten in
    Großbuchstaben zur Markierung UNRESOLVED (siehe resolve_path).
    """
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
        elif re.fullmatch(r'[A-Z][A-Z0-9_]*', part):
            # Unbekannte Konstante (z. B. importiert): nicht raten, sonst prüft der
            # Abgleich womöglich still eine falsche Adresse.
            return None
        elif re.fullmatch(r'[\w.?\[\]()]+', part):
            result += PLACEHOLDER
        else:
            return None
    return result


def interpolate(name: str, constants: dict[str, str], seen: frozenset) -> str:
    """Ersetzt ${…} durch den Wert einer Konstante, BASE_URL durch nichts, unbekannte Konstanten durch UNRESOLVED, alles andere durch {x}."""
    name = name.strip()
    if name in ('BASE_URL', 'import.meta.env.VITE_APP_API'):
        return ''
    if name in constants and name not in seen:
        value = resolve(constants[name], constants, seen | {name})
        return value if value is not None else UNRESOLVED
    if re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
        return UNRESOLVED
    return PLACEHOLDER


def resolve_path(expression: str, constants: dict[str, str]) -> str | None:
    """Wie resolve, aber None, sobald irgendein Baustein nicht auflösbar war."""
    resolved = resolve(expression, constants)
    if resolved is None or UNRESOLVED in resolved:
        return None
    return resolved


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


class UnreadableSource(ValueError):
    """Der Quelltext ließ sich nicht sicher lesen, z. B. weil am Ende noch eine Zeichenkette offen ist."""


# Nach diesen Zeichen beginnt mit "/" ein regulärer Ausdruck, sonst ist es eine Division.
REGEX_PRECEDERS = set('(,=:[!&|?{};+-*%<>~^') | {''}


class _Scanner:
    """Liest JavaScript/TypeScript Zeichen für Zeichen und ersetzt Kommentare durch Leerzeichen.

    Unterscheidet Code, Zeichenketten ('…', "…", `…` mit ${…}), reguläre
    Ausdrücke (/…/) und Kommentare (// und /* … */). Jede Leseart hat ihren
    eigenen Schritt. Jeder Schritt gibt die Position zurück, an der es
    weitergeht.
    """

    def __init__(self, text: str):
        self.text, self.out = text, []
        self.stack = [['code', 0]]  # Rahmen: ['code'|'expr', offene Klammern] oder ['template']
        self.last = ''              # letztes Zeichen im Code, entscheidet über "/" als Ausdruck

    def run(self) -> str:
        """Liest den ganzen Text und gibt ihn ohne Kommentare zurück."""
        i = 0
        while i < len(self.text):
            step = self.template_step if self.stack[-1][0] == 'template' else self.code_step
            i = step(i)
        if len(self.stack) != 1:
            raise UnreadableSource('Template-Zeichenkette (`…`) wird nicht geschlossen')
        return ''.join(self.out)

    def emit(self, start: int, end: int) -> int:
        """Übernimmt text[start:end] unverändert."""
        self.out.append(self.text[start:end])
        return end

    def template_step(self, i: int) -> int:
        """Ein Schritt innerhalb von `…`: Escape, Ende oder Beginn von ${…}."""
        text = self.text
        if text[i] == '\\':
            return self.emit(i, i + 2)
        if text[i] == '`':
            self.stack.pop()
            self.last = '`'
        elif text.startswith('${', i):
            self.stack.append(['expr', 0])
            return self.emit(i, i + 2)
        return self.emit(i, i + 1)

    def code_step(self, i: int) -> int:
        """Ein Schritt im Code: Kommentar, Zeichenkette, Ausdruck oder einzelnes Zeichen."""
        text, char = self.text, self.text[i]
        if text.startswith('//', i) or text.startswith('/*', i):
            return self.comment(i)
        if char in '\'"':
            return self.quoted(i)
        if char == '`':
            self.stack.append(['template'])
            return self.emit(i, i + 1)
        if char == '/' and self.last in REGEX_PRECEDERS:
            end = self.regex_end(i)
            if end is not None:
                self.last = '/'
                return self.emit(i, end)
        return self.plain(i)

    def comment(self, i: int) -> int:
        """Ersetzt einen //- oder /* */-Kommentar durch Leerzeichen, Zeilenumbrüche bleiben."""
        if self.text.startswith('//', i):
            end = self.text.find('\n', i)
        else:
            end = self.text.find('*/', i + 2)
            end = end + 2 if end != -1 else -1
        end = len(self.text) if end == -1 else end
        self.out.append(re.sub(r'[^\n]', ' ', self.text[i:end]))
        return end

    def quoted(self, i: int) -> int:
        """Überspringt '…' oder "…". Solche Zeichenketten enden immer in derselben Zeile."""
        text, quote, end = self.text, self.text[i], i + 1
        while end < len(text) and text[end] != quote:
            if text[end] == '\n':
                raise UnreadableSource(f'Zeichenkette ab Zeichen {i} endet nicht in ihrer Zeile')
            end += 2 if text[end] == '\\' else 1
        if end >= len(text):
            raise UnreadableSource(f'Zeichenkette ab Zeichen {i} wird nicht geschlossen')
        self.last = quote
        return self.emit(i, end + 1)

    def regex_end(self, i: int) -> int | None:
        """Ende eines regulären Ausdrucks /…/ ab i, oder None, wenn es doch keiner ist."""
        text, end, in_class = self.text, i + 1, False
        while end < len(text) and (in_class or text[end] != '/'):
            if text[end] == '\n':
                return None
            if text[end] == '\\':
                end += 1
            in_class = {'[': True, ']': False}.get(text[end], in_class)
            end += 1
        return end + 1 if end < len(text) else None

    def plain(self, i: int) -> int:
        """Ein gewöhnliches Zeichen im Code; zählt Klammern, um das Ende von ${…} zu erkennen."""
        frame, char = self.stack[-1], self.text[i]
        if char == '}' and frame[0] == 'expr' and frame[1] == 0:
            self.stack.pop()
        elif char in '{}':
            frame[1] += 1 if char == '{' else -1
        if not char.isspace():
            self.last = char
        return self.emit(i, i + 1)


def strip_comments(text: str) -> str:
    """Ersetzt Kommentare durch Leerzeichen, Zeilenumbrüche bleiben (für die Zeilennummern).

    Auskommentierter Code ist kein Aufruf. Endet der Text mitten in einer
    Zeichenkette, hat sich das Lesen verschluckt: Dann wird UnreadableSource
    geworfen, statt still weiterzumachen und Aufrufe zu übersehen.
    """
    return _Scanner(text).run()


def script_part(path: pathlib.Path, text: str) -> str:
    """Bei .vue-Dateien nur der <script>-Teil; der Rest wird zu Leerzeichen (Zeilennummern bleiben).

    Im Vorlagenteil stehen Texte wie "Gib's ein", deren Apostroph sonst als
    Beginn einer Zeichenkette gelesen würde.
    """
    if path.suffix != '.vue':
        return text
    keep = [False] * len(text)
    for match in re.finditer(r'<script\b[^>]*>(.*?)</script>', text, re.S):
        for index in range(match.start(1), match.end(1)):
            keep[index] = True
    return ''.join(c if keep[i] or c == '\n' else ' ' for i, c in enumerate(text))


def calls_in_file(path: pathlib.Path) -> list[Call]:
    """Alle axios-Aufrufe einer Datei. Konstanten werden bis zur Stelle des Aufrufs berücksichtigt."""
    raw = path.read_text(encoding='utf-8')
    try:
        text = strip_comments(script_part(path, raw))
    except UnreadableSource as error:
        raise UnreadableSource(f'{path}: {error}') from error
    definitions = [(m.start(), m.group(1), m.group(2)) for m in CONST.finditer(text)]
    result = []
    for match in CALL.finditer(text):
        constants = {name: value for pos, name, value in definitions if pos < match.start()}
        raw = first_argument(text, match.end())
        resolved = resolve_path(raw, constants)
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
