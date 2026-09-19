"""Interaktive Konsole: Sätze eintippen und sofort sehen, was passiert."""
import sys

from .fehler import KlarsatzFehler, LimitFehler, SyntaxFehler, formatiere_fehler
from .lexer import lexer
from .parser import STARTER
from .werte import als_text

BANNER = ("Klarsatz {version} – die interaktive Konsole\n"
          "Tippe einen Satz mit Punkt am Ende (z. B.  Zeige \"Hallo\".)  oder einen Ausdruck (z. B.  3 plus 4).\n"
          "Mehrzeilige Blöcke (Wenn … : … Ende.) einfach zeilenweise eintippen.  :hilfe zeigt alle Befehle.")

HILFE = """Befehle der Konsole (alle beginnen mit einem Doppelpunkt):
  :hilfe            diese Übersicht
  :variablen        alle Variablen mit ihren Werten
  :aufgaben         alle Aufgaben und Dinge
  :laden DATEI      ein Programm laden und ausführen (Variablen und Aufgaben bleiben erhalten)
  :neu              alles vergessen und von vorn beginnen
  :ende             beenden (oder Strg+D)
Eine leere Zeile mitten in einem unfertigen Satz bricht die Eingabe ab und zeigt, was fehlt."""

_UNFERTIG = ("das Ende des Programms", "nie mit 'Ende.' geschlossen")


def _beginnt_wie_satz(text):
    try:
        toks = [t for t in lexer(text) if t.art != "EOF"]
    except SyntaxFehler:
        return True
    if not toks:
        return True
    if toks[0].art == "WORT" and toks[0].norm in STARTER:
        return True
    return len(toks) > 1 and toks[1].art == "WORT" and toks[1].norm == "hat"


def _zeige_fehler(e, text, ausgabe):
    ausgabe(formatiere_fehler(e, text))


def starte_konsole(interpreter, eingabe=None, ausgabe=None, banner=True):
    """Liest Zeilen, bis Strg+D oder ':ende'. `eingabe(prompt)` und `ausgabe(text)` sind austauschbar."""
    from . import __version__
    eingabe = eingabe or input
    ausgabe = ausgabe or print
    if eingabe is input:
        try:
            import readline  # noqa: F401  (Pfeiltasten und Verlauf, wo verfügbar)
        except ImportError:
            pass
    if banner:
        ausgabe(BANNER.format(version=__version__))

    puffer = []
    while True:
        try:
            zeile = eingabe("      ... " if puffer else "klarsatz> ")
        except EOFError:
            ausgabe("")
            ausgabe("Tschüss!")
            return 0
        except KeyboardInterrupt:
            puffer.clear()
            ausgabe("\n(Eingabe verworfen)")
            continue

        if not puffer and zeile.strip().startswith(":"):
            if _befehl(zeile.strip(), interpreter, ausgabe) == "ende":
                return 0
            continue
        if not puffer and not zeile.strip():
            continue

        erzwungen = bool(puffer) and not zeile.strip()
        puffer.append(zeile)
        text = "\n".join(puffer)

        if not _beginnt_wie_satz(text):
            try:
                ergebnis = interpreter.werte_aus(text)
            except SyntaxFehler:
                pass                                            # kein Ausdruck – dann war es wohl ein Satz (unten)
            except KlarsatzFehler as e:                         # ein Ausdruck, der beim Auswerten scheitert
                puffer.clear()
                _zeige_fehler(e, text, ausgabe)
                continue
            else:
                ausgabe("= " + als_text(ergebnis))
                puffer.clear()
                continue

        try:
            programm = interpreter.parse(text)
        except SyntaxFehler as e:
            if not erzwungen and any(m in e.meldung for m in _UNFERTIG):
                continue                                        # Satz oder Block ist noch nicht zu Ende
            puffer.clear()
            _zeige_fehler(e, text, ausgabe)
            continue
        except KlarsatzFehler as e:
            puffer.clear()
            _zeige_fehler(e, text, ausgabe)
            continue
        puffer.clear()
        try:
            interpreter.fuehre_aus(programm)
        except KeyboardInterrupt:
            ausgabe("\nAbgebrochen.")
        except LimitFehler as e:
            _zeige_fehler(e, text, ausgabe)
        except KlarsatzFehler as e:
            _zeige_fehler(e, text, ausgabe)


def _befehl(text, interpreter, ausgabe):
    teile = text.split(None, 1)
    name = teile[0].lower()
    arg = teile[1].strip() if len(teile) > 1 else ""
    if name in (":ende", ":quit", ":exit", ":q"):
        ausgabe("Tschüss!")
        return "ende"
    if name in (":hilfe", ":help", ":?"):
        ausgabe(HILFE)
    elif name == ":variablen":
        b = interpreter.global_bereich
        if not b.werte:
            ausgabe("(noch keine Variablen)")
        for n, w in b.werte.items():
            konst = "  (Konstante)" if n in b.konstanten else ""
            wert = als_text(w)
            ausgabe(f"  {b.anzeige[n]} = {wert if len(wert) <= 70 else wert[:67] + '…'}{konst}")
    elif name == ":aufgaben":
        if not interpreter.aufgaben and not interpreter.strukturen:
            ausgabe("(noch keine Aufgaben oder Dinge)")
        for anz, params, _ in interpreter.aufgaben.values():
            ausgabe(f"  Aufgabe {anz}" + (f" mit {' und '.join(p[1] for p in params)}" if params else ""))
        for anz, felder in interpreter.strukturen.values():
            ausgabe(f"  Ding {anz}: {', '.join(f[1] for f in felder)}")
    elif name == ":neu":
        interpreter.zuruecksetzen()
        ausgabe("Alles vergessen – wir fangen neu an.")
    elif name == ":laden":
        if not arg:
            ausgabe("Welche Datei? Zum Beispiel:  :laden programme/01_taschenrechner.klar")
            return None
        try:
            with open(arg, encoding="utf-8") as f:
                quelle = f.read()
        except (OSError, UnicodeDecodeError) as e:
            ausgabe(f"Die Datei '{arg}' lässt sich nicht laden ({getattr(e, 'strerror', None) or 'keine Textdatei'}).")
            return None
        try:
            interpreter.lauf(quelle)
        except KlarsatzFehler as e:
            _zeige_fehler(e, quelle, ausgabe)
    else:
        ausgabe(f"Den Befehl {name} kenne ich nicht. :hilfe zeigt alle.")
    return None
