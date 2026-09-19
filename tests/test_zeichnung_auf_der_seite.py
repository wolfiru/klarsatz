"""Das Bild auf der Startseite entsteht aus dem Programm, das danebensteht.

Wäre es ein gemaltes Symbol, müsste man es glauben. So kann man es nachrechnen: Das SVG
wird aus `webseite/assets/zeichnung.klar` erzeugt, und genau dieses Programm zeigt die
Seite im Codeblock daneben. Beides darf nicht auseinanderlaufen.
"""
import html
import re
import unittest
from pathlib import Path

from klarsatz import web
from klarsatz.zeichnung import als_svg

WURZEL = Path(__file__).resolve().parent.parent
PROGRAMM = WURZEL / "webseite" / "assets" / "zeichnung.klar"
BILD = WURZEL / "webseite" / "assets" / "zeichnung.svg"
SEITE = WURZEL / "webseite" / "seiten" / "index.html"


class BildUndProgramm(unittest.TestCase):
    def test_das_bild_ist_aktuell(self):
        """Sonst zeigt die Seite ein Bild, das ihr Programm gar nicht mehr malt."""
        ergebnis = web.laufe(PROGRAMM.read_text(encoding="utf-8"), seed=0)
        self.assertEqual(ergebnis.zustand, "fertig", ergebnis.fehler)
        striche = [e for e in ergebnis.verlauf if e[0] == "linie"]
        self.assertEqual(als_svg(striche), BILD.read_text(encoding="utf-8"),
                         "zeichnung.svg passt nicht mehr — python3 tools/baue_zeichnung.py ausführen.")

    def test_die_seite_zeigt_genau_dieses_programm(self):
        seite = SEITE.read_text(encoding="utf-8")
        m = re.search(r'<div class="zk-text">.*?<pre class="klar">(.*?)</pre>', seite, re.S)
        self.assertIsNotNone(m, "Der Codeblock beim Zeichenkurs fehlt.")
        gezeigt = html.unescape(m.group(1)).strip()
        self.assertEqual(gezeigt, PROGRAMM.read_text(encoding="utf-8").strip())

    def test_das_programm_zieht_auch_wirklich_striche(self):
        ergebnis = web.laufe(PROGRAMM.read_text(encoding="utf-8"), seed=0)
        self.assertEqual(len([e for e in ergebnis.verlauf if e[0] == "linie"]), 48)
