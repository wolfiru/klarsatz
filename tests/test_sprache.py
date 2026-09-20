"""Tests für Klarsatz:  python3 -m unittest -v test_klarsatz"""
import unittest
from pathlib import Path

from klarsatz import (Interpreter, KlarsatzFehler, LaufzeitFehler, LimitFehler,
                      SyntaxFehler, lexer)

WURZEL = Path(__file__).resolve().parent.parent
BEISPIELE = WURZEL / "beispiele"
PROGRAMME = WURZEL / "programme"


def laufe(code, eingaben=(), **kw):
    """Führt Code aus und gibt die Ausgabezeilen zurück."""
    aus, eing = [], iter(eingaben)
    Interpreter(ausgabe=aus.append, eingabe=lambda _p="": next(eing), **kw).lauf(code)
    return aus


class Ausrichten(unittest.TestCase):
    """Damit Tabellen untereinander stehen — 'Formatiert' setzt nur die Nachkommastellen."""

    def test_rechtsbuendig_fuellt_links_auf(self):
        self.assertEqual(laufe('Zeige Rechtsbündig von 42 auf 6 Zeichen und "|".'), ["    42|"])

    def test_linksbuendig_fuellt_rechts_auf(self):
        self.assertEqual(laufe('Zeige Linksbündig von "ab" auf 5 Zeichen und "|".'), ["ab   |"])

    def test_zu_kurze_breite_schneidet_nichts_ab(self):
        self.assertEqual(laufe('Zeige Rechtsbündig von "abcdef" auf 3 Zeichen.'), ["abcdef"])

    def test_zahlen_werden_deutsch_dargestellt(self):
        self.assertEqual(laufe("Zeige Rechtsbündig von 1.5 auf 5 Zeichen und \"|\"."), ["  1,5|"])

    def test_tabelle_steht_untereinander(self):
        zeilen = laufe("""
            Erstelle eine Liste namens Zahlen mit 7 und 42 und 1234.
            Für jede Zahl in Zahlen:
                Zeige Rechtsbündig von Zahl auf 6 Zeichen und "|".
            Ende.""")
        self.assertEqual([len(z) for z in zeilen], [7, 7, 7])

    def test_breite_muss_eine_ganze_zahl_sein(self):
        with self.assertRaisesRegex(LaufzeitFehler, "ganze"):
            laufe('Zeige Rechtsbündig von 1 auf "viel" Zeichen.')


class Winkelfunktionen(unittest.TestCase):
    """Rechnen in Grad — passend zu 'Drehe dich um 90 Grad'."""

    def test_sinus_kosinus_tangens(self):
        self.assertEqual(laufe("Zeige den Sinus von 30."), ["0,5"])
        self.assertEqual(laufe("Zeige den Kosinus von 60."), ["0,5"])
        self.assertEqual(laufe("Zeige den Tangens von 45."), ["1"])

    def test_rechenrauschen_wird_weggerundet(self):
        """Der Kosinus von 90 Grad ist 0 – nicht 6,1e-17."""
        self.assertEqual(laufe("Zeige den Kosinus von 90."), ["0"])
        self.assertEqual(laufe("Zeige den Sinus von 180."), ["0"])

    def test_cosinus_mit_c_geht_auch(self):
        self.assertEqual(laufe("Zeige den Cosinus von 60."), ["0,5"])

    def test_umkehrfunktionen_liefern_grad(self):
        self.assertEqual(laufe("Zeige den Arkussinus von 0.5."), ["30"])
        self.assertEqual(laufe("Zeige den Arkuskosinus von 1."), ["0"])
        self.assertEqual(laufe("Zeige den Arkustangens von 1."), ["45"])

    def test_negative_winkel(self):
        self.assertEqual(laufe("Zeige den Sinus von -30."), ["-0,5"])

    def test_tangens_von_90_ist_nicht_bestimmt(self):
        with self.assertRaisesRegex(LaufzeitFehler, "nicht bestimmt"):
            laufe("Zeige den Tangens von 90.")
        with self.assertRaisesRegex(LaufzeitFehler, "nicht bestimmt"):
            laufe("Zeige den Tangens von 270.")

    def test_arkussinus_braucht_werte_von_minus_eins_bis_eins(self):
        with self.assertRaisesRegex(LaufzeitFehler, "zwischen -1 und 1"):
            laufe("Zeige den Arkussinus von 2.")

    def test_braucht_eine_zahl(self):
        with self.assertRaisesRegex(LaufzeitFehler, "braucht eine Zahl"):
            laufe('Zeige den Sinus von "viel".')

    def test_im_zusammenspiel(self):
        """Der Faktor, mit dem man ein Zwölfeck um seine Mitte zeichnet."""
        self.assertEqual(laufe("Merke 1 geteilt durch (2 mal den Tangens von 15) als f.\n"
                               "Zeige Formatiert von f auf 3 Stellen."), ["1,866"])


