"""Formatierer: ordentlich einrücken, nie den Inhalt ändern."""
import contextlib
import io
import random
import tempfile
import unittest
from pathlib import Path

from klarsatz import SyntaxFehler
from klarsatz.cli import main
from klarsatz.formatierer import formatiere
from klarsatz.interpreter import Interpreter
from klarsatz.lexer import lexer

WURZEL = Path(__file__).resolve().parent.parent
ALLE = sorted(list((WURZEL / "programme").glob("*.klar")) + list((WURZEL / "beispiele").glob("*.klar")))


def tokens(text):
    return [(t.art, t.wert) for t in lexer(text)]


class Einruecken(unittest.TestCase):
    def test_bloecke(self):
        roh = 'Wenn wahr ist:\nZeige 1.\nWiederhole 2 Mal:\nZeige 2.\nEnde.\nEnde.\nZeige 3.\n'
        soll = 'Wenn wahr ist:\n    Zeige 1.\n    Wiederhole 2 Mal:\n        Zeige 2.\n    Ende.\nEnde.\nZeige 3.\n'
        self.assertEqual(formatiere(roh), soll)

    def test_sonst_zweige_stehen_auf_hoehe_des_wenn(self):
        roh = ('Wenn a gleich 1 ist:\nZeige 1.\nSonst wenn a gleich 2 ist:\nZeige 2.\nSonst:\nZeige 3.\nEnde.\n')
        soll = ('Wenn a gleich 1 ist:\n    Zeige 1.\nSonst wenn a gleich 2 ist:\n    Zeige 2.\nSonst:\n    Zeige 3.\nEnde.\n')
        self.assertEqual(formatiere(roh), soll)

    def test_kurzform_ketten_bleiben_auf_einer_ebene(self):
        roh = 'Zähle von 1 bis 3 mit i:\nWenn i gleich 1 ist, zeige "a".\nSonst wenn i gleich 2 ist, zeige "b".\nSonst zeige "c".\nEnde.\n'
        soll = 'Zähle von 1 bis 3 mit i:\n    Wenn i gleich 1 ist, zeige "a".\n    Sonst wenn i gleich 2 ist, zeige "b".\n    Sonst zeige "c".\nEnde.\n'
        self.assertEqual(formatiere(roh), soll)

    def test_versuche_bei_fehler(self):
        roh = 'Versuche:\nZeige 1.\nBei Fehler:\nZeige 2.\nEnde.\n'
        soll = 'Versuche:\n    Zeige 1.\nBei Fehler:\n    Zeige 2.\nEnde.\n'
        self.assertEqual(formatiere(roh), soll)

    def test_aufgaben(self):
        roh = 'Definiere Aufgabe F von x:\nGib x zurück.\nEnde.\nZeige F von 1.\n'
        self.assertEqual(formatiere(roh), 'Definiere Aufgabe F von x:\n    Gib x zurück.\nEnde.\nZeige F von 1.\n')

    def test_saetze_ueber_mehrere_zeilen(self):
        roh = 'Erstelle Liste namens L mit\n"a"\nund "b".\nZeige L.\n'
        soll = 'Erstelle Liste namens L mit\n    "a"\n    und "b".\nZeige L.\n'
        self.assertEqual(formatiere(roh), soll)

    def test_kommentare_bleiben_erhalten(self):
        roh = 'Anmerkung: Kopf\nWenn wahr ist:\nAnmerkung: drinnen\nZeige 1. Anmerkung: hinten\nEnde.\n'
        soll = 'Anmerkung: Kopf\nWenn wahr ist:\n    Anmerkung: drinnen\n    Zeige 1. Anmerkung: hinten\nEnde.\n'
        self.assertEqual(formatiere(roh), soll)

    def test_doppelpunkt_im_kommentar_oeffnet_keinen_block(self):
        roh = 'Zeige 1. Anmerkung: bla:\nZeige 2.\n'
        self.assertEqual(formatiere(roh), roh)

    def test_doppelpunkt_im_text_oeffnet_keinen_block(self):
        roh = 'Zeige "Ergebnis:".\nZeige 2.\n'
        self.assertEqual(formatiere(roh), roh)

    def test_tabulatoren_und_leerzeichen_am_zeilenende(self):
        self.assertEqual(formatiere('Wenn wahr ist:\t \n\t\tZeige 1.   \nEnde.\n'), 'Wenn wahr ist:\n    Zeige 1.\nEnde.\n')

    def test_leerzeilen(self):
        self.assertEqual(formatiere('\n\n\nZeige 1.\n\n\n\nZeige 2.\n\n\n'), 'Zeige 1.\n\nZeige 2.\n')

    def test_leere_und_kommentar_eingaben(self):
        self.assertEqual(formatiere(''), '')
        self.assertEqual(formatiere('\n\n'), '')
        self.assertEqual(formatiere('Anmerkung: nur ein Kommentar'), 'Anmerkung: nur ein Kommentar\n')

    def test_zu_viele_ende_werden_nicht_negativ(self):
        self.assertEqual(formatiere('Ende.\nEnde.\nZeige 1.\n'), 'Ende.\nEnde.\nZeige 1.\n')

    def test_einzugsbreite(self):
        self.assertEqual(formatiere('Wenn wahr ist:\nZeige 1.\nEnde.\n', einzug=2), 'Wenn wahr ist:\n  Zeige 1.\nEnde.\n')

    def test_lexerfehler_werden_gemeldet(self):
        with self.assertRaises(SyntaxFehler):
            formatiere('Zeige "offen.')


