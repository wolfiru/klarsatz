"""Kommandozeile: Programme ausführen, prüfen, formatieren – oder in der Konsole ausprobieren."""
import argparse
import os
import random
import sys
import time
from dataclasses import replace

from . import __version__
from .dateisystem import KeinDateisystem, OrdnerDateisystem
from .fehler import KlarsatzFehler, formatiere_fehler
from .grenzen import Grenzen
from .interpreter import Interpreter


def baue_parser():
    ap = argparse.ArgumentParser(
        prog="klarsatz", description="Klarsatz – eine Programmiersprache, die wie Deutsch klingt.",
        epilog="Ohne Datei startet die interaktive Konsole.")
    ap.add_argument("datei", nargs="?", help="Programm (.klar)")
    ap.add_argument("--version", action="version", version=f"Klarsatz {__version__}")

    was = ap.add_argument_group("Was tun?")
    was.add_argument("--pruefe", action="store_true",
                     help="Programm prüfen, ohne es auszuführen (Tippfehler, Endlosschleifen, unerreichbarer Code …)")
    was.add_argument("--streng", action="store_true",
                     help="mit --pruefe: auch Hinweise und Warnungen führen zum Fehlerstatus 1")
    was.add_argument("--formatiere", action="store_true", help="Programm sauber einrücken und ausgeben")
    was.add_argument("--ersetzen", action="store_true", help="mit --formatiere: Datei direkt überschreiben")
    was.add_argument("--nach-python", action="store_true", dest="nach_python",
                     help="das Programm in lesbares Python übersetzen und ausgeben")
    was.add_argument("--tokens", action="store_true", help="die vom Lexer gelesenen Wörter anzeigen")
    was.add_argument("--ast", action="store_true", help="den Syntaxbaum anzeigen")

    lauf = ap.add_argument_group("Ausführen")
    lauf.add_argument("--seed", type=int, default=None, help="Startwert für Zufallszahlen (reproduzierbar)")
    lauf.add_argument("--limit", type=int, default=None, metavar="SCHRITTE",
                      help="Abbruch nach so vielen Schritten (Schutz vor Endlosschleifen)")
    lauf.add_argument("--zeit", type=float, default=None, metavar="SEKUNDEN", help="Abbruch nach so vielen Sekunden")
    lauf.add_argument("--bild", metavar="DATEI.SVG",
                      help="die Zeichnung des Programms als SVG-Bild speichern")
    lauf.add_argument("--streng-grenzen", action="store_true", dest="streng_grenzen",
                      help="knappe Grenzen für Zeit, Speicher und Größe (für fremde Programme)")

    dat = ap.add_argument_group("Dateien (Standard: nur im aktuellen Ordner und darunter)")
    g = dat.add_mutually_exclusive_group()
    g.add_argument("--ohne-dateien", action="store_true", help="Lesen/Schreiben von Dateien verbieten")
    g.add_argument("--dateien-ordner", metavar="ORDNER", help="Dateien nur in diesem Ordner erlauben")
    g.add_argument("--dateien-ueberall", action="store_true",
                   help="Dateien überall erlauben (Vorsicht: nur für eigene, vertrauenswürdige Programme!)")

    ap.add_argument("--debug", action="store_true", help="bei internen Fehlern den Python-Traceback zeigen")
    return ap


def baue_interpreter(args, **kw):
    grenzen = Grenzen.streng() if args.streng_grenzen else Grenzen()
    if args.limit is not None:
        grenzen = replace(grenzen, schritte=args.limit)
    if args.zeit is not None:
        grenzen = replace(grenzen, sekunden=args.zeit)
    if args.ohne_dateien:
        fs = KeinDateisystem()
    elif args.dateien_ueberall:
        fs = OrdnerDateisystem(None)
    else:
        fs = OrdnerDateisystem(args.dateien_ordner or os.getcwd())
    zufall = random.Random(args.seed) if args.seed is not None else None
    return Interpreter(grenzen=grenzen, dateisystem=fs, zufall=zufall, **kw)


