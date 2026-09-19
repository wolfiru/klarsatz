"""Prüfmodus: findet er, was er finden soll – und lässt gute Programme in Ruhe?"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from klarsatz.cli import main
from klarsatz.pruefer import formatiere_befunde, pruefe

WURZEL = Path(__file__).resolve().parent.parent


def codes(code):
    return [b.code for b in pruefe(code)]


def finde(code, kennung):
    return [b for b in pruefe(code) if b.code == kennung]


class Namen(unittest.TestCase):
    def test_tippfehler_mit_vorschlag(self):
        b = finde("Merke 5 als Zahl.\nZeige Zahll.", "unbekannter-name")
        self.assertEqual(len(b), 1)
        self.assertEqual((b[0].schwere, b[0].zeile), ("Fehler", 2))
        self.assertIn("Meintest du 'Zahl'?", b[0].meldung)

    def test_auch_in_selten_erreichten_zweigen(self):
        code = "Merke 5 als Zahl.\nWenn Zahl größer als 100 ist:\n    Zeige Zahll.\nEnde."
        self.assertEqual(len(finde(code, "unbekannter-name")), 1)

    def test_setze_auf_unbekannten_namen(self):
        b = finde("Setze x auf 3.", "unbekannter-name")
        self.assertIn("Lege es zuerst mit 'Merke", b[0].meldung)

    def test_lokale_namen_sind_aussen_unbekannt(self):
        code = "Definiere Aufgabe F von x:\n    Merke 1 als y.\n    Gib x plus y zurück.\nEnde.\nZeige F von 1.\nZeige y."
        b = finde(code, "unbekannter-name")
        self.assertEqual([x.zeile for x in b], [6])

    def test_aufgaben_lesen_globale_namen(self):
        code = "Merke 10 als g.\nDefiniere Aufgabe F von x:\n    Gib x plus g zurück.\nEnde.\nZeige F von 1."
        self.assertEqual(finde(code, "unbekannter-name"), [])

    def test_fehlermeldung_ist_nach_versuche_bekannt(self):
        code = "Versuche:\n    Zeige 1.\nBei Fehler:\n    Zeige Fehlermeldung.\nEnde."
        self.assertEqual(finde(code, "unbekannter-name"), [])

    def test_alle_arten_der_anlage_zaehlen(self):
        code = ('Frage "?" und merke die Antwort als A.\nErstelle Liste namens L.\nErstelle Tabelle namens T.\n'
                'Verbinde "a" zu V.\nTeile "a,b" bei "," zu P.\nKopiere L als K.\nLies die Datei "x" als D.\n'
                'Zähle von 1 bis 2 mit I:\nEnde.\nFür jedes E in L:\nEnde.\n'
                'Zeige A und V und P und K und D und L und T und I und E.')
        self.assertEqual(finde(code, "unbekannter-name"), [])


class Reihenfolge(unittest.TestCase):
    def test_benutzt_vor_anlegen(self):
        b = finde("Zeige x.\nMerke 1 als x.", "benutzt-vor-anlegen")
        self.assertEqual((b[0].zeile, b[0].schwere), (1, "Warnung"))
        self.assertIn("Zeile 2", b[0].meldung)

    def test_normale_reihenfolge_ist_ruhig(self):
        self.assertEqual(finde("Merke 1 als x.\nZeige x.", "benutzt-vor-anlegen"), [])

    def test_aufgaben_duerfen_spaeter_angelegte_globale_lesen(self):
        code = "Definiere Aufgabe F:\n    Zeige g.\nEnde.\nMerke 1 als g.\nFühre F aus."
        self.assertEqual(codes(code).count("benutzt-vor-anlegen"), 0)

    def test_gleiche_zeile_ist_ok(self):
        self.assertEqual(finde("Merke 1 als x.\nMerke x plus 1 als x.", "benutzt-vor-anlegen"), [])


class Konstanten(unittest.TestCase):
    def test_aendern_ist_ein_fehler(self):
        for zeile in ["Setze P auf 4.", "Erhöhe P um 1.", "Merke 4 als P."]:
            with self.subTest(zeile=zeile):
                b = finde(f"Merke für immer 3 als P.\n{zeile}", "konstante-aendern")
                self.assertEqual((len(b), b[0].schwere, b[0].zeile), (1, "Fehler", 2))

    def test_konstante_in_schleife(self):
        b = finde("Wiederhole 3 Mal:\n    Merke für immer 3 als P.\nEnde.\nZeige 1.", "konstante-in-schleife")
        self.assertEqual(b[0].schwere, "Warnung")

    def test_zweimal_anlegen(self):
        self.assertEqual(len(finde("Merke für immer 1 als P.\nMerke für immer 2 als P.", "konstante-aendern")), 1)

    def test_lesen_ist_erlaubt(self):
        self.assertEqual(finde("Merke für immer 3 als P.\nZeige P plus 1.", "konstante-aendern"), [])

    def test_gleicher_name_in_aufgabe_ist_eine_andere_konstante(self):
        code = "Merke für immer 3 als P.\nDefiniere Aufgabe F:\n    Merke 5 als P.\n    Zeige P.\nEnde.\nFühre F aus.\nZeige P."
        self.assertEqual(finde(code, "konstante-aendern"), [])


class Kontrollfluss(unittest.TestCase):
    def test_gib_ausserhalb(self):
        self.assertEqual(len(finde("Gib 1 zurück.", "gib-ausserhalb")), 1)

    def test_abbruch_ausserhalb(self):
        self.assertEqual(len(finde("Höre auf.", "ausserhalb-schleife")), 1)
        self.assertEqual(len(finde("Mach weiter.", "ausserhalb-schleife")), 1)

    def test_abbruch_in_aufgabe_zaehlt_die_umgebende_schleife_nicht(self):
        code = "Wiederhole 2 Mal:\n    Definiere Aufgabe F:\n        Höre auf.\n    Ende.\nEnde."
        self.assertEqual(len(finde(code, "ausserhalb-schleife")), 1)

    def test_abbruch_in_schleife_ist_ok(self):
        code = "Wiederhole 2 Mal:\n    Wenn wahr ist, höre auf.\nEnde."
        self.assertEqual(finde(code, "ausserhalb-schleife"), [])

    def test_unerreichbar_nach_gib(self):
        code = "Definiere Aufgabe F:\n    Gib 1 zurück.\n    Zeige 2.\nEnde.\nZeige F."
        b = finde(code, "unerreichbar")
        self.assertEqual((len(b), b[0].zeile), (1, 3))

    def test_unerreichbar_nach_vollstaendigem_wenn(self):
        code = ("Definiere Aufgabe F von x:\n    Wenn x gleich 1 ist:\n        Gib 1 zurück.\n    Sonst:\n"
                "        Gib 2 zurück.\n    Ende.\n    Zeige 3.\nEnde.\nZeige F von 1.")
        self.assertEqual(len(finde(code, "unerreichbar")), 1)

    def test_kein_alarm_ohne_sonst(self):
        code = ("Definiere Aufgabe F von x:\n    Wenn x gleich 1 ist:\n        Gib 1 zurück.\n    Ende.\n"
                "    Gib 2 zurück.\nEnde.\nZeige F von 1.")
        self.assertEqual(finde(code, "unerreichbar"), [])

    def test_unerreichbar_nach_abbruch(self):
        code = "Wiederhole 2 Mal:\n    Höre auf.\n    Zeige 1.\nEnde."
        self.assertEqual(len(finde(code, "unerreichbar")), 1)


class Endlosschleifen(unittest.TestCase):
    def test_immer_wahr_ohne_ausgang(self):
        b = finde("Wiederhole solange wahr ist:\n    Zeige 1.\nEnde.", "endlosschleife")
        self.assertEqual((len(b), b[0].zeile, b[0].schwere), (1, 1, "Warnung"))

    def test_mit_hoere_auf_ist_es_ok(self):
        code = "Wiederhole solange wahr ist:\n    Frage \"?\" und merke die Antwort als A.\n    Wenn A gleich 1 ist, höre auf.\nEnde."
        self.assertEqual(finde(code, "endlosschleife"), [])

    def test_mit_gib_ist_es_ok(self):
        code = "Definiere Aufgabe F:\n    Wiederhole solange wahr ist:\n        Gib 1 zurück.\n    Ende.\nEnde.\nZeige F."
        self.assertEqual(finde(code, "endlosschleife"), [])

    def test_abbruch_der_inneren_schleife_reicht_nicht(self):
        code = ("Wiederhole solange wahr ist:\n    Wiederhole 3 Mal:\n        Höre auf.\n    Ende.\nEnde.")
        self.assertEqual(len(finde(code, "endlosschleife")), 1)

    def test_bedingung_wird_nie_veraendert(self):
        code = "Merke 0 als n.\nWiederhole solange n kleiner als 3 ist:\n    Zeige n.\nEnde."
        b = finde(code, "endlosschleife")
        self.assertEqual(len(b), 1)
        self.assertIn("n", b[0].meldung)

    def test_veraenderung_in_verschachtelter_stelle_zaehlt(self):
        code = ("Merke 0 als n.\nWiederhole solange n kleiner als 3 ist:\n    Wenn wahr ist:\n"
                "        Erhöhe n um 1.\n    Ende.\nEnde.")
        self.assertEqual(finde(code, "endlosschleife"), [])

    def test_veraenderung_durch_frage_und_liste(self):
        self.assertEqual(finde('Merke "" als a.\nWiederhole solange a gleich "" ist:\n    Frage "?" und merke die Antwort als a.\nEnde.',
                               "endlosschleife"), [])
        self.assertEqual(finde("Erstelle Liste namens L.\nWiederhole solange Länge von L kleiner als 3 ist:\n    Füge 1 zu L hinzu.\nEnde.",
                               "endlosschleife"), [])

    def test_aufgaben_koennten_globales_aendern(self):
        code = ("Merke 0 als n.\nDefiniere Aufgabe Weiter:\n    Setze n auf n plus 1.\nEnde.\n"
                "Wiederhole solange n kleiner als 3 ist:\n    Führe Weiter aus.\nEnde.")
        self.assertEqual(finde(code, "endlosschleife"), [])

    def test_immer_falsch(self):
        self.assertEqual(len(finde("Wiederhole solange falsch ist:\n    Zeige 1.\nEnde.", "schleife-laeuft-nie")), 1)

    def test_zaehle_die_nie_laeuft(self):
        self.assertEqual(len(finde("Zähle von 5 bis 1 mit i:\n    Zeige i.\nEnde.", "schleife-laeuft-nie")), 1)
        self.assertEqual(finde("Zähle von 5 bis 1 rückwärts mit i:\n    Zeige i.\nEnde.", "schleife-laeuft-nie"), [])
        self.assertEqual(len(finde("Zähle von 1 bis 5 rückwärts mit i:\n    Zeige i.\nEnde.", "schleife-laeuft-nie")), 1)
        self.assertEqual(finde("Zähle von 5 bis 1 in Schritten von -1 mit i:\n    Zeige i.\nEnde.", "schleife-laeuft-nie"), [])

    def test_endlose_rekursion(self):
        code = "Definiere Aufgabe F von x:\n    Gib F von x zurück.\nEnde.\nZeige F von 1."
        self.assertEqual(len(finde(code, "endlose-rekursion")), 1)
        ok = "Definiere Aufgabe F von x:\n    Wenn x kleiner als 1 ist, gib 0 zurück.\n    Gib F von (x minus 1) zurück.\nEnde.\nZeige F von 3."
        self.assertEqual(finde(ok, "endlose-rekursion"), [])


class Dinge(unittest.TestCase):
    KOPF = "Hund hat Name und Alter.\n"

    def test_unbekanntes_ding_mit_vorschlag(self):
        b = finde(self.KOPF + 'Erschaffe Hunt mit Name "x" und Alter 1 als h.\nZeige h.', "unbekanntes-ding")
        self.assertIn("Meintest du 'Hund'?", b[0].meldung)

    def test_fehlendes_und_ueberfluessiges_feld(self):
        self.assertEqual(len(finde(self.KOPF + 'Erschaffe Hund mit Name "x" als h.\nZeige h.', "fehlendes-feld")), 1)
        b = finde(self.KOPF + 'Erschaffe Hund mit Name "x" und Alter 1 und Farbe "b" als h.\nZeige h.', "unbekanntes-feld")
        self.assertIn("Farbe", b[0].meldung)

    def test_gebeugte_feldnamen_sind_ok(self):
        code = "Hund hat einen Namen und ein Alter.\nErschaffe Hund mit Name \"x\" und Alter 1 als h.\nZeige Namen von h."
        self.assertEqual([c for c in codes(code) if c.startswith(("unbekannt", "fehlend"))], [])

    def test_tippfehler_bei_aufgabe_wird_als_feld_erkannt(self):
        code = "Definiere Aufgabe Quadrat von x:\n    Gib x mal x zurück.\nEnde.\nZeige Quadrt von 5."
        b = finde(code, "unbekanntes-feld")
        self.assertEqual(len(b), 1)
        self.assertIn("Meintest du 'Quadrat'?", b[0].meldung)

    def test_vorhandenes_feld_ist_ruhig(self):
        code = self.KOPF + 'Erschaffe Hund mit Name "x" und Alter 1 als h.\nSetze Alter von h auf 2.\nZeige Alter von h.'
        self.assertEqual([c for c in codes(code) if c.startswith(("unbekannt", "fehlend"))], [])


class Aufgaben(unittest.TestCase):
    def test_ohne_rueckgabe_als_wert(self):
        code = "Definiere Aufgabe F:\n    Zeige 1.\nEnde.\nMerke F als x.\nZeige x."
        self.assertEqual(len(finde(code, "aufgabe-ohne-rueckgabe")), 1)

    def test_ohne_rueckgabe_per_fuehre_ist_ok(self):
        self.assertEqual(finde("Definiere Aufgabe F:\n    Zeige 1.\nEnde.\nFühre F aus.", "aufgabe-ohne-rueckgabe"), [])

    def test_unbenutzte_aufgabe_und_parameter(self):
        code = "Definiere Aufgabe F von x:\n    Zeige 1.\nEnde.\nDefiniere Aufgabe G:\n    Zeige 2.\nEnde.\nFühre F mit 1 aus."
        self.assertEqual(len(finde(code, "unbenutzter-parameter")), 1)
        b = finde(code, "unbenutzte-aufgabe")
        self.assertEqual((len(b), b[0].schwere), (1, "Hinweis"))

    def test_doppelte_definition(self):
        code = "Definiere Aufgabe F:\n    Zeige 1.\nEnde.\nDefiniere Aufgabe F:\n    Zeige 2.\nEnde.\nFühre F aus."
        self.assertEqual(len(finde(code, "doppelte-aufgabe")), 1)

    def test_lokale_variable_verdeckt_globale(self):
        code = ("Merke 0 als Zaehler.\nDefiniere Aufgabe Erhoehen:\n    Merke Zaehler plus 1 als Zaehler.\nEnde.\n"
                "Führe Erhoehen aus.\nZeige Zaehler.")
        b = finde(code, "lokale-verdeckt-globale")
        self.assertEqual((len(b), b[0].zeile, b[0].schwere), (1, 3, "Warnung"))
        self.assertIn("Setze Zaehler auf", b[0].meldung)

    def test_lokale_variable_ohne_lesen_vorher_ist_ok(self):
        code = ("Merke 0 als Zaehler.\nDefiniere Aufgabe F:\n    Merke 5 als Zaehler.\n    Zeige Zaehler.\nEnde.\n"
                "Führe F aus.\nZeige Zaehler.")
        self.assertEqual(finde(code, "lokale-verdeckt-globale"), [])

    def test_parameter_darf_globalen_namen_tragen(self):
        code = "Merke 0 als x.\nDefiniere Aufgabe F von x:\n    Merke x plus 1 als x.\n    Gib x zurück.\nEnde.\nZeige F von x."
        self.assertEqual(finde(code, "lokale-verdeckt-globale"), [])


class Rechnungen(unittest.TestCase):
    def test_division_durch_null(self):
        for code in ["Zeige 5 geteilt durch 0.", "Zeige den Rest von 5 geteilt durch 0.",
                     "Wenn 5 durch 0 teilbar ist, zeige 1."]:
            with self.subTest(code=code):
                self.assertEqual(len(finde(code, "division-durch-null")), 1)
        self.assertEqual(finde("Zeige 5 geteilt durch 2.", "division-durch-null"), [])

    def test_rechnen_mit_text(self):
        self.assertEqual(len(finde('Zeige "a" plus 1.', "rechnen-mit-text")), 1)
        self.assertEqual(len(finde('Zeige 2 mal "b".', "rechnen-mit-text")), 1)
        self.assertEqual(finde('Zeige "a" und 1.', "rechnen-mit-text"), [])

    def test_element_null(self):
        self.assertEqual(len(finde('Erstelle Liste namens L mit 1.\nZeige Element 0 von L.', "element-null")), 1)
        self.assertEqual(len(finde('Zeige Zeichen 0 bis 2 von "abc".', "element-null")), 1)
        self.assertEqual(finde('Erstelle Liste namens L mit 1.\nZeige Element 1 von L.', "element-null"), [])

    def test_zufall_grenzen(self):
        self.assertEqual(len(finde("Zeige Zufallszahl von 5 bis 1.", "zufall-grenzen")), 1)

    def test_konstante_bedingung(self):
        self.assertEqual(len(finde("Wenn wahr ist, zeige 1.", "konstante-bedingung")), 1)
        self.assertEqual(len(finde("Wenn 1 gleich 2 ist, zeige 1.", "konstante-bedingung")), 1)
        self.assertEqual(finde("Merke 1 als x.\nWenn x gleich 2 ist, zeige 1.", "konstante-bedingung"), [])

    def test_klammer_hinweis_bei_aufruf(self):
        code = "Definiere Aufgabe Quadrat von x:\n    Gib x mal x zurück.\nEnde.\nZeige Quadrat von 5 plus 1."
        b = finde(code, "klammern")
        self.assertEqual((len(b), b[0].schwere, b[0].zeile), (1, "Hinweis", 4))
        self.assertIn("Klammern", b[0].meldung)
        ok = "Definiere Aufgabe Quadrat von x:\n    Gib x mal x zurück.\nEnde.\nZeige Quadrat von (5 plus 1)."
        self.assertEqual(finde(ok, "klammern"), [])


class Hinweise(unittest.TestCase):
    def test_unbenutzte_variable(self):
        b = finde("Merke 1 als x.\nZeige 2.", "unbenutzte-variable")
        self.assertEqual((len(b), b[0].schwere), (1, "Hinweis"))

    def test_benutzung_ueber_listenbefehle_zaehlt(self):
        self.assertEqual(finde("Erstelle Liste namens L.\nFüge 1 zu L hinzu.", "unbenutzte-variable"), [])

    def test_schleifenvariablen_werden_nicht_bemaengelt(self):
        self.assertEqual(finde("Zähle von 1 bis 3 mit i:\n    Zeige 1.\nEnde.", "unbenutzte-variable"), [])

    def test_leere_bloecke(self):
        for code in ["Wenn wahr ist:\nEnde.", "Wiederhole 2 Mal:\nEnde.", "Definiere Aufgabe F:\nEnde.\nFühre F aus."]:
            with self.subTest(code=code):
                self.assertEqual(len(finde(code, "leerer-block")), 1)


class Syntax(unittest.TestCase):
    def test_syntaxfehler_wird_als_ein_befund_gemeldet(self):
        b = pruefe("Merke 5 als Zahl.\nZeigee Zahl.")
        self.assertEqual(len(b), 1)
        self.assertEqual((b[0].schwere, b[0].code, b[0].zeile, b[0].spalte), ("Fehler", "syntax", 2, 0))

    def test_leeres_programm(self):
        self.assertEqual(pruefe(""), [])
        self.assertEqual(pruefe("Anmerkung: nur ein Kommentar."), [])


class Ausgabe(unittest.TestCase):
    def test_ausgabeformat(self):
        code = "Merke 5 als Zahl.\nZeige Zahll."
        text = formatiere_befunde(pruefe(code), code, "t.klar")
        self.assertIn("Zeile 2 – Fehler: Ich kenne 'Zahll' nicht", text)
        self.assertIn("     2 | Zeige Zahll.", text)
        self.assertTrue(text.rstrip().endswith("Gefunden: 1 Fehler, 1 Hinweis."))

    def test_keine_probleme(self):
        code = 'Zeige "hallo".'
        self.assertTrue(formatiere_befunde(pruefe(code), code).endswith("Keine Probleme gefunden."))

    def test_sortierung_nach_zeile(self):
        code = "Zeige y.\nMerke 1 als a.\nZeige x."
        zeilen = [b.zeile for b in pruefe(code)]
        self.assertEqual(zeilen, sorted(zeilen))


class Kommandozeile(unittest.TestCase):
    def datei(self, inhalt):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p = Path(d.name) / "t.klar"
        p.write_text(inhalt, encoding="utf-8")
        return str(p)

    def cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(args))
        return code, out.getvalue()

    def test_exitcodes(self):
        self.assertEqual(self.cli("--pruefe", self.datei("Zeige 1."))[0], 0)
        code, out = self.cli("--pruefe", self.datei("Zeige x."))
        self.assertEqual(code, 1)
        self.assertIn("Fehler", out)

    def test_streng_zaehlt_auch_hinweise(self):
        p = self.datei("Merke 1 als x.\nZeige 2.")
        self.assertEqual(self.cli("--pruefe", p)[0], 0)
        self.assertEqual(self.cli("--pruefe", "--streng", p)[0], 1)

    def test_prueft_ohne_auszufuehren(self):
        code, out = self.cli("--pruefe", self.datei('Schreibe "x" in die Datei "sollte-nie-entstehen.txt".'))
        self.assertEqual(code, 0)
        self.assertFalse(Path("sollte-nie-entstehen.txt").exists())


class KeineFalschenAlarme(unittest.TestCase):
    def test_alle_mitgelieferten_programme_haben_keine_fehler_und_warnungen(self):
        for datei in sorted(list((WURZEL / "programme").glob("*.klar")) + list((WURZEL / "beispiele").glob("*.klar"))):
            if datei.name == "fehler.klar":              # enthält absichtlich Fehler
                continue
            with self.subTest(programm=datei.name):
                schlimm = [b for b in pruefe(datei.read_text(encoding="utf-8")) if b.schwere != "Hinweis"]
                self.assertEqual(schlimm, [], schlimm)

    def test_fehler_klar_wird_richtig_bemaengelt(self):
        code = (WURZEL / "beispiele" / "fehler.klar").read_text(encoding="utf-8")
        self.assertEqual(sorted(set(codes(code)) - {"unbenutzte-variable"}), ["division-durch-null", "unbekannter-name"])


if __name__ == "__main__":
    unittest.main()
