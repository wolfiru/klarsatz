"""Lexer: zerlegt den Quelltext in Wörter, Zahlen, Texte und Satzzeichen."""
import re

from .fehler import SyntaxFehler

# ════════════════════════════════════════════════════════════════════
#  Normalisierung & Lexer
# ════════════════════════════════════════════════════════════════════
_UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def norm(s: str) -> str:
    """Schlüsselwörter/Namen vergleichen: klein, ä->ae, ö->oe, ü->ue, ß->ss."""
    return s.casefold().translate(_UMLAUTE)


ARTIKEL = {"der", "die", "das", "den", "dem", "des",
           "ein", "eine", "einen", "einem", "einer", "eines"}
# Füllwörter, die einen Befehl natürlicher klingen lassen, ohne etwas zu bedeuten:
# "Merke dir 5 als Zahl.", "Zeige mir die Summe.", "Drehe dich um 90 Grad nach rechts."
FUELLWOERTER = {"dir", "dich", "mir", "mich", "uns", "sich", "bitte"}
UEBERLESEN = ARTIKEL | FUELLWOERTER
KONTRAKTION = {"zur": "zu", "zum": "zu", "vom": "von", "im": "in", "ins": "in"}

_TOKEN = re.compile(r'''
    (?P<leer>[ \t\r]+)
  | (?P<nl>\n)
  | (?P<zahl>\d+(?:\.\d+)?)
  | (?P<text>"[^"\n]*"|„[^“”"\n]*[“”"])
  | (?P<wort>[^\W\d_]\w*)
  | (?P<minus>-(?=\d))
  | (?P<sym>[.,:()])
''', re.VERBOSE)


class Token:
    __slots__ = ("art", "wert", "norm", "zeile", "spalte", "laenge")

    def __init__(self, art, wert, zeile, spalte=0, laenge=None):
        self.art = art          # WORT, ZAHL, TEXT, EOF oder das Symbol selbst ('.', ',', ':', '(', ')', '-')
        self.wert = wert
        self.zeile = zeile
        self.spalte = spalte    # 0-basierte Spalte in der Quelltextzeile
        self.laenge = laenge if laenge is not None else len(str(wert))
        self.norm = norm(wert) if art == "WORT" else None


def lexer(quelltext: str):
    tokens = []
    zeile, pos, n = 1, 0, len(quelltext)
    zeilenanfang = 0
    while pos < n:
        m = _TOKEN.match(quelltext, pos)
        if not m:
            c = quelltext[pos]
            spalte = pos - zeilenanfang
            if c in '"„':
                raise SyntaxFehler("Ein Text wurde nicht mit Anführungszeichen geschlossen.", zeile, spalte, 1)
            hinweis = " Rechnen geht mit Wörtern: plus, minus, mal, geteilt durch." if c in "+-*/^%=<>" else ""
            raise SyntaxFehler(f"Das Zeichen '{c}' kenne ich nicht.{hinweis}", zeile, spalte, 1)
        art, wert = m.lastgroup, m.group()
        spalte = m.start() - zeilenanfang
        pos = m.end()
        if art == "leer":
            continue
        if art == "nl":
            zeile += 1
            zeilenanfang = pos
            continue
        if art == "zahl":
            tokens.append(Token("ZAHL", float(wert) if "." in wert else int(wert), zeile, spalte, len(wert)))
        elif art == "text":
            inhalt = wert[1:-1].replace("\\n", "\n").replace("\\t", "\t")
            tokens.append(Token("TEXT", inhalt, zeile, spalte, len(wert)))
        elif art == "wort":
            nw = norm(wert)
            if nw == "anmerkung" and quelltext[pos:].lstrip(" \t").startswith(":"):
                ende = quelltext.find("\n", pos)      # Kommentar bis Zeilenende
                pos = n if ende == -1 else ende
                continue
            if nw in UEBERLESEN:
                continue                              # Artikel und Füllwörter überliest der Lexer
            t = Token("WORT", wert, zeile, spalte, len(wert))
            t.norm = KONTRAKTION.get(t.norm, t.norm)
            tokens.append(t)
        else:                                          # Satzzeichen und Minuszeichen vor Zahlen
            tokens.append(Token(wert, wert, zeile, spalte, 1))
    tokens += [Token("EOF", "", zeile, pos - zeilenanfang, 0)] * 3
    return tokens
