#!/usr/bin/env python3
"""Fuzz-Test von Hand: lange Läufe mit Zufallssaat.

    python3 tools/fuzze.py                    # 5000 Beschüsse, zufällige Saat
    python3 tools/fuzze.py --laeufe 200000    # länger
    python3 tools/fuzze.py --saat 4711        # genau diesen Lauf noch einmal
    python3 tools/fuzze.py --wiederhole 123   # genau diesen einen Beschuss zeigen
    python3 tools/fuzze.py --laut             # jeden Beschuss mitschreiben

Ein kurzer, fester Ausschnitt davon läuft bei jedem Testlauf mit (tests/test_fuzz.py).
Hier geht es um die Dauerbeschießung: je länger sie läuft, desto mehr sagt sie aus.

Gefundene Pannen landen als .klar-Dateien in einem Ordner, damit man sie einzeln
ansehen kann.
"""
import argparse
import random
import sys
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from tests import fuzzer  # noqa: E402


def wiederhole(saat):
    """Zeigt einen einzelnen Beschuss: was verdorben wurde und was dabei herauskommt."""
    name, text, rezept, stelle, funktion = fuzzer.baue(saat)
    print(f"Saat {saat}: {name}, verdorben durch {' + '.join(rezept)}, beschossen wird {stelle}()")
    print("─" * 70)
    print(text)
    print("─" * 70)
    try:
        with fuzzer.zeitwache(20.0):
            funktion(text, fuzzer.knappe_grenzen())
        print("Ergebnis: sauber durchgelaufen (kein Fehler)")
    except fuzzer.KlarsatzFehler as e:
        print(f"Ergebnis: {type(e).__name__} — {e.meldung}   (so soll es sein)")
    except BaseException as e:
        print(f"Ergebnis: PANNE {type(e).__name__} — {e}")
        return 1
    return 0


def main():
    p = argparse.ArgumentParser(description="Klarsatz mit verdorbenen Programmen beschießen")
    p.add_argument("--laeufe", type=int, default=5000, help="Anzahl der Beschüsse (Vorgabe 5000)")
    p.add_argument("--saat", type=int, default=None, help="feste Saat statt einer zufälligen")
    p.add_argument("--wiederhole", type=int, default=None, metavar="SAAT",
                   help="einen einzelnen Beschuss zeigen und ausführen")
    p.add_argument("--zeitgrenze", type=float, default=20.0, help="ab wann etwas als Hänger gilt (Sekunden)")
    p.add_argument("--laut", action="store_true", help="jeden Beschuss mitschreiben")
    p.add_argument("--ordner", default="/tmp/klarsatz-fuzz", help="wohin gefundene Pannen gelegt werden")
    a = p.parse_args()

    if a.wiederhole is not None:
        return wiederhole(a.wiederhole)

    saat = a.saat if a.saat is not None else random.randrange(2 ** 32)
    programme = fuzzer.quellen()
    print(f"{a.laeufe} Beschüsse auf {len(programme)} Programme, Saat {saat}")
    print(f"({len(fuzzer.VERDERBER)} Arten zu verderben, {len(fuzzer.STELLEN)} beschossene Stellen)\n")

    def mitschreiben(nr, name, stelle, rezept):
        if a.laut:
            print(f"  {nr:6}  {stelle:12} {name:32} {'+'.join(rezept)}")
        elif nr and nr % 5000 == 0:
            print(f"  … {nr} Beschüsse")

    begonnen = time.time()
    pannen = fuzzer.beschiesse(saat, a.laeufe, programme=programme,
                               zeitgrenze=a.zeitgrenze, bei_lauf=mitschreiben)
    dauer = time.time() - begonnen

    print(f"\n{a.laeufe} Beschüsse in {dauer:.0f} s ({a.laeufe / max(dauer, 0.001):.0f} je Sekunde)")
    if not pannen:
        print("Keine Panne: Alles endete als Klarsatz-Fehler, nichts hing, nichts stürzte ab.")
        return 0

    ordner = Path(a.ordner)
    ordner.mkdir(parents=True, exist_ok=True)
    print(f"\n{len(pannen)} PANNEN:\n")
    for i, panne in enumerate(pannen):
        print(f"  {panne.kurz()}")
        ziel = ordner / f"panne-{i:03}-{panne.stelle}-{panne.saat}.klar"
        ziel.write_text(panne.quelltext, encoding="utf-8")
    print(f"\nQuelltexte liegen in {ordner}")
    print(f"Einzeln ansehen: python3 tools/fuzze.py --wiederhole {pannen[0].saat}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
