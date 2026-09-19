"""Härtung: Grenzen, Dateisystem, Absturzschutz – und verständliche Fehlermeldungen."""
import os
import tempfile
import time
import unittest
from pathlib import Path

from klarsatz import Interpreter, KlarsatzFehler, LaufzeitFehler, LimitFehler, SyntaxFehler
from klarsatz.dateisystem import KeinDateisystem, OrdnerDateisystem, SpeicherDateisystem
from klarsatz.fehler import formatiere_fehler
from klarsatz.grenzen import Grenzen


def laufe(code, eingaben=(), **kw):
    aus, eing = [], iter(eingaben)
    Interpreter(ausgabe=aus.append, eingabe=lambda _p="": next(eing), **kw).lauf(code)
    return aus


class Absturzschutz(unittest.TestCase):
    """Kein Programm darf mit einem Python-Traceback enden – immer nur mit einem Klarsatz-Fehler."""

    def test_tief_verschachtelte_klammern(self):
        with self.assertRaisesRegex(SyntaxFehler, "zu tief verschachtelt"):
            laufe("Zeige " + "(" * 50000 + "1" + ")" * 50000 + ".")

    def test_tief_verschachtelte_bloecke(self):
        code = "Wenn wahr ist:\n" * 200 + "Zeige 1.\n" + "Ende.\n" * 200
        with self.assertRaisesRegex(SyntaxFehler, "zu tief verschachtelt"):
            laufe(code)

    def test_kurzform_ketten(self):
        with self.assertRaises(SyntaxFehler):
            laufe("Wenn wahr ist, " * 5000 + "zeige 1.")

    def test_lange_ketten_von_operatoren(self):
        with self.assertRaises(SyntaxFehler):
            laufe("Wenn " + "nicht " * 5000 + "wahr ist, zeige 1.")
        with self.assertRaises(SyntaxFehler):
            laufe("Zeige " + "minus " * 5000 + "1.")
        with self.assertRaises(SyntaxFehler):
            laufe("Zeige 2 " + "hoch 2 " * 5000 + ".")

    def test_sehr_lange_rechnung_bricht_sauber_ab(self):
        code = "Zeige 1" + " plus 1" * 100000 + "."
        with self.assertRaises(KlarsatzFehler):
            laufe(code)

    def test_verschachtelte_aufrufe(self):
        code = "Definiere Aufgabe F von x:\nGib x zurück.\nEnde.\nZeige " + "F von " * 5000 + "1."
        with self.assertRaises(SyntaxFehler):
            laufe(code)

    def test_mittlere_verschachtelung_geht_noch(self):
        self.assertEqual(laufe("Zeige " + "(" * 20 + "1" + ")" * 20 + "."), ["1"])
        self.assertEqual(laufe("Wenn wahr ist:\n" * 10 + "Zeige 1.\n" + "Ende.\n" * 10), ["1"])

    def test_programm_zu_lang(self):
        with self.assertRaises(LimitFehler):
            laufe("Zeige 1.\n" * 1000, grenzen=Grenzen(quelltext=500))

    def test_selbstenthaltende_liste(self):
        with self.assertRaisesRegex(LaufzeitFehler, "selbst"):
            laufe("Erstelle Liste namens L.\nFüge L zu L hinzu.")

    def test_gegenseitig_enthaltende_listen_sind_kein_absturz(self):
        code = ("Erstelle Liste namens A.\nErstelle Liste namens B.\nFüge B zu A hinzu.\n"
                "Füge A zu B hinzu.\nZeige A.")
        with self.assertRaises(KlarsatzFehler):
            laufe(code)

    def test_riesige_zahl_anzeigen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "zu viele Stellen"):
            laufe("Merke 10 hoch 5000 als x.\nZeige x.")

    def test_python_meldungen_sind_deutsch(self):
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe("Merke 10 hoch 400 als x.\nMerke x mal 1.5 als y.")            # int zu groß für float


