"""Maschinerie für den Fuzz-Test: Programme verderben und sehen, was zerbricht.

Die Zusage von Klarsatz lautet: Ein Programm kann den Interpreter nicht aus der Bahn
werfen. Egal wie kaputt der Quelltext ist, es kommt ein `KlarsatzFehler` heraus — nie
ein Python-Traceback, nie ein Hänger. Bisher war das nur mit *gültigen* Programmen
geprüft. Hier werden gültige Programme zufällig zerhackt und alles beschossen, was
Quelltext entgegennimmt.

Benutzt von `tests/test_fuzz.py` (kurz und deterministisch, läuft immer mit) und von
`tools/fuzze.py` (lange Läufe von Hand).
"""
import dataclasses
import random
import re
import signal
import string
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from klarsatz import formatierer, nach_python, pruefer, web
from klarsatz.fehler import KlarsatzFehler
from klarsatz.grenzen import Grenzen

WURZEL = Path(__file__).resolve().parent.parent

# Zeichen, die in der Sprache etwas bedeuten, kommen häufiger vor als beliebige
# Buchstaben: Ein verschobener Punkt oder Doppelpunkt trifft die Satzstruktur, und
# genau dort ist ein Parser verwundbar.
ZEICHEN = list('.:,"()[]' + "\n\t ") * 3 + list(string.ascii_letters + string.digits) + list("äöüßÄÖÜ-+*/<>=%#")

# Verdorbene Programme fragen oft an unerwarteter Stelle. Der Vorrat ist bewusst
# gemischt: Zahlen, Text, leer, Unfug.
ANTWORTEN = ["1", "5", "ja", "nein", "Rocco", "", "0", "-3", "2,5", "abc", "42", "n"]


class Zeitueberschreitung(BaseException):
    """Absichtlich von BaseException abgeleitet, damit kein `except Exception` sie verschluckt."""


@contextmanager
def zeitwache(sekunden):
    """Bricht ab, wenn etwas länger braucht als erlaubt — ein Hänger soll als Befund
    erscheinen und nicht die ganze Testsuite anhalten."""
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def ausloesen(signum, rahmen):
        raise Zeitueberschreitung(f"nach {sekunden} s noch nicht fertig")

    vorher = signal.signal(signal.SIGALRM, ausloesen)
    signal.setitimer(signal.ITIMER_REAL, sekunden)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, vorher)


# ── Die Verderber ───────────────────────────────────────────────────────────────

def _zeichen_loeschen(z, t):
    i = z.randrange(len(t))
    return t[:i] + t[i + 1:]


def _zeichen_einfuegen(z, t):
    i = z.randrange(len(t) + 1)
    return t[:i] + z.choice(ZEICHEN) + t[i:]


def _zeichen_ersetzen(z, t):
    i = z.randrange(len(t))
    return t[:i] + z.choice(ZEICHEN) + t[i + 1:]


def _wort_loeschen(z, t):
    woerter = t.split(" ")
    if len(woerter) < 2:
        return t
    del woerter[z.randrange(len(woerter))]
    return " ".join(woerter)


def _wort_doppeln(z, t):
    woerter = t.split(" ")
    i = z.randrange(len(woerter))
    woerter.insert(i, woerter[i])
    return " ".join(woerter)


def _woerter_vertauschen(z, t):
    woerter = t.split(" ")
    if len(woerter) < 2:
        return t
    i, j = z.randrange(len(woerter)), z.randrange(len(woerter))
    woerter[i], woerter[j] = woerter[j], woerter[i]
    return " ".join(woerter)


def _zeile_loeschen(z, t):
    zeilen = t.split("\n")
    if len(zeilen) < 2:
        return t
    del zeilen[z.randrange(len(zeilen))]
    return "\n".join(zeilen)


def _zeilen_vertauschen(z, t):
    zeilen = t.split("\n")
    if len(zeilen) < 2:
        return t
    i, j = z.randrange(len(zeilen)), z.randrange(len(zeilen))
    zeilen[i], zeilen[j] = zeilen[j], zeilen[i]
    return "\n".join(zeilen)