class Unveraenderlichkeit(unittest.TestCase):
    def test_idempotent_und_inhaltsgleich_fuer_alle_programme(self):
        for datei in ALLE:
            with self.subTest(programm=datei.name):
                s = datei.read_text(encoding="utf-8")
                t = formatiere(s)
                self.assertEqual(formatiere(t), t)
                self.assertEqual([(a, b) for a, b in tokens(s)], [(a, b) for a, b in tokens(t)])

    def test_mitgelieferte_programme_sind_schon_sauber(self):
        for datei in ALLE:
            with self.subTest(programm=datei.name):
                s = datei.read_text(encoding="utf-8")
                self.assertEqual(formatiere(s), s)

    def test_eingerueckt_zerstoert_und_wiederhergestellt(self):
        zufall = random.Random(1)
        for datei in ALLE:
            with self.subTest(programm=datei.name):
                s = datei.read_text(encoding="utf-8")
                kaputt = "\n".join(
                    (" " * zufall.randint(0, 9) if zufall.random() < 0.5 else "\t" * zufall.randint(0, 3)) + z.strip()
                    for z in s.split("\n"))
                self.assertEqual(formatiere(kaputt), s)

    def test_programme_laufen_nach_dem_formatieren_gleich(self):
        for name in ("fizzbuzz.klar", "aufgaben.klar", "listen.klar", "rechnen.klar", "dinge.klar"):
            with self.subTest(programm=name):
                s = (WURZEL / "beispiele" / name).read_text(encoding="utf-8")
                kaputt = "\n".join(z.strip() for z in s.split("\n"))
                a, b = [], []
                Interpreter(ausgabe=a.append).lauf(s)
                Interpreter(ausgabe=b.append).lauf(formatiere(kaputt))
                self.assertEqual(a, b)


class Kommandozeile(unittest.TestCase):
    def cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(args))
        return code, out.getvalue()

    def test_ausgabe_und_ersetzen(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.klar"
            p.write_text("Wenn wahr ist:\nZeige 1.\nEnde.\n", encoding="utf-8")
            code, out = self.cli("--formatiere", str(p))
            self.assertEqual((code, out), (0, "Wenn wahr ist:\n    Zeige 1.\nEnde.\n"))
            self.assertEqual(p.read_text(encoding="utf-8"), "Wenn wahr ist:\nZeige 1.\nEnde.\n")     # unverändert
            code, out = self.cli("--formatiere", "--ersetzen", str(p))
            self.assertIn("neu formatiert", out)
            self.assertEqual(p.read_text(encoding="utf-8"), "Wenn wahr ist:\n    Zeige 1.\nEnde.\n")
            code, out = self.cli("--formatiere", "--ersetzen", str(p))
            self.assertIn("schon sauber", out)


if __name__ == "__main__":
    unittest.main()
