"""Die interaktive Konsole – mit einem simulierten Menschen am Eingabefeld."""
import tempfile
import unittest
from pathlib import Path

from klarsatz import Interpreter
from klarsatz.grenzen import Grenzen
from klarsatz.repl import starte_konsole


def sitzung(zeilen, interpreter=None, **kw):
    """Spielt eine Konsolensitzung durch; gibt alles zurück, was am Bildschirm erschienen wäre."""
    it = iter(zeilen)
    schirm = []

    def eingabe(prompt=""):
        try:
            z = next(it)
        except StopIteration:
            raise EOFError
        schirm.append(prompt + z)
        return z

    interp = interpreter or Interpreter(ausgabe=schirm.append, eingabe=eingabe, **kw)
    code = starte_konsole(interp, eingabe=eingabe, ausgabe=schirm.append, banner=False)
    return code, schirm


class Grundlagen(unittest.TestCase):
    def test_saetze_und_ausdruecke(self):
        code, s = sitzung(["Merke 5 als x.", "x plus 2", "x größer als 3", "x kleiner als 3", 'Zeige x mal 2.'])
        self.assertEqual(code, 0)
        self.assertIn("= 7", s)
        self.assertIn("= wahr", s)
        self.assertIn("= falsch", s)
        self.assertIn("10", s)
        self.assertEqual(s[-1], "Tschüss!")

    def test_ausdruecke_mit_texten_und_listen(self):
        _, s = sitzung(['Erstelle Liste namens L mit 1 und 2.', 'L', 'Länge von L', '"ab"'])
        self.assertIn("= [1, 2]", s)
        self.assertIn("= 2", s)
        self.assertIn("= ab", s)

    def test_mehrzeilige_bloecke(self):
        _, s = sitzung(["Merke 5 als x.", "Wenn x gleich 5 ist:", 'Zeige "fünf".', "Ende."])
        self.assertIn("      ... Zeige \"fünf\".", s)
        self.assertIn("fünf", s)

    def test_aufgaben_ueber_mehrere_eingaben(self):
        _, s = sitzung(["Definiere Aufgabe Quadrat von n:", "Gib n mal n zurück.", "Ende.",
                        "Quadrat von 4", "Zeige Quadrat von 3.", "Definiere Aufgabe Zwei:", "Zeige 2.", "Ende.", "Führe Zwei aus."])
        self.assertIn("= 16", s)
        self.assertIn("9", s)
        self.assertIn("2", s)

    def test_saetze_ueber_mehrere_zeilen(self):
        _, s = sitzung(["Erstelle Liste namens L mit", '"a"', 'und "b".', "Zeige L."])
        self.assertIn("[a, b]", s)

    def test_leere_zeilen_werden_ignoriert(self):
        code, s = sitzung(["", "   ", "Zeige 1."])
        self.assertIn("1", s)

    def test_frage_liest_von_derselben_eingabe(self):
        _, s = sitzung(['Frage "Name?" und merke die Antwort als N.', "Emil", 'Zeige "Hallo, " und N.'])
        self.assertIn("Hallo, Emil", s)


class Fehler(unittest.TestCase):
    def test_laufzeitfehler_beenden_die_sitzung_nicht(self):
        _, s = sitzung(["Zeige y.", "Zeige 1 plus 1."])
        self.assertTrue(any("Ich kenne 'y' nicht" in z for z in s))
        self.assertIn("2", s)

    def test_syntaxfehler_mit_markierung(self):
        _, s = sitzung(["Zeigee 1."])
        text = "\n".join(s)
        self.assertIn("Meintest du 'Zeige'?", text)
        self.assertIn("^^^^^^", text)

    def test_unfertiger_satz_wartet_weiter(self):
        _, s = sitzung(["Zeige 1", "."])
        self.assertIn("      ... .", s)
        self.assertIn("1", s)

    def test_leerzeile_erzwingt_fehlermeldung(self):
        _, s = sitzung(["Wenn wahr ist:", "Zeige 1.", ""])
        self.assertTrue(any("nie mit 'Ende.' geschlossen" in z for z in s))

    def test_nach_fehler_beginnt_neue_eingabe(self):
        _, s = sitzung(["Wenn wahr ist:", "", "Zeige 5."])
        self.assertIn("5", s)

    def test_falscher_ausdruck_wird_als_satz_gemeldet(self):
        _, s = sitzung(["foo bar baz"])
        self.assertTrue(any("Ich verstehe" in z for z in s))

    def test_unbekannte_variable_als_ausdruck(self):
        _, s = sitzung(["zahll"])
        self.assertTrue(any("Ich kenne 'zahll' nicht" in z for z in s))

    def test_endlosschleife_wird_gestoppt_und_konsole_lebt_weiter(self):
        interp = Interpreter(grenzen=Grenzen(schritte=500), ausgabe=lambda z: None)
        _, s = sitzung(["Wiederhole solange wahr ist:", "Merke 1 als a.", "Ende.", 'Zeige "noch da".'], interpreter=interp)
        self.assertTrue(any("Schrittlimit" in z for z in s))

    def test_strg_c_waehrend_einer_ausfuehrung(self):
        class Unterbrochen(Interpreter):
            def _a_zeige(self, k, b):
                raise KeyboardInterrupt
        _, s = sitzung(["Zeige 1.", "x"], interpreter=Unterbrochen(ausgabe=lambda z: None))
        self.assertIn("Abgebrochen.", "\n".join(s))

    def test_strg_c_bei_der_eingabe_verwirft_den_puffer(self):
        aufrufe = iter([KeyboardInterrupt, "Zeige 2.", EOFError])
        schirm = []

        def eingabe(prompt=""):
            x = next(aufrufe)
            if isinstance(x, type) and issubclass(x, BaseException):
                raise x
            return x
        starte_konsole(Interpreter(ausgabe=schirm.append), eingabe=eingabe, ausgabe=schirm.append, banner=False)
        self.assertIn("2", schirm)
        self.assertTrue(any("verworfen" in z for z in schirm))