class Ressourcen(unittest.TestCase):
    def test_text_verdoppeln_wird_gestoppt(self):
        code = 'Merke "aaaaaaaaaa" als T.\nWiederhole 100 Mal:\nVerbinde T und T zu T.\nEnde.'
        with self.assertRaisesRegex(LaufzeitFehler, "zu lang"):
            laufe(code)                                                          # Standardgrenze
        with self.assertRaisesRegex(LaufzeitFehler, "zu lang"):
            laufe(code, grenzen=Grenzen(text=1000))

    def test_liste_waechst_unbegrenzt(self):
        code = "Erstelle Liste namens L.\nWiederhole solange wahr ist:\nFüge 1 zu L hinzu.\nEnde."
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe(code, grenzen=Grenzen(liste=1000))

    def test_teile_erzeugt_zu_grosse_liste(self):
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe('Merke "a,a,a,a,a,a,a,a,a,a" als T.\nTeile T bei "," zu L.', grenzen=Grenzen(liste=5))

    def test_zahlen_wachsen_unbegrenzt(self):
        code = "Merke 3 als x.\nWiederhole 1000 Mal:\nMerke x mal x als x.\nEnde."
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe(code)
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe("Zeige 9 hoch 9 hoch 9.")

    def test_ausgabelimit_laesst_sich_nicht_abfangen(self):
        code = ('Versuche:\n  Wiederhole solange wahr ist:\n    Zeige "xxxxxxxxxx".\n  Ende.\n'
                'Bei Fehler:\n  Zeige "gefangen".\nEnde.')
        aus = []
        with self.assertRaises(LimitFehler):
            Interpreter(ausgabe=aus.append, grenzen=Grenzen(ausgabe=1000)).lauf(code)
        self.assertNotIn("gefangen", aus)
        self.assertLessEqual(len(aus), 100)

    def test_zeitlimit(self):
        start = time.monotonic()
        with self.assertRaisesRegex(LimitFehler, "Zeitlimit"):
            laufe("Wiederhole solange wahr ist:\nMerke 1 als x.\nEnde.", grenzen=Grenzen(sekunden=0.3))
        self.assertLess(time.monotonic() - start, 5)

    def test_zeitlimit_nicht_abfangbar(self):
        code = "Versuche:\n  Wiederhole solange wahr ist:\n  Ende.\nBei Fehler:\n  Zeige 1.\nEnde."
        with self.assertRaises(LimitFehler):
            laufe(code, grenzen=Grenzen(sekunden=0.2))

    def test_eingabe_wird_gekuerzt(self):
        aus = laufe('Frage "?" und merke die Antwort als A.\nZeige Länge von A.', ["x" * 50000],
                    grenzen=Grenzen(eingabe=100))
        self.assertEqual(aus, ["100"])

    def test_streng_ist_strenger(self):
        s, n = Grenzen.streng(), Grenzen()
        self.assertLess(s.text, n.text)
        self.assertIsNotNone(s.sekunden)
        with self.assertRaises(LimitFehler):
            laufe("Zeige 1.\n" * 200000, grenzen=Grenzen.streng())

    def test_grenzen_pro_lauf_neu_gezaehlt(self):
        it = Interpreter(ausgabe=lambda _z: None, max_schritte=50)
        it.lauf("Zeige 1.\n" * 30)
        it.lauf("Zeige 1.\n" * 30)                       # zweiter Lauf hat wieder 50 Schritte