class Grundlagen(unittest.TestCase):
    def test_hallo_welt(self):
        self.assertEqual(laufe('Zeige "Hallo Welt".'), ["Hallo Welt"])

    def test_artikel_und_gross_klein_egal(self):
        self.assertEqual(laufe("merke 5 als ZAHL.\nZEIGE die zahl."), ["5"])

    def test_fuellwoerter_werden_ueberlesen(self):
        """'dir', 'mir', 'dich' … lassen Befehle natürlicher klingen und bedeuten nichts."""
        self.assertEqual(laufe("Merke dir 5 als Zahl.\nZeige mir die Zahl."), ["5"])
        self.assertEqual(laufe("Merke 1 als a.\nBitte zeige a."), ["1"])
        self.assertEqual(laufe("Erstelle dir eine Liste namens L mit 1 und 2.\nZeige die Länge von L."), ["2"])
        # Gleichbedeutend mit der knappen Schreibweise
        self.assertEqual(laufe("Merke dir 3 als n.\nZeige uns n."), laufe("Merke 3 als n.\nZeige n."))

    def test_umlaute_und_ae_sind_gleich(self):
        self.assertEqual(laufe("Merke 1 als Groesse.\nZeige Größe."), ["1"])
        self.assertEqual(laufe("Zaehle von 1 bis 2 mit i:\nZeige i.\nEnde."), ["1", "2"])

    def test_kommentar(self):
        self.assertEqual(laufe("Anmerkung: nichts davon zählt.\nZeige 1. Anmerkung: auch das nicht\nZeige 2."),
                         ["1", "2"])

    def test_deutsche_anfuehrungszeichen(self):
        self.assertEqual(laufe("Zeige „Hallo“."), ["Hallo"])

    def test_zeige_klebt_mit_und_zusammen(self):
        self.assertEqual(laufe('Zeige "a" und 1 und "b".'), ["a1b"])

    def test_rechnen(self):
        code = """
        Zeige 2 plus 3 mal 4.
        Zeige (2 plus 3) mal 4.
        Zeige 7 geteilt durch 2.
        Zeige 8 geteilt durch 2.
        Zeige den Rest von 7 geteilt durch 2.
        Zeige die Wurzel von 16.
        Zeige die Wurzel von 2.
        Zeige 2 hoch 3 hoch 2.
        Zeige minus 5 plus 2.
        Zeige der Betrag von minus 3.
        """
        self.assertEqual(laufe(code), ["14", "20", "3,5", "4", "1", "4", "1,41421356237", "512", "-3", "3"])

    def test_konstante(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Konstante"):
            laufe("Merke für immer 3 als Pi.\nSetze Pi auf 4.")

    def test_setze_kennt_nur_bekanntes(self):
        with self.assertRaisesRegex(LaufzeitFehler, "noch nicht"):
            laufe("Setze x auf 1.")

    def test_frage(self):
        self.assertEqual(laufe('Frage "Alter?" und merke die Antwort als Alter.\nZeige Alter plus 1.', ["41"]),
                         ["42"])


class Bedingungen(unittest.TestCase):
    def test_blockform_mit_sonst_wenn(self):
        code = """
        Zähle von 9 bis 11 mit z:
            Wenn z größer als 10 ist:
                Zeige "groß".
            Sonst wenn z gleich 10 ist:
                Zeige "zehn".
            Sonst:
                Zeige "klein".
            Ende.
        Ende.
        """
        self.assertEqual(laufe(code), ["klein", "zehn", "groß"])

    def test_fizzbuzz_kurzform(self):
        aus = laufe((BEISPIELE / "fizzbuzz.klar").read_text(encoding="utf-8"))
        self.assertEqual(len(aus), 100)
        self.assertEqual(aus[:15], ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
                                     "11", "Fizz", "13", "14", "FizzBuzz"])
        self.assertEqual(aus[99], "Buzz")

    def test_logik(self):
        code = """
        Merke 5 als a.
        Wenn a größer als 1 und a kleiner als 10 ist, zeige "innen".
        Wenn a kleiner als 1 oder a größer als 4 ist, zeige "oder".
        Wenn nicht a gleich 5 ist, zeige "falsch".
        Sonst zeige "richtig".
        Wenn a nicht gleich 6 ist, zeige "ungleich".
        Wenn a nicht durch 2 teilbar ist, zeige "ungerade".
        Wenn a mindestens 5 ist, zeige "mindestens".
        Wenn a höchstens 4 ist, zeige "zu klein".
        Sonst zeige "nicht höchstens".
        """
        self.assertEqual(laufe(code), ["innen", "oder", "richtig", "ungleich", "ungerade",
                                       "mindestens", "nicht höchstens"])

    def test_ist_vor_und_nach_dem_vergleich(self):
        self.assertEqual(laufe("Wenn 3 ist größer als 2, zeige 1.\nWenn 3 größer als 2 ist, zeige 2."), ["1", "2"])

    def test_wahrheitswerte(self):
        self.assertEqual(laufe("Merke wahr als fertig.\nWenn fertig ist, zeige 1.\nWenn nicht fertig ist, zeige 2."),
                         ["1"])

    def test_text_vergleich_deutsch(self):
        self.assertEqual(laufe('Wenn "Äpfel" kleiner als "Birnen" ist, zeige "ja".'), ["ja"])

    def test_typfehler_beim_vergleich(self):
        with self.assertRaisesRegex(LaufzeitFehler, "nicht der Größe nach"):
            laufe('Wenn "a" größer als 1 ist, zeige 1.')

    def test_kurzform_sonst_gehoert_zum_aeusseren_blockwenn(self):
        code = """
        Wenn 1 gleich 2 ist:
            Wenn 3 gleich 3 ist, zeige "innen".
        Sonst:
            Zeige "außen-sonst".
        Ende.
        """
        self.assertEqual(laufe(code), ["außen-sonst"])


