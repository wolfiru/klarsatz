"""Tests für die Übersetzung nach Python.

Der wichtigste Test steht ganz unten: Für Programme ohne Eingabe, Zufall und Zeichnen
muss das erzeugte Python **dieselbe Ausgabe** liefern wie Klarsatz selbst.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from klarsatz import Interpreter
from klarsatz.nach_python import NichtUebersetzbar, nach_python

WURZEL = Path(__file__).resolve().parent.parent


def py(quelltext):
    return nach_python(quelltext).strip()


class Grundformen(unittest.TestCase):
    def test_zuweisung_und_ausgabe(self):
        self.assertEqual(py('Merke 5 als Zahl.\nZeige Zahl.'), "Zahl = 5\nprint(Zahl)")

    def test_zeige_mit_mehreren_teilen(self):
        self.assertIn("sep=''", py('Zeige "a" und 1.'))

    def test_schleife_zaehlt_ab_eins_bis_einschliesslich(self):
        self.assertIn("range(1, 10 + 1)", py("Zähle von 1 bis 10 mit i:\n    Zeige i.\nEnde."))

    def test_rueckwaerts(self):
        self.assertIn("range(10, 1 - 1, -1)", py("Zähle von 10 bis 1 rückwärts mit i:\n    Zeige i.\nEnde."))

    def test_bedingung_wird_if_elif_else(self):
        quelle = ("Merke 5 als n.\nWenn n größer als 3 ist:\n    Zeige 1.\n"
                  "Sonst wenn n gleich 3 ist:\n    Zeige 2.\nSonst:\n    Zeige 3.\nEnde.")
        erzeugt = py(quelle)
        self.assertIn("if (n > 3):", erzeugt)
        self.assertIn("elif (n == 3):", erzeugt)
        self.assertIn("else:", erzeugt)

    def test_teilbar_wird_modulo(self):
        self.assertIn("% 3 == 0", py("Merke 9 als n.\nWenn n durch 3 teilbar ist, zeige n."))

    def test_listen_zaehlen_ab_eins(self):
        """Klarsatz zählt ab 1, Python ab 0 — die Übersetzung rechnet um."""
        self.assertIn("[2 - 1]", py('Erstelle eine Liste namens L mit 1 und 2.\nZeige Element 2 von L.'))

    def test_aufgabe_wird_def(self):
        erzeugt = py("Definiere Aufgabe Summe von a und b:\n    Gib a plus b zurück.\nEnde.")
        self.assertIn("def Summe(a, b):", erzeugt)
        self.assertIn("return (a + b)", erzeugt)

    def test_ding_wird_dataclass(self):
        erzeugt = py('Ein Hund hat einen Namen und ein Alter.\n'
                     'Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Waldi.')
        self.assertIn("@dataclass", erzeugt)
        self.assertIn("class Hund:", erzeugt)
        self.assertIn("Waldi = Hund(Namen='Rocco', Alter=5)", erzeugt)

    def test_zeichnen_wird_turtle(self):
        erzeugt = py("Gehe 100 Schritte vor.\nDrehe dich um 90 Grad nach rechts.")
        self.assertIn("import turtle", erzeugt)
        self.assertIn("stift.forward(100)", erzeugt)
        self.assertIn("stift.right(90)", erzeugt)

    def test_grossschreibung_bleibt_einheitlich(self):
        """Klarsatz unterscheidet Groß/klein nicht, Python schon."""
        erzeugt = py("merke 9 als DRITTE.\nZeige die dritte.")
        self.assertEqual(erzeugt, "DRITTE = 9\nprint(DRITTE)")

    def test_hinweise_stehen_als_kommentar_im_kopf(self):
        erzeugt = py("Merke 7 als a.\nZeige a geteilt durch 2.")
        self.assertIn("# Hinweise zur Übersetzung:", erzeugt)
        self.assertIn("ganze Zahl", erzeugt)


class AlleProgramme(unittest.TestCase):
    def test_jedes_programm_ergibt_gueltiges_python(self):
        dateien = sorted(list((WURZEL / "beispiele").glob("*.klar")) + list((WURZEL / "programme").glob("*.klar")))
        self.assertGreaterEqual(len(dateien), 20)
        for datei in dateien:
            with self.subTest(programm=datei.name):
                erzeugt = nach_python(datei.read_text(encoding="utf-8"))
                compile(erzeugt, datei.name, "exec")      # wirft SyntaxError, wenn etwas nicht stimmt


class GleicheAusgabe(unittest.TestCase):
    """Der eigentliche Beweis: Python muss dasselbe ausgeben wie Klarsatz."""

    GLEICH = ["beispiele/hallo.klar", "beispiele/fizzbuzz.klar",
              "beispiele/aufgaben.klar", "beispiele/schreibweise.klar"]

    def test_ausgabe_stimmt_ueberein(self):
        for name in self.GLEICH:
            with self.subTest(programm=name):
                quelle = (WURZEL / name).read_text(encoding="utf-8")
                aus = []
                Interpreter(ausgabe=aus.append, eingabe=lambda _p="": "Wolfgang",
                            max_schritte=200_000).lauf(quelle)

                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
                    f.write(nach_python(quelle))
                    pfad = f.name
                fertig = subprocess.run([sys.executable, pfad], capture_output=True, text=True,
                                        input="Wolfgang\n", timeout=60)
                self.assertEqual(fertig.returncode, 0, fertig.stderr[-400:])
                self.assertEqual("\n".join(str(z) for z in aus), fertig.stdout.rstrip("\n"))


class Grenzen(unittest.TestCase):
    def test_unbekannter_satz_meldet_sich_deutlich(self):
        from klarsatz.nach_python import NachPython
        uebersetzer = NachPython()
        with self.assertRaisesRegex(NichtUebersetzbar, "noch nicht nach Python"):
            uebersetzer._satz(("gibtesnicht", 1))


if __name__ == "__main__":
    unittest.main()
