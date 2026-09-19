"""Laufzeitwerte, Bereiche und Textdarstellung."""
import math
import re
from decimal import ROUND_HALF_UP, Decimal, localcontext

from .fehler import LaufzeitFehler
from .lexer import norm

# ════════════════════════════════════════════════════════════════════
#  Laufzeit: Werte, Bereiche, Ausgabe
# ════════════════════════════════════════════════════════════════════
def passt(a: str, b: str) -> bool:
    """Feldnamen dürfen leicht gebeugt sein: Name / Namen, Zahl / Zahlen."""
    if a == b:
        return True
    for x, y in ((a, b), (b, a)):
        for s in ("n", "en", "s", "es", "e"):
            if x == y + s:
                return True
    return False


class Objekt:
    def __init__(self, typ, felder, werte):
        self.typ, self.felder, self.werte = typ, felder, werte

    def schluessel(self, fnorm):
        for norm_, _ in self.felder:
            if passt(norm_, fnorm):
                return norm_
        return None

    def anzeige(self, norm_):
        return next(a for n, a in self.felder if n == norm_)


def _ist_zahl(w):
    return isinstance(w, (int, float)) and not isinstance(w, bool)


def typname(w):
    if isinstance(w, bool):
        return "ein Wahrheitswert"
    if _ist_zahl(w):
        return "eine Zahl"
    if isinstance(w, str):
        return "ein Text"
    if isinstance(w, list):
        return "eine Liste"
    if isinstance(w, dict):
        return "eine Tabelle"
    if isinstance(w, Objekt):
        return f"ein {w.typ}"
    return "nichts"


def als_text(w):
    if w is True:
        return "wahr"
    if w is False:
        return "falsch"
    if w is None:
        return "nichts"
    if isinstance(w, int):
        return str(w)
    if isinstance(w, float):
        if w.is_integer() and abs(w) < 1e15:
            return str(int(w))
        return format(w, ".12g").replace(".", ",")
    if isinstance(w, str):
        return w
    if isinstance(w, list):
        return "[" + ", ".join(als_text(x) for x in w) + "]"
    if isinstance(w, dict):
        return "{" + ", ".join(f"{als_text(k)}: {als_text(v)}" for k, v in w.items()) + "}"
    if isinstance(w, Objekt):
        inner = ", ".join(f"{a}: {als_text(w.werte[n])}" for n, a in w.felder)
        return f"{w.typ}({inner})"
    return str(w)


class Bereich:
    def __init__(self, eltern=None):
        self.werte, self.anzeige, self.konstanten, self.eltern = {}, {}, set(), eltern

    def finde(self, n):
        b = self
        while b is not None:
            if n in b.werte:
                return b
            b = b.eltern
        return None

    def bekannte(self):
        d, b = {}, self
        while b is not None:
            for k, a in b.anzeige.items():
                d.setdefault(k, a)
            b = b.eltern
        return d

    def lege_an(self, n, anz, wert, konstant=False):
        if n in self.konstanten:
            raise LaufzeitFehler(f"'{anz}' ist eine Konstante ('für immer') und lässt sich nicht ändern.")
        self.werte[n] = wert
        self.anzeige[n] = anz
        if konstant:
            self.konstanten.add(n)


def _gleich(a, b):
    """Gleichheit ohne Verwechslung von wahr/1 und falsch/0."""
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def _sortierschluessel(w):
    """Texte werden 'deutsch' sortiert: Äpfel steht bei A, nicht hinter Z."""
    return norm(w) if isinstance(w, str) else w


def _auto_zahl(s):
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+[.,]\d+", s):
        return float(s.replace(",", "."))
    return s


def runde_dezimal(w, stellen):
    """Kaufmännisch runden (2,675 -> 2,68), so wie man es in der Schule lernt. Gibt Decimal zurück."""
    if isinstance(w, int):
        ziffern = int(w.bit_length() * 0.30103) + 2
        with localcontext() as ctx:
            ctx.prec = ziffern + stellen + 10
            return Decimal(w).quantize(Decimal(1).scaleb(-stellen), rounding=ROUND_HALF_UP)
    if not math.isfinite(w):
        raise LaufzeitFehler("Diese Zahl lässt sich nicht runden.")
    with localcontext() as ctx:
        ctx.prec = 400
        return Decimal(repr(w)).quantize(Decimal(1).scaleb(-stellen), rounding=ROUND_HALF_UP)