def _einzug_aendern(z, t):
    """Klarsatz gliedert über Einrückung — das ist eine empfindliche Stelle."""
    zeilen = t.split("\n")
    i = z.randrange(len(zeilen))
    zeilen[i] = " " * z.choice([0, 1, 2, 3, 7, 13, 40]) + zeilen[i].lstrip()
    return "\n".join(zeilen)


def _punkt_entfernen(z, t):
    """Jeder Satz endet mit einem Punkt. Einen davon wegzunehmen trifft die Grammatik im Kern."""
    stellen = [i for i, c in enumerate(t) if c == "."]
    if not stellen:
        return t
    i = z.choice(stellen)
    return t[:i] + t[i + 1:]


def _doppelpunkt_entfernen(z, t):
    stellen = [i for i, c in enumerate(t) if c == ":"]
    if not stellen:
        return t
    i = z.choice(stellen)
    return t[:i] + t[i + 1:]


def _abschneiden(z, t):
    return t[:z.randrange(1, len(t) + 1)]


def _stueck_doppeln(z, t):
    i = z.randrange(len(t))
    j = min(len(t), i + z.randrange(1, 60))
    return t[:j] + t[i:j] + t[j:]


def _zahl_aendern(z, t):
    """Zahlen durch Grenzfälle ersetzen. Bleibt meist gültiger Quelltext und zielt damit
    auf den Interpreter statt auf den Parser: Teilen durch null, negative Anzahlen,
    Wiederholungen jenseits des Erträglichen."""
    stellen = list(re.finditer(r"\b\d+\b", t))
    if not stellen:
        return t
    m = z.choice(stellen)
    ersatz = z.choice(["0", "-1", "1", "999999999", "10000000000000000000000000000000", "2"])
    return t[:m.start()] + ersatz + t[m.end():]


def _text_aendern(z, t):
    """Inhalt eines Texts austauschen — leer, sehr lang, mit Sonderzeichen."""
    stellen = list(re.finditer(r'"[^"\n]*"', t))
    if not stellen:
        return t
    m = z.choice(stellen)
    ersatz = z.choice(['""', '"ä"', '"' + "x" * 500 + '"', '"0"', '"-1"', '"{}[]:.,"', '"  "'])
    return t[:m.start()] + ersatz + t[m.end():]


def _satz_doppeln(z, t):
    """Eine ganze Zeile samt Einrückung verdoppeln — bleibt gültig, ändert aber den Ablauf."""
    zeilen = t.split("\n")
    i = z.randrange(len(zeilen))
    zeilen.insert(i, zeilen[i])
    return "\n".join(zeilen)


VERDERBER = [
    ("zahl_aendern", _zahl_aendern),
    ("text_aendern", _text_aendern),
    ("satz_doppeln", _satz_doppeln),
    ("zeichen_loeschen", _zeichen_loeschen),
    ("zeichen_einfuegen", _zeichen_einfuegen),
    ("zeichen_ersetzen", _zeichen_ersetzen),
    ("wort_loeschen", _wort_loeschen),
    ("wort_doppeln", _wort_doppeln),
    ("woerter_vertauschen", _woerter_vertauschen),
    ("zeile_loeschen", _zeile_loeschen),
    ("zeilen_vertauschen", _zeilen_vertauschen),
    ("einzug_aendern", _einzug_aendern),
    ("punkt_entfernen", _punkt_entfernen),
    ("doppelpunkt_entfernen", _doppelpunkt_entfernen),
    ("abschneiden", _abschneiden),
    ("stueck_doppeln", _stueck_doppeln),
]


def verdirb(zufall, quelltext, anzahl=None):
    """Wendet ein paar Verderber hintereinander an. Gibt den Text und das Rezept zurück."""
    rezept = []
    text = quelltext
    for _ in range(anzahl if anzahl is not None else zufall.randint(1, 4)):
        name, f = zufall.choice(VERDERBER)
        if not text:
            break
        text = f(zufall, text)
        rezept.append(name)
    return text, rezept