class Schleifen(unittest.TestCase):
    def test_wiederhole_mal(self):
        self.assertEqual(laufe('Wiederhole 3 Mal:\n  Zeige "x".\nEnde.'), ["x"] * 3)

    def test_mal_als_rechenzeichen_bleibt_moeglich(self):
        self.assertEqual(laufe('Wiederhole 2 mal 2 Mal:\n  Zeige "x".\nEnde.'), ["x"] * 4)

    def test_solange(self):
        self.assertEqual(laufe("Merke 0 als n.\nWiederhole solange n kleiner als 3 ist:\n"
                               "  Erhöhe n um 1.\nEnde.\nZeige n."), ["3"])

    def test_zaehle_vorwaerts_rueckwaerts_schritte(self):
        self.assertEqual(laufe("Zähle von 1 bis 3 mit i:\nZeige i.\nEnde."), ["1", "2", "3"])
        self.assertEqual(laufe("Zähle von 3 bis 1 rückwärts mit i:\nZeige i.\nEnde."), ["3", "2", "1"])
        self.assertEqual(laufe("Zähle von 3 bis 1 mit i:\nZeige i.\nEnde."), [])          # ohne 'rückwärts' nichts
        self.assertEqual(laufe("Zähle von 1 bis 0 mit i:\nZeige i.\nEnde."), [])          # leere Bereiche bleiben leer
        self.assertEqual(laufe("Zähle von 0 bis 10 in Schritten von 5 mit i:\nZeige i.\nEnde."), ["0", "5", "10"])

    def test_abbruch_und_weiter(self):
        code = "Zähle von 1 bis 10 mit i:\nWenn i gleich 2 ist, mach weiter.\nWenn i gleich 4 ist, höre auf.\nZeige i.\nEnde."
        self.assertEqual(laufe(code), ["1", "3"])

    def test_fuer_jedes_liste_und_text(self):
        self.assertEqual(laufe('Erstelle Liste namens L mit 1 und 2.\nFür jedes x in L:\nZeige x.\nEnde.'), ["1", "2"])
        self.assertEqual(laufe('Für jedes c in "ab":\nZeige c.\nEnde.'), ["a", "b"])

    def test_endlosschleife_wird_gestoppt(self):
        with self.assertRaises(LimitFehler):
            laufe("Wiederhole solange wahr ist:\nEnde.", max_schritte=1000)

    def test_limit_kann_nicht_abgefangen_werden(self):
        with self.assertRaises(LimitFehler):
            laufe("Versuche:\n  Wiederhole solange wahr ist:\n  Ende.\nBei Fehler:\n  Zeige 1.\nEnde.",
                  max_schritte=1000)


