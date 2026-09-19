"""Zahlen auf der Webseite müssen stimmen.

Angaben wie „zwanzig Beispielprogramme" veralten leise: Es fällt niemandem auf, wenn ein
Programm dazukommt. Hier wird nachgezählt — gegen die Dateien, nicht gegen das Gedächtnis.
"""
import json
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITE = WURZEL / "webseite" / "seiten" / "index.html"
HEIM = Path("/var/www/html/index.html")

WORT = {9: "neun", 20: "zwanzig", 29: "neunundzwanzig"}


def ist_ruthner_at():
    """Liegt unter /var/www/html/index.html wirklich die Startseite von ruthner.at?"""
    try:
        return "klarsatz/" in HEIM.read_text(encoding="utf-8")
    except OSError:
        return False


class Beispielzahlen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programme = len(list((WURZEL / "programme").glob("*.klar")))
        cls.beispiele = len(list((WURZEL / "beispiele").glob("*.klar")))
        cls.spielwiese = len(json.loads((WURZEL / "playground" / "beispiele.json")
                                        .read_text(encoding="utf-8")))
        cls.text = SEITE.read_text(encoding="utf-8")

    def test_die_spielwiese_zaehlt_beide_ordner(self):
        self.assertEqual(self.spielwiese, self.programme + self.beispiele)

    def test_die_startseite_nennt_die_richtigen_zahlen(self):
        self.assertIn(f"{WORT[self.programme]} Beispielprogramme", self.text,
                      f"Erwartet '{WORT[self.programme]} Beispielprogramme' im Downloadbereich.")
        self.assertIn(f"{WORT[self.beispiele]}\nkleine Sprachbeispiele".replace("\n", " "), self.text)
        self.assertIn(f"{self.spielwiese}, die auch in der", self.text)

    def test_die_sofort_demo_nennt_die_zahl_der_spielwiese(self):
        m = re.search(r"unter <strong>(\d+) Beispielen</strong>", self.text)
        self.assertIsNotNone(m, "Der Hinweis in der Sofort-Demo nennt keine Zahl mehr.")
        self.assertEqual(int(m.group(1)), self.spielwiese)

    def test_ruthner_at_nennt_dieselbe_zahl(self):
        """Nur auf Wolfgangs Rechner. Auf einem CI-Läufer liegt unter diesem Pfad die
        Standardseite von Apache — die Datei ist also da, aber es ist nicht unsere."""
        if not ist_ruthner_at():
            self.skipTest("Die Startseite von ruthner.at liegt hier nicht")
        self.assertIn(f"{WORT[self.spielwiese]} Beispielprogramme",
                      HEIM.read_text(encoding="utf-8"))