def _lies_datei(pfad):
    try:
        with open(pfad, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(f"Die Datei '{pfad}' lässt sich nicht öffnen: {e.strerror}", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"Die Datei '{pfad}' ist keine Textdatei (UTF-8).", file=sys.stderr)
    return None


def main(argv=None):
    args = baue_parser().parse_args(argv)

    if args.datei is None:
        from .repl import starte_konsole
        return starte_konsole(baue_interpreter(args))

    quelle = _lies_datei(args.datei)
    if quelle is None:
        return 2
    try:
        return _bearbeite(args, quelle)
    except BrokenPipeError:
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        return 0
    except KeyboardInterrupt:
        print("\nAbgebrochen.", file=sys.stderr)
        return 130
    except KlarsatzFehler as e:
        print(formatiere_fehler(e, quelle), file=sys.stderr)
        return 1
    except Exception as e:                       # ein Fehler im Interpreter selbst, nicht im Programm
        if args.debug:
            raise
        print(f"Interner Fehler im Interpreter ({type(e).__name__}: {e}).\n"
              "Das ist ein Fehler in Klarsatz, nicht in deinem Programm. Mit --debug siehst du Details.",
              file=sys.stderr)
        return 70


def _bearbeite(args, quelle):
    if args.tokens:
        from .lexer import lexer
        for t in lexer(quelle):
            if t.art != "EOF":
                print(f"Zeile {t.zeile:>3}, Spalte {t.spalte + 1:>3}  {t.art:<6} {t.wert!r}")
        return 0
    if args.ast:
        from pprint import pprint
        pprint(baue_interpreter(args).parse(quelle), width=110, sort_dicts=False)
        return 0
    if args.formatiere:
        from .formatierer import formatiere
        text = formatiere(quelle)
        if args.ersetzen:
            if text != quelle:
                with open(args.datei, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"{args.datei}: neu formatiert.")
            else:
                print(f"{args.datei}: war schon sauber formatiert.")
        else:
            sys.stdout.write(text)
        return 0
    if args.nach_python:
        from .nach_python import nach_python
        print(nach_python(quelle), end="")
        return 0
    if args.pruefe:
        from .pruefer import pruefe, formatiere_befunde
        befunde = pruefe(quelle)
        print(formatiere_befunde(befunde, quelle, args.datei))
        schlimm = [b for b in befunde if b.schwere == "Fehler" or args.streng]
        return 1 if schlimm else 0
    interpreter = baue_interpreter(args)

    # Ein Programm kann darum bitten, im Takt neu zu laufen ("Wiederhole dieses Programm
    # jede Sekunde."). Dann läuft es hier wieder und wieder, bis Strg+C kommt.
    erster_lauf = True
    while True:
        if not erster_lauf and sys.stdout.isatty():
            print("\033[2J\033[H", end="")          # Bildschirm löschen, Cursor nach oben
        interpreter.lauf(quelle)

        if args.bild:
            from .zeichnung import als_svg
            if not interpreter.zeichnung:
                print("Das Programm hat nichts gezeichnet – es ist kein Bild entstanden.", file=sys.stderr)
                return 1
            try:
                with open(args.bild, "w", encoding="utf-8") as f:
                    f.write(als_svg(interpreter.zeichnung))
            except OSError as e:
                print(f"Das Bild '{args.bild}' lässt sich nicht schreiben: {e.strerror}", file=sys.stderr)
                return 2
            print(f"{len(interpreter.zeichnung)} Striche als Bild gespeichert: {args.bild}", file=sys.stderr)

        takt = interpreter.wiederholung
        if not takt:
            return 0
        sys.stdout.flush()                           # bei getakteten Läufen sofort sichtbar
        if erster_lauf:
            print(f"(Läuft alle {takt:g} s neu – beenden mit Strg+C.)", file=sys.stderr)
        erster_lauf = False
        time.sleep(takt)


if __name__ == "__main__":
    sys.exit(main())