class Listen(unittest.TestCase):
    def test_listenbefehle(self):
        code = """
        Erstelle eine Liste namens L.
        Füge 3 zur L hinzu.
        Füge 1 zur L hinzu.
        Füge 2 zur L hinzu.
        Sortiere L.
        Zeige L.
        Sortiere L absteigend.
        Zeige L.
        Entferne 3 aus L.
        Zeige das erste Element von L und das letzte Element von L und die Länge von L.
        Zeige Element 2 von L.
        """
        self.assertEqual(laufe(code), ["[1, 2, 3]", "[3, 2, 1]", "212", "1"])

    def test_grenzen_werden_geprueft(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Element 4 gibt es nicht"):
            laufe("Erstelle Liste namens L mit 1 und 2.\nZeige Element 4 von L.")
        with self.assertRaisesRegex(LaufzeitFehler, "Element 0 gibt es nicht"):
            laufe("Erstelle Liste namens L mit 1.\nZeige Element 0 von L.")
        with self.assertRaisesRegex(LaufzeitFehler, "leer"):
            laufe("Erstelle Liste namens L.\nZeige das erste Element von L.")

    def test_entfernen_was_fehlt(self):
        with self.assertRaisesRegex(LaufzeitFehler, "steht nicht in"):
            laufe("Erstelle Liste namens L.\nEntferne 1 aus L.")

    def test_deutsche_sortierung(self):
        self.assertEqual(laufe('Erstelle Liste namens L mit "Zebra" und "Äpfel" und "Birne".\nSortiere L.\nZeige L.'),
                         ["[Äpfel, Birne, Zebra]"])


class Aufgaben(unittest.TestCase):
    def test_aufgaben_beispiel(self):
        aus = laufe((BEISPIELE / "aufgaben.klar").read_text(encoding="utf-8"))
        self.assertEqual(aus[:3], ["Hallo, Wolfgang!", "5 zum Quadrat: 25", "3 + 4 = 7"])
        self.assertEqual(aus[-1], "10! = 3628800")

    def test_aufruf_vor_definition(self):
        self.assertEqual(laufe("Zeige Doppelt von 4.\nDefiniere Aufgabe Doppelt von x:\nGib x mal 2 zurück.\nEnde."),
                         ["8"])

    def test_aufgabe_ohne_parameter(self):
        self.assertEqual(laufe('Definiere Aufgabe Gruss:\nZeige "hi".\nEnde.\nFühre Gruss aus.'), ["hi"])

    def test_bereiche_lokal(self):
        code = "Definiere Aufgabe F von x:\nMerke 99 als y.\nGib x zurück.\nEnde.\nZeige F von 1.\nZeige y."
        with self.assertRaisesRegex(LaufzeitFehler, "kenne 'y' nicht"):
            laufe(code)

    def test_globale_sind_lesbar(self):
        self.assertEqual(laufe("Merke 10 als g.\nDefiniere Aufgabe F von x:\nGib x plus g zurück.\nEnde.\nZeige F von 1."),
                         ["11"])

    def test_endlose_rekursion_wird_gemeldet(self):
        with self.assertRaisesRegex(LaufzeitFehler, "verschachtelte Aufgaben"):
            laufe("Definiere Aufgabe F von x:\nGib F von x zurück.\nEnde.\nZeige F von 1.")

    def test_gib_ausserhalb(self):
        with self.assertRaisesRegex(LaufzeitFehler, "innerhalb einer Aufgabe"):
            laufe("Gib 1 zurück.")


class Dinge(unittest.TestCase):
    def test_strukturen_und_gebeugte_feldnamen(self):
        code = """
        Ein Hund hat einen Namen und ein Alter.
        Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Waldi.
        Zeige den Namen von Waldi.
        Setze Alter von Waldi auf 6.
        Erhöhe das Alter von Waldi um 1.
        Zeige Alter von Waldi.
        """
        self.assertEqual(laufe(code), ["Rocco", "7"])

    def test_fehlendes_feld_beim_erschaffen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "fehlt noch: Alter"):
            laufe('Hund hat Name und Alter.\nErschaffe Hund mit Name "x" als h.')

    def test_falsches_feld(self):
        with self.assertRaisesRegex(LaufzeitFehler, "kein Feld 'Farbe'"):
            laufe('Hund hat Name.\nErschaffe Hund mit Name "x" als h.\nZeige Farbe von h.')


