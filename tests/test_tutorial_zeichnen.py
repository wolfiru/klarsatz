"""Der Grafikkurs rechnet sich selbst nach.

Ein Zeichenprogramm gibt keinen Text aus — trotzdem lässt sich genau prüfen, was entsteht:
Der Interpreter malt nicht selbst, er *meldet* jeden Strich als
`("linie", x1, y1, x2, y2, Farbe, Breite)`. Daraus ergibt sich alles, was im Kurs behauptet
wird: wie viele Striche, in welchen Farben, und ob die Figur geschlossen ist.

Ein ```zeichnung-Block im Markdown sagt das an:

    striche: 4
    farben: gold
    geschlossen: ja
"""
import unittest
from pathlib import Path

from klarsatz import web
from klarsatz.grenzen import Grenzen
from klarsatz.interpreter import FARBEN
from tests.test_tutorial import lies_bloecke

KURS = Path(__file__).resolve().parent.parent / "docs" / "TUTORIAL-ZEICHNEN.md"
SAAT = 0

# Der Interpreter meldet Farben als Hexwert — zurück zum deutschen Namen.
NAME_ZU_HEX = dict(FARBEN)
SCHREIBWEISE = {"grün": "gruen", "türkis": "tuerkis", "weiß": "weiss"}


def striche(ergebnis):
    return [v for v in ergebnis.verlauf if v[0] == "linie"]


def erwartung(zeilen):
    """'striche: 4' / 'farben: gold, türkis' / 'geschlossen: ja' -> dict"""
    werte = {}
    for zeile in zeilen:
        if ":" not in zeile:
            continue
        schluessel, wert = zeile.split(":", 1)
        werte[schluessel.strip().lower()] = wert.strip()
    return werte


class Grafikkurs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bloecke = lies_bloecke(KURS.read_text(encoding="utf-8"))

    def laufe(self, block):
        return web.laufe(block.quelltext, antworten=block.eingaben, seed=SAAT,
                         grenzen=Grenzen(schritte=500_000, sekunden=10, warte=0, striche=200_000))

    def test_der_kurs_ist_vorhanden(self):
        self.assertTrue(KURS.exists(), "docs/TUTORIAL-ZEICHNEN.md fehlt")
        self.assertGreaterEqual(len(self.bloecke), 12)

    def test_es_gibt_acht_lektionen(self):
        ueberschriften = [z for z in KURS.read_text(encoding="utf-8").split("\n")
                          if z.startswith("## Lektion ")]
        self.assertEqual(len(ueberschriften), 8, f"gefunden: {ueberschriften}")

    def test_jedes_programm_laeuft(self):
        for block in self.bloecke:
            with self.subTest(lektion=block.lektion, zeile=block.zeile):
                ergebnis = self.laufe(block)
                self.assertNotEqual(ergebnis.zustand, "fehler",
                                    f"Zeile {block.zeile} läuft nicht:\n{ergebnis.fehler}")

    def test_jede_angekuendigte_zeichnung_entsteht_auch(self):
        geprueft = 0
        for block in self.bloecke:
            if not block.zeichnung:
                continue
            soll = erwartung(block.zeichnung)
            with self.subTest(lektion=block.lektion, zeile=block.zeile):
                gemalt = striche(self.laufe(block))

                if "striche" in soll:
                    self.assertEqual(len(gemalt), int(soll["striche"]),
                                     f"Zeile {block.zeile}: andere Anzahl Striche als angekündigt.")

                if "farben" in soll:
                    erwartet = {SCHREIBWEISE.get(f.strip(), f.strip()).lower()
                                for f in soll["farben"].split(",")}
                    unbekannt = erwartet - set(NAME_ZU_HEX)
                    self.assertEqual(unbekannt, set(), f"Diese Farben gibt es nicht: {unbekannt}")
                    benutzt = {s[5] for s in gemalt}
                    self.assertEqual(benutzt, {NAME_ZU_HEX[f] for f in erwartet},
                                     f"Zeile {block.zeile}: andere Farben als angekündigt.")

                if "geschlossen" in soll:
                    self.assertTrue(gemalt, "ohne Striche ist nichts geschlossen")
                    anfang = (round(gemalt[0][1], 6), round(gemalt[0][2], 6))
                    ende = (round(gemalt[-1][3], 6), round(gemalt[-1][4], 6))
                    ist_zu = anfang == ende
                    self.assertEqual(ist_zu, soll["geschlossen"].lower() in ("ja", "wahr"),
                                     f"Zeile {block.zeile}: Anfang {anfang}, Ende {ende}")
                geprueft += 1
        self.assertGreater(geprueft, 5, "Kaum Zeichnungen angekündigt — dann prüft der Kurs sich nicht.")

    def test_die_pruefung_wuerde_eine_falsche_angabe_auch_merken(self):
        """Gegenprobe: Ein Kurs, in dem nie etwas auffällt, prüft vielleicht gar nichts."""
        from tests.test_tutorial import Block
        block = Block(zeile=0, lektion="Gegenprobe",
                      quelltext="Gehe 10 Schritte vor.\n", zeichnung=["striche: 99"])
        gemalt = striche(self.laufe(block))
        self.assertNotEqual(len(gemalt), 99)


if __name__ == "__main__":
    unittest.main()