class Dateizugriff(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        (self.dir / "innen.txt").write_text("drinnen", encoding="utf-8")
        self.aussen = tempfile.TemporaryDirectory()
        (Path(self.aussen.name) / "geheim.txt").write_text("geheim", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()
        self.aussen.cleanup()

    def fs(self):
        return OrdnerDateisystem(self.dir)

    def test_innerhalb_des_ordners(self):
        aus = laufe('Lies die Datei "innen.txt" als X.\nZeige X.\nSchreibe "neu" in die Datei "neu.txt".', dateisystem=self.fs())
        self.assertEqual(aus, ["drinnen"])
        self.assertEqual((self.dir / "neu.txt").read_text(encoding="utf-8"), "neu")

    def test_unterordner_erlaubt(self):
        (self.dir / "sub").mkdir()
        laufe('Schreibe "x" in die Datei "sub/a.txt".', dateisystem=self.fs())
        self.assertTrue((self.dir / "sub" / "a.txt").exists())

    def test_absoluter_pfad_ausserhalb_ist_gesperrt(self):
        pfad = str(Path(self.aussen.name) / "geheim.txt")
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe(f'Lies die Datei "{pfad}" als X.', dateisystem=self.fs())
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe('Lies die Datei "/etc/hostname" als X.', dateisystem=self.fs())

    def test_schreiben_ausserhalb_ist_gesperrt(self):
        pfad = str(Path(self.aussen.name) / "neu.txt")
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe(f'Schreibe "x" in die Datei "{pfad}".', dateisystem=self.fs())
        self.assertFalse((Path(self.aussen.name) / "neu.txt").exists())

    def test_punkt_punkt_ausbruch(self):
        rel = os.path.relpath(Path(self.aussen.name) / "geheim.txt", self.dir)
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe(f'Lies die Datei "{rel}" als X.', dateisystem=self.fs())

    def test_symlink_ausbruch(self):
        link = self.dir / "abkuerzung"
        try:
            os.symlink(self.aussen.name, link)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks nicht verfügbar")
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe('Lies die Datei "abkuerzung/geheim.txt" als X.', dateisystem=self.fs())
        with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
            laufe('Schreibe "x" in die Datei "abkuerzung/neu.txt".', dateisystem=self.fs())

    def test_ordner_statt_datei_und_fehlende_datei(self):
        (self.dir / "sub").mkdir()
        with self.assertRaisesRegex(LaufzeitFehler, "ist ein Ordner"):
            laufe('Lies die Datei "sub" als X.', dateisystem=self.fs())
        with self.assertRaisesRegex(LaufzeitFehler, "gibt es nicht"):
            laufe('Lies die Datei "nix.txt" als X.', dateisystem=self.fs())

    def test_ungueltige_namen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "kein gültiger Dateiname"):
            laufe('Lies die Datei "" als X.', dateisystem=self.fs())
        with self.assertRaisesRegex(LaufzeitFehler, "Text sein"):
            laufe('Lies die Datei 5 als X.', dateisystem=self.fs())

    def test_dateigroesse_ist_begrenzt(self):
        (self.dir / "gross.txt").write_text("x" * 5000, encoding="utf-8")
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe('Lies die Datei "gross.txt" als X.', dateisystem=self.fs(), grenzen=Grenzen(datei=1000, text=1000))
        with self.assertRaisesRegex(LaufzeitFehler, "zu lang"):
            laufe('Merke "abcdef" als T.\nSchreibe T in die Datei "k.txt".', dateisystem=self.fs(), grenzen=Grenzen(datei=3))

    def test_binaerdatei_ist_kein_absturz(self):
        (self.dir / "b.bin").write_bytes(bytes(range(128, 256)))
        with self.assertRaisesRegex(LaufzeitFehler, "keine Textdatei"):
            laufe('Lies die Datei "b.bin" als X.', dateisystem=self.fs())

    def test_standard_ist_der_arbeitsordner(self):
        alt = os.getcwd()
        try:
            os.chdir(self.dir)
            self.assertEqual(laufe('Lies die Datei "innen.txt" als X.\nZeige X.'), ["drinnen"])
            with self.assertRaisesRegex(LaufzeitFehler, "nicht zugreifen"):
                laufe('Lies die Datei "/etc/hostname" als X.')
        finally:
            os.chdir(alt)

    def test_ueberall_erlaubt_ist_moeglich_aber_ausdruecklich(self):
        pfad = str(Path(self.aussen.name) / "geheim.txt")
        self.assertEqual(laufe(f'Lies die Datei "{pfad}" als X.\nZeige X.', dateisystem=OrdnerDateisystem(None)),
                         ["geheim"])

    def test_speicherdateisystem(self):
        sp = SpeicherDateisystem({"a.txt": "eins"})
        aus = laufe('Lies die Datei "a.txt" als X.\nZeige X.\nSchreibe "zwei" in die Datei "b.txt".', dateisystem=sp)
        self.assertEqual(aus, ["eins"])
        self.assertEqual(sp.dateien["b.txt"], "zwei")
        with self.assertRaisesRegex(LaufzeitFehler, "gibt es nicht"):
            laufe('Lies die Datei "c.txt" als X.', dateisystem=sp)

    def test_speicherdateisystem_hat_eine_obergrenze(self):
        sp = SpeicherDateisystem(max_dateien=2)
        with self.assertRaisesRegex(LaufzeitFehler, "mehr geht nicht"):
            laufe('Zähle von 1 bis 5 mit i:\nVerbinde "d" und i zu N.\nSchreibe "x" in die Datei N.\nEnde.', dateisystem=sp)

    def test_kein_dateisystem(self):
        with self.assertRaisesRegex(LaufzeitFehler, "abgeschaltet"):
            laufe('Schreibe "x" in die Datei "a.txt".', dateisystem=KeinDateisystem())


class Fehlermeldungen(unittest.TestCase):
    def fehler(self, code, **kw):
        with self.assertRaises(KlarsatzFehler) as cm:
            laufe(code, **kw)
        return cm.exception

    def test_aufrufkette(self):
        code = ("Definiere Aufgabe Innen von x:\n"
                "    Gib 10 geteilt durch x zurück.\n"
                "Ende.\n"
                "Definiere Aufgabe Aussen von y:\n"
                "    Gib Innen von y zurück.\n"
                "Ende.\n"
                "Zeige Aussen von 0.\n")
        e = self.fehler(code)
        self.assertEqual(e.zeile, 2)
        self.assertEqual(e.aufrufe, [("Innen", 5), ("Aussen", 7)])
        text = formatiere_fehler(e, code)
        self.assertIn("Durch null kann man nicht teilen.", text)
        self.assertIn("in der Aufgabe „Innen“, aufgerufen in Zeile 5", text)
        self.assertIn("in der Aufgabe „Aussen“, aufgerufen in Zeile 7", text)
        self.assertIn("Zeige Aussen von 0.", text)

    def test_rekursion_zeigt_kurze_kette(self):
        code = "Definiere Aufgabe F von x:\n    Gib F von x zurück.\nEnde.\nZeige F von 1.\n"
        e = self.fehler(code, grenzen=Grenzen(tiefe=5))
        self.assertIn("Abbruchbedingung", e.meldung)
        self.assertGreaterEqual(len(e.aufrufe), 5)

    def test_syntaxfehler_zeigt_spalte_und_markierung(self):
        code = "Merke 5 als Zahl.\nZeigee Zahl.\n"
        e = self.fehler(code)
        self.assertEqual((e.zeile, e.spalte, e.laenge), (2, 0, 6))
        text = formatiere_fehler(e, code)
        self.assertIn("(Zeile 2, Spalte 1)", text)
        self.assertIn("^^^^^^", text)
        self.assertIn("Meintest du 'Zeige'?", text)

    def test_fehlender_punkt_wird_hinter_dem_letzten_wort_markiert(self):
        code = "Zeige 1\nZeige 2.\n"
        e = self.fehler(code)
        self.assertEqual((e.zeile, e.spalte), (1, 7))
        text = formatiere_fehler(e, code).splitlines()
        self.assertEqual(text[1], "     1 | Zeige 1")
        self.assertEqual(text[2], "       |        ^")

    def test_unbekanntes_zeichen_mit_hinweis(self):
        code = "Zeige 1 + 2.\n"
        e = self.fehler(code)
        self.assertIn("plus, minus, mal", e.meldung)
        self.assertEqual(e.spalte, 8)

    def test_tabulatoren_verschieben_die_markierung_nicht(self):
        code = "Wenn wahr ist:\n\tZeigee 1.\nEnde.\n"
        text = formatiere_fehler(self.fehler(code), code).splitlines()
        self.assertIn("Zeigee", text[1])
        self.assertEqual(text[2].index("^"), text[1].index("Z"))

    def test_namenskollision_variable_und_aufgabe(self):
        kopf = "Definiere Aufgabe Klein von x:\n    Gib x zurück.\nEnde.\n"
        for zeile in ["Merke 1 als Klein.", 'Frage "?" und merke die Antwort als Klein.', "Zähle von 1 bis 2 mit Klein:\nEnde.",
                      "Erstelle Liste namens Klein.", "Setze Klein auf 3."]:
            with self.subTest(zeile=zeile):
                e = self.fehler(kopf + zeile + "\n", eingaben=["1"]) if False else self.fehler(kopf + zeile + "\n")
                self.assertIsInstance(e, SyntaxFehler)
                self.assertIn("Name einer Aufgabe", e.meldung)

    def test_aufgabe_ohne_werte_aufgerufen(self):
        e = self.fehler("Definiere Aufgabe Klein von x:\n    Gib x zurück.\nEnde.\nZeige Klein.\n")
        self.assertIn("Ist eine Variable gemeint?", e.meldung)

    def test_speicherfehler_hat_text(self):
        # simuliert: MemoryError in einer Anweisung
        class Kaputt(Interpreter):
            def _a_zeige(self, k, b):
                raise MemoryError
        with self.assertRaisesRegex(LaufzeitFehler, "Speicher"):
            Kaputt(ausgabe=lambda _z: None).lauf('Zeige 1.')

    def test_limitfehler_ueberschrift(self):
        code = "Wiederhole solange wahr ist:\nEnde.\n"
        e = self.fehler(code, max_schritte=100)
        self.assertTrue(formatiere_fehler(e, code).startswith("Abgebrochen"))


class Kommandozeile(unittest.TestCase):
    def lauf_cli(self, args, stdin=""):
        import contextlib
        import io
        from klarsatz.cli import main
        out, err = io.StringIO(), io.StringIO()
        alt = __import__("sys").stdin
        __import__("sys").stdin = io.StringIO(stdin)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = main(args)
        finally:
            __import__("sys").stdin = alt
        return code, out.getvalue(), err.getvalue()

    def datei(self, inhalt):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p = Path(d.name) / "t.klar"
        p.write_text(inhalt, encoding="utf-8")
        return str(p)

    def test_lauf_und_fehlerausgabe(self):
        code, out, err = self.lauf_cli([self.datei('Zeige "hallo".')])
        self.assertEqual((code, out.strip()), (0, "hallo"))
        code, out, err = self.lauf_cli([self.datei("Zeige 1 geteilt durch 0.")])
        self.assertEqual(code, 1)
        self.assertIn("Fehler beim Ausführen (Zeile 1)", err)

    def test_fehlende_datei(self):
        code, out, err = self.lauf_cli(["/gibt/es/nicht.klar"])
        self.assertEqual(code, 2)
        self.assertIn("lässt sich nicht öffnen", err)

    def test_interner_fehler_wird_nicht_zum_traceback(self):
        import klarsatz.cli as cli
        alt = cli.Interpreter.lauf
        cli.Interpreter.lauf = lambda self, q: 1 / 0
        try:
            code, out, err = self.lauf_cli([self.datei("Zeige 1.")])
        finally:
            cli.Interpreter.lauf = alt
        self.assertEqual(code, 70)
        self.assertIn("Interner Fehler im Interpreter", err)
        self.assertNotIn("Traceback", err)

    def test_tokens_und_ast(self):
        p = self.datei('Zeige "a".')
        code, out, _ = self.lauf_cli(["--tokens", p])
        self.assertIn("WORT   'Zeige'", out)
        code, out, _ = self.lauf_cli(["--ast", p])
        self.assertIn("'zeige'", out)

    def test_dateioptionen(self):
        p = self.datei('Lies die Datei "/etc/hostname" als X.\nZeige "gelesen".')
        code, out, err = self.lauf_cli([p])
        self.assertEqual(code, 1)
        self.assertIn("nicht zugreifen", err)
        code, out, err = self.lauf_cli([p, "--ohne-dateien"])
        self.assertIn("abgeschaltet", err)
        code, out, err = self.lauf_cli([p, "--dateien-ueberall"])
        self.assertIn(code, (0, 1))                                   # je nach Rechner gibt es /etc/hostname
        self.assertNotIn("nicht zugreifen", err)

    def test_zeit_und_streng(self):
        p = self.datei("Wiederhole solange wahr ist:\nEnde.")
        code, out, err = self.lauf_cli([p, "--zeit", "0.3"])
        self.assertEqual(code, 1)
        self.assertIn("Zeitlimit", err)
        code, out, err = self.lauf_cli([p, "--streng-grenzen", "--limit", "2000"])
        self.assertIn("Schrittlimit", err)



class FeldzugriffAufNichtDinge(unittest.TestCase):
    """Ein Feldzugriff auf etwas, das kein Ding ist, muss freundlich scheitern —
    nicht mit einem Python-Fehler (hier stolperte der Interpreter über obj.werte)."""

    def test_feld_auf_zahl_lesen(self):
        # Ein Wort, das keine eingebaute Funktion ist, liest Klarsatz als Feldnamen.
        with self.assertRaisesRegex(LaufzeitFehler, "geht nur bei Dingen"):
            Interpreter(ausgabe=lambda _z: None).lauf("Zeige den Umfang von 30.")

    def test_feld_auf_zahl_setzen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "geht nur bei Dingen"):
            Interpreter(ausgabe=lambda _z: None).lauf("Merke 5 als n.\nSetze das Alter von n auf 3.")

    def test_feld_auf_text(self):
        with self.assertRaisesRegex(LaufzeitFehler, "geht nur bei Dingen"):
            Interpreter(ausgabe=lambda _z: None).lauf('Merke "abc" als t.\nZeige die Größe von t.')


if __name__ == "__main__":
    unittest.main()