class Fehlerbehandlung(unittest.TestCase):
    def test_versuche_und_fehlermeldung(self):
        code = "Versuche:\n  Zeige 1 geteilt durch 0.\nBei Fehler:\n  Zeige Fehlermeldung.\nEnde."
        self.assertEqual(laufe(code), ["Durch null kann man nicht teilen."])

    def test_text_plus_zahl_hat_hilfreiche_meldung(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Verbinde"):
            laufe('Zeige "a" plus 1.')

    def test_zusicherung(self):
        laufe("Stelle sicher, dass 1 kleiner als 2 ist.")
        with self.assertRaisesRegex(LaufzeitFehler, "Zusicherung"):
            laufe("Stelle sicher, dass 2 kleiner als 1 ist.")

    def test_variablen_tippfehler_bekommt_vorschlag(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Meintest du 'Summe'"):
            laufe("Merke 1 als Summe.\nZeige Summee.")

    def test_fehler_haben_zeilennummer(self):
        try:
            laufe("Zeige 1.\nZeige 2.\nZeige x.")
        except LaufzeitFehler as e:
            self.assertEqual(e.zeile, 3)


class Dateien(unittest.TestCase):
    def test_dateien_lesen_schreiben(self):
        import tempfile
        from klarsatz.dateisystem import OrdnerDateisystem
        with tempfile.TemporaryDirectory() as d:
            aus = laufe('Schreibe "Hallo" in die Datei "t.txt".\nLies die Datei "t.txt" als Inhalt.\nZeige Inhalt.',
                        dateisystem=OrdnerDateisystem(d))
        self.assertEqual(aus, ["Hallo"])

    def test_dateien_abschaltbar(self):
        with self.assertRaisesRegex(LaufzeitFehler, "abgeschaltet"):
            laufe('Lies die Datei "x.txt" als Inhalt.', dateien=False)

    def test_fehlende_datei(self):
        with self.assertRaisesRegex(LaufzeitFehler, "gibt es nicht"):
            laufe('Lies die Datei "diese-datei-gibt-es-nicht.txt" als Inhalt.')


class Syntaxfehler(unittest.TestCase):
    def fehler(self, code):
        with self.assertRaises(SyntaxFehler) as cm:
            laufe(code)
        return cm.exception

    def test_tippfehler_im_verb(self):
        e = self.fehler("Zeigee 1.")
        self.assertIn("Meintest du 'Zeige'", e.meldung)

    def test_fehlender_punkt_meldet_richtige_zeile(self):
        e = self.fehler("Zeige 1\nZeige 2.")
        self.assertIn("Punkt", e.meldung)
        self.assertEqual(e.zeile, 1)

    def test_block_nicht_geschlossen(self):
        e = self.fehler("Wiederhole 2 Mal:\n  Zeige 1.")
        self.assertIn("Ende", e.meldung)
        self.assertEqual(e.zeile, 1)

    def test_sonst_ohne_wenn(self):
        self.assertIn("ohne passendes", self.fehler("Sonst:\nEnde.").meldung)

    def test_unbekanntes_zeichen(self):
        self.assertIn("kenne ich nicht", self.fehler("Zeige 1 + 2.").meldung)

    def test_text_nicht_geschlossen(self):
        self.assertIn("Anführungszeichen", self.fehler('Zeige "abc.').meldung)

    def test_aufgabe_ohne_fuehre(self):
        e = self.fehler("Definiere Aufgabe F:\nZeige 1.\nEnde.\nF.")
        self.assertIn("Führe F", e.meldung)


class NeueBefehle(unittest.TestCase):
    def test_zufallszahl_ist_reproduzierbar_und_im_bereich(self):
        import random
        code = "Zähle von 1 bis 200 mit i:\nZeige Zufallszahl von 3 bis 7.\nEnde."
        a = laufe(code, zufall=random.Random(5))
        b = laufe(code, zufall=random.Random(5))
        self.assertEqual(a, b)
        self.assertEqual(set(a), {"3", "4", "5", "6", "7"})

    def test_zufallszahl_fehler(self):
        with self.assertRaisesRegex(LaufzeitFehler, "nicht größer"):
            laufe("Zeige Zufallszahl von 5 bis 1.")
        with self.assertRaisesRegex(LaufzeitFehler, "ganze Zahlen"):
            laufe('Zeige Zufallszahl von 1 bis "x".')

    def test_zufallszahl_mit_berechneter_obergrenze(self):
        code = ("Erstelle Liste namens L mit 1 und 2 und 3.\n"
                "Merke Zufallszahl von 1 bis Länge von L als Nr.\nZeige Element Nr von L.")
        self.assertIn(laufe(code)[0], ("1", "2", "3"))

    def test_runden(self):
        code = ("Zeige Abgerundet von 2.7 und Abgerundet von minus 2.1.\n"
                "Zeige Aufgerundet von 2.1 und Aufgerundet von 5.\n"
                "Zeige Gerundet von 2.5 und Gerundet von 2.4.")
        self.assertEqual(laufe(code), ["2-3", "35", "32"])

    def test_formatiert(self):
        code = ('Zeige Formatiert von 3.14159 auf 2 Stellen.\nZeige Formatiert von 5 auf 2 Stellen.\n'
                'Zeige Formatiert von 2.5 auf 0 Stellen.\nZeige Formatiert von minus 0.001 auf 2 Stellen.')
        self.assertEqual(laufe(code), ["3,14", "5,00", "3", "0,00"])       # kaufmännisch: 2,5 -> 3

    def test_teile_text(self):
        code = 'Teile "a;b;;c" bei ";" zu Teile.\nZeige Teile.\nZeige Länge von Teile.'
        self.assertEqual(laufe(code), ["[a, b, , c]", "4"])
        with self.assertRaisesRegex(LaufzeitFehler, "nicht leer"):
            laufe('Teile "abc" bei "" zu T.')
        with self.assertRaisesRegex(LaufzeitFehler, "zwei Texte"):
            laufe('Teile 5 bei "," zu T.')

    def test_typ_tests(self):
        code = """
        Merke 5 als a.  Merke "x" als b.  Erstelle Liste namens c.
        Wenn a eine Zahl ist, zeige 1.
        Wenn b keine Zahl ist, zeige 2.
        Wenn b ein Text ist, zeige 3.
        Wenn c eine Liste ist, zeige 4.
        Wenn a keine Liste ist und b keine Liste ist, zeige 5.
        Wenn nicht a eine Zahl ist, zeige 6.
        Wenn a keine Zahl ist, zeige 7.
        """
        self.assertEqual(laufe(code), ["1", "2", "3", "4", "5"])

    def test_keine_ohne_typ_ist_ein_klarer_fehler(self):
        with self.assertRaisesRegex(SyntaxFehler, "Nach 'keine'"):
            laufe("Merke 1 als a.\nWenn a keine gleich 1 ist, zeige 1.")

    def test_enthaelt(self):
        code = """
        Erstelle Liste namens L mit 1 und "a".
        Wenn L enthält 1, zeige "eins".
        Wenn L enthält "a" ist, zeige "a".
        Wenn nicht L enthält 2 ist, zeige "keine zwei".
        Wenn "Hallo Welt" enthält "lo W", zeige "text".
        Wenn "Hallo" enthält "x", zeige "nein".
        Sonst zeige "kein x".
        """
        self.assertEqual(laufe(code), ["eins", "a", "keine zwei", "text", "kein x"])
        with self.assertRaisesRegex(LaufzeitFehler, "enthält"):
            laufe('Wenn 5 enthält 5, zeige 1.')
        with self.assertRaisesRegex(LaufzeitFehler, "enthält"):
            laufe('Wenn "abc" enthält 5, zeige 1.')

    def test_enthaelt_unterscheidet_wahr_und_eins(self):
        self.assertEqual(laufe("Erstelle Liste namens L mit 1.\nWenn L enthält wahr, zeige 1.\nSonst zeige 2."), ["2"])

    def test_zaehle_rueckwaerts_und_leere_bereiche(self):
        self.assertEqual(laufe("Zähle von 3 bis 1 rückwärts mit i:\nZeige i.\nEnde."), ["3", "2", "1"])
        self.assertEqual(laufe("Zähle von 3 bis 1 abwärts mit i:\nZeige i.\nEnde."), ["3", "2", "1"])
        self.assertEqual(laufe("Zähle von 10 bis 0 in Schritten von minus 5 mit i:\nZeige i.\nEnde."), ["10", "5", "0"])
        self.assertEqual(laufe("Erstelle Liste namens L.\nZähle von 1 bis Länge von L mit i:\nZeige i.\nEnde."), [])

    def test_element_mit_namen_und_klammern_als_nummer(self):
        code = ('Erstelle Liste namens L mit "a" und "b" und "c".\nMerke 2 als Nr.\n'
                'Zeige Element Nr von L.\nZeige Element (Nr plus 1) von L.')
        self.assertEqual(laufe(code), ["b", "c"])

    def test_feld_mit_von_bleibt_moeglich(self):
        code = 'Hund hat Alter.\nErschaffe Hund mit Alter 3 als h.\nZeige Alter von h.'
        self.assertEqual(laufe(code), ["3"])


class TextFunktionen(unittest.TestCase):
    def test_klein_und_grossbuchstaben(self):
        self.assertEqual(laufe('Zeige Kleinbuchstaben von "HalLo" und Großbuchstaben von "HalLo".'), ["halloHALLO"])

    def test_nur_fuer_texte(self):
        with self.assertRaisesRegex(LaufzeitFehler, "braucht einen Text"):
            laufe("Zeige Kleinbuchstaben von 5.")


class Zahlenraten(unittest.TestCase):
    """Der Computer errät die Zahl; ein simulierter Spieler antwortet über 'Frage'."""
    QUELLE = (PROGRAMME / "08_zahlenraten_computer_raet.klar").read_text(encoding="utf-8")

    @staticmethod
    def spieler(geheime_zahlen, antworten=None, **kw):
        """Simuliert den Menschen. geheime_zahlen: eine Zahl pro Runde. antworten: Wörter für h/n/r."""
        import re
        wort = {"h": "h", "n": "n", "r": "r"}
        wort.update(antworten or {})
        runden = list(geheime_zahlen)
        protokoll = []

        def eingabe(prompt=""):
            protokoll.append(prompt)
            m = re.search(r"die (\d+)\?", prompt)
            if m:
                tipp, geheim = int(m.group(1)), runden[0]
                return wort["r" if tipp == geheim else "h" if tipp < geheim else "n"]
            runden.pop(0)                                # 'Noch eine Runde?'
            return "j" if runden else "n"

        aus = []
        Interpreter(ausgabe=aus.append, eingabe=eingabe, **kw).lauf(Zahlenraten.QUELLE)
        return aus, protokoll

    def test_alle_zahlen_von_1_bis_10_werden_in_hoechstens_4_tipps_erraten(self):
        for z in range(1, 11):
            with self.subTest(zahl=z):
                aus, prot = self.spieler([z])
                tipps = [p for p in prot if p.startswith("Tipp ")]
                self.assertLessEqual(len(tipps), 4)
                self.assertTrue(any(f"Deine Zahl ist die {z} " in zeile for zeile in aus), aus)

    def test_mehrere_runden(self):
        aus, _ = self.spieler([3, 10, 1])
        erfolge = [z for z in aus if z.startswith("Geschafft")]
        self.assertEqual(len(erfolge), 3)
        self.assertIn("Deine Zahl ist die 10 ", erfolge[1])
        self.assertEqual(aus[-1], "Danke fürs Spielen!")

    def test_antworten_ganze_woerter_und_grossschreibung(self):
        aus, _ = self.spieler([7], {"h": "Höher", "n": "NIEDRIGER", "r": "Richtig!"})
        self.assertTrue(any("Deine Zahl ist die 7 " in z for z in aus))

    def test_unverstandene_eingaben_werden_erneut_gefragt(self):
        # Auf Tipp 1 (die 5) kommen erst Zahl, leere Eingabe und Unsinn, dann "n"; Tipp 2 (die 2) stimmt.
        antworten = iter(["5", "", "vielleicht", "n", "r", "n"])
        protokoll = []

        def eingabe(prompt=""):
            protokoll.append(prompt)
            return next(antworten)

        aus = []
        Interpreter(ausgabe=aus.append, eingabe=eingabe).lauf(self.QUELLE)
        self.assertEqual(aus.count("Das habe ich nicht verstanden. Bitte antworte mit h, n oder r."), 3)
        self.assertTrue(any("Deine Zahl ist die 2 " in z for z in aus), aus)

    def test_schummeln_wird_erkannt(self):
        antworten = iter(["h"] * 20 + ["n"])
        aus = []
        Interpreter(ausgabe=aus.append, eingabe=lambda _p="": next(antworten)).lauf(self.QUELLE)
        self.assertTrue(any("geschummelt" in z for z in aus), aus)

    def test_zahl_als_antwort_wird_nicht_zum_absturz(self):
        antworten = iter(["42", "r", "n"])
        aus = []
        Interpreter(ausgabe=aus.append, eingabe=lambda _p="": next(antworten)).lauf(self.QUELLE)
        self.assertTrue(any("Deine Zahl ist die 5 " in z for z in aus))


class Beispieldateien(unittest.TestCase):
    def test_alle_beispiele_laufen(self):
        for datei in sorted(BEISPIELE.glob("*.klar")):
            with self.subTest(datei=datei.name):
                try:
                    laufe(datei.read_text(encoding="utf-8"))
                except KlarsatzFehler as e:
                    # fehler.klar endet absichtlich mit einer verletzten Zusicherung
                    self.assertEqual(datei.name, "fehler.klar")
                    self.assertIn("Zusicherung", e.meldung)



class FuerJedenJedeJedes(unittest.TestCase):
    """„Für jedes Ort" ist falsches Deutsch — die Sprache soll das nicht erzwingen."""

    def laufe(self, quelle):
        ausgabe = []
        Interpreter(ausgabe=ausgabe.append).lauf(quelle)
        return ausgabe

    def test_alle_drei_formen_tun_dasselbe(self):
        for wort in ("jeden", "jede", "jedes"):
            with self.subTest(form=wort):
                self.assertEqual(
                    self.laufe(f'Erstelle eine Liste namens L mit "a" und "b".\n'
                               f'Für {wort} Stueck in L:\n    Zeige Stueck.\nEnde.'),
                    ["a", "b"])

    def test_die_meldung_nennt_alle_drei(self):
        with self.assertRaisesRegex(SyntaxFehler, "'jeden', 'jede' oder 'jedes'"):
            self.laufe("Für alles X in L:\n    Zeige X.\nEnde.")

    def test_die_programme_benutzen_die_passende_form(self):
        """Wer die Beispiele liest, soll richtiges Deutsch lesen."""
        import re
        from pathlib import Path
        artikel = {"Ort": "jeden", "Strecke": "jede", "Zeile": "jede", "Note": "jede",
                   "Weg": "jeden", "Artikel": "jeden", "Eintrag": "jeden", "Name": "jeden",
                   "Hund": "jeden", "Frucht": "jede", "Farbe": "jede", "Wert": "jeden",
                   "Ton": "jeden"}
        wurzel = Path(__file__).resolve().parent.parent
        dateien = list((wurzel / "programme").glob("*.klar")) + list((wurzel / "beispiele").glob("*.klar"))
        for datei in dateien:
            for treffer in re.finditer(r"Für (jede[nrs]?) ([A-ZÄÖÜ][A-Za-zÄÖÜäöüß]*)",
                                       datei.read_text(encoding="utf-8")):
                erwartet = artikel.get(treffer.group(2))
                if erwartet:
                    with self.subTest(datei=datei.name, stelle=treffer.group(0)):
                        self.assertEqual(treffer.group(1), erwartet)


if __name__ == "__main__":
    unittest.main()
