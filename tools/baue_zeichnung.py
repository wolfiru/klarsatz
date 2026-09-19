#!/usr/bin/env python3
"""Malt das Bild für die Startseite — mit Klarsatz selbst.

    python3 tools/baue_zeichnung.py

Aus `webseite/assets/zeichnung.klar` wird `webseite/assets/zeichnung.svg`. Das Bild neben
dem Hinweis auf den Zeichenkurs ist damit kein gezeichnetes Symbol, sondern das Ergebnis
des Programms, das direkt daneben steht. Ändert sich am Zeichnen etwas, ändert sich das
Bild — und die CI merkt, wenn jemand vergisst, es neu zu bauen.
"""
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from klarsatz import web                                  # noqa: E402
from klarsatz.zeichnung import als_svg                          # noqa: E402

QUELLE = WURZEL / "webseite" / "assets" / "zeichnung.klar"
ZIEL = WURZEL / "webseite" / "assets" / "zeichnung.svg"


def main() -> int:
    ergebnis = web.laufe(QUELLE.read_text(encoding="utf-8"), seed=0)
    if ergebnis.zustand == "fehler":
        print(ergebnis.fehler, file=sys.stderr)
        return 1
    striche = [e for e in ergebnis.verlauf if e[0] == "linie"]
    ZIEL.write_text(als_svg(striche), encoding="utf-8")
    print(f"{ZIEL.name}: {len(striche)} Striche, {ZIEL.stat().st_size} Bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