class Befehle(unittest.TestCase):
    def test_hilfe_variablen_aufgaben(self):
        _, s = sitzung(["Merke 5 als x.", "Merke für immer 3 als Pi.", "Hund hat Name.",
                        "Definiere Aufgabe F mit a und b:", "Gib a zurück.", "Ende.", ":variablen", ":aufgaben", ":hilfe"])
        text = "\n".join(s)
        self.assertIn("  x = 5", text)
        self.assertIn("  Pi = 3  (Konstante)", text)
        self.assertIn("  Aufgabe F mit a und b", text)
        self.assertIn("  Ding Hund: Name", text)
        self.assertIn(":laden DATEI", text)

    def test_leere_uebersichten(self):
        _, s = sitzung([":variablen", ":aufgaben"])
        self.assertIn("(noch keine Variablen)", s)
        self.assertIn("(noch keine Aufgaben oder Dinge)", s)

    def test_neu_vergisst_alles(self):
        _, s = sitzung(["Merke 5 als x.", "Definiere Aufgabe F:", "Zeige 1.", "Ende.", ":neu", "x", "Führe F aus."])
        text = "\n".join(s)
        self.assertIn("Alles vergessen", text)
        self.assertIn("Ich kenne 'x' nicht", text)
        self.assertIn("Diese Aufgabe kenne ich nicht", text)

    def test_laden(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.klar"
            p.write_text('Merke 7 als g.\nDefiniere Aufgabe F:\n    Zeige g.\nEnde.\nZeige "geladen".\n', encoding="utf-8")
            _, s = sitzung([f":laden {p}", "Führe F aus.", ":laden", ":laden /gibt/es/nicht.klar"])
        text = "\n".join(s)
        self.assertIn("geladen", s)
        self.assertIn("7", s)
        self.assertIn("Welche Datei?", text)
        self.assertIn("lässt sich nicht laden", text)

    def test_laden_mit_fehler_im_programm(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.klar"
            p.write_text("Zeige x.\n", encoding="utf-8")
            _, s = sitzung([f":laden {p}"])
        self.assertTrue(any("Ich kenne 'x' nicht" in z for z in s))

    def test_unbekannter_befehl(self):
        _, s = sitzung([":blub"])
        self.assertTrue(any("kenne ich nicht" in z for z in s))

    def test_ende_beendet(self):
        code, s = sitzung([":ende", "Zeige 1."])
        self.assertEqual(code, 0)
        self.assertNotIn("1", s)
        self.assertEqual(s[-1], "Tschüss!")

    def test_befehle_gelten_nur_am_anfang_einer_eingabe(self):
        _, s = sitzung(["Erstelle Liste namens L mit", ":ende", "Zeige 1."])       # ':ende' ist hier Teil des Satzes
        self.assertNotIn("Tschüss!", s[:-1])


class ZusammenspielMitCli(unittest.TestCase):
    def test_cli_ohne_datei_startet_die_konsole(self):
        import contextlib
        import io
        import sys
        from klarsatz.cli import main
        alt = sys.stdin
        sys.stdin = io.StringIO("Zeige 1 plus 1.\n")
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = main([])
        finally:
            sys.stdin = alt
        self.assertEqual(code, 0)
        self.assertIn("2", out.getvalue())
        self.assertIn("interaktive Konsole", out.getvalue())


if __name__ == "__main__":
    unittest.main()