# ── Die beschossenen Stellen ────────────────────────────────────────────────────

def _stelle_laufe(text, grenzen):
    web.laufe(text, antworten=ANTWORTEN, grenzen=grenzen)


def _stelle_pruefe(text, grenzen):
    pruefer.pruefe(text)


def _stelle_formatiere(text, grenzen):
    einmal = formatierer.formatiere(text)
    # Wer einmal formatiert hat, soll beim zweiten Mal dasselbe bekommen.
    zweimal = formatierer.formatiere(einmal)
    if zweimal != einmal:
        raise AssertionError("Formatieren ist nicht stabil: der zweite Durchgang ändert noch einmal etwas")


def _stelle_nach_python(text, grenzen):
    nach_python.nach_python(text)


STELLEN = [
    ("laufe", _stelle_laufe),
    ("pruefe", _stelle_pruefe),
    ("formatiere", _stelle_formatiere),
    ("nach_python", _stelle_nach_python),
]


@dataclass
class Panne:
    """Ein Fund: etwas anderes als ein KlarsatzFehler kam heraus."""
    stelle: str
    programm: str
    rezept: list
    saat: int
    ausnahme: str
    meldung: str
    quelltext: str

    def kurz(self):
        return (f"{self.stelle}({self.programm}) nach {'+'.join(self.rezept)} [Saat {self.saat}]: "
                f"{self.ausnahme}: {self.meldung}")


def knappe_grenzen():
    """Eng genug, dass ein Fuzz-Lauf zügig bleibt — `warte=0`, sonst hielte eine
    verdorbene Uhr den Lauf minutenlang auf."""
    return dataclasses.replace(Grenzen.streng(), schritte=200_000, sekunden=2.0, warte=0, striche=5_000)


def quellen(ordner=("programme", "beispiele")):
    """Die gültigen Programme, aus denen die Mutanten gemacht werden."""
    dateien = []
    for name in ordner:
        dateien += sorted((WURZEL / name).glob("*.klar"))
    return [(d.name, d.read_text(encoding="utf-8")) for d in dateien]


def beschiesse(saat, laeufe, programme=None, grenzen=None, zeitgrenze=20.0, bei_lauf=None):
    """Führt `laeufe` Beschüsse aus und gibt alle Pannen zurück.

    Für dieselbe Saat kommt derselbe Lauf heraus — ein Fund ist also wiederholbar.
    """
    programme = programme if programme is not None else quellen()
    grenzen = grenzen or knappe_grenzen()
    vergabe = random.Random(saat)
    pannen = []

    for nr in range(laeufe):
        # Jeder Beschuss bekommt seine eigene Saat. Dadurch lässt sich ein Fund
        # später allein wiederholen, ohne den ganzen Lauf noch einmal zu fahren.
        einzelsaat = vergabe.randrange(2 ** 32)
        name, text, rezept, stelle, funktion = baue(einzelsaat, programme)
        if bei_lauf:
            bei_lauf(nr, name, stelle, rezept)
        try:
            with zeitwache(zeitgrenze):
                funktion(text, grenzen)
        except KlarsatzFehler:
            pass                      # genau so soll es sein
        except Zeitueberschreitung as e:
            pannen.append(Panne(stelle, name, rezept, einzelsaat, "Hänger", str(e), text))
        except BaseException as e:    # alles andere ist ein Fund
            pannen.append(Panne(stelle, name, rezept, einzelsaat, type(e).__name__, str(e)[:300], text))
    return pannen


def baue(einzelsaat, programme=None):
    """Stellt einen einzelnen Beschuss zusammen: Programm, Verderbnis, beschossene Stelle."""
    programme = programme if programme is not None else quellen()
    zufall = random.Random(einzelsaat)
    name, original = zufall.choice(programme)
    text, rezept = verdirb(zufall, original)
    stelle, funktion = zufall.choice(STELLEN)
    return name, text, rezept, stelle, funktion
