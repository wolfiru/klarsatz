"""Neue Sprachbefehle: negative Zahlen, Tabellen, Textwerkzeuge, Listenwerkzeuge, Klammern in Bedingungen."""
import random
import unittest

from klarsatz import Interpreter, KlarsatzFehler, LaufzeitFehler, SyntaxFehler


def laufe(code, eingaben=(), seed=None, **kw):
    aus, eing = [], iter(eingaben)
    z = random.Random(seed) if seed is not None else None
    Interpreter(ausgabe=aus.append, eingabe=lambda _p="": next(eing), zufall=z, **kw).lauf(code)
    return aus


class NegativeZahlen(unittest.TestCase):
    def test_literale(self):
        self.assertEqual(laufe("Zeige -5 plus 2 und -1.5.\nZeige 2 hoch -1.\nMerke -3 als x.\nZeige x mal -2."),
                         ["-3-1,5", "0,5", "6"])

    def test_minus_zeichen_zum_rechnen_gibt_hilfreichen_fehler(self):
        with self.assertRaisesRegex(SyntaxFehler, "minus"):
            laufe("Zeige 3 - 2.")
        with self.assertRaisesRegex(SyntaxFehler, "'minus'"):
            laufe("Zeige 3 -2.")


class Tabellen(unittest.TestCase):
    def test_grundlagen(self):
        code = """
        Erstelle eine Tabelle namens Preise.
        Trage "Apfel" mit 3 in Preise ein.
        Trage "Birne" mit 2 in Preise ein.
        Trage "Apfel" mit 4 in Preise ein.
        Zeige Wert für "Apfel" in Preise.
        Zeige Länge von Preise.
        Zeige Preise.
        Wenn Preise enthält "Birne", zeige "hat Birne".
        Wenn nicht Preise enthält "Kiwi" ist, zeige "keine Kiwi".
        Entferne "Birne" aus Preise.
        Zeige Preise.
        """
        self.assertEqual(laufe(code), ["4", "2", "{Apfel: 4, Birne: 2}", "hat Birne", "keine Kiwi", "{Apfel: 4}"])

    def test_startwerte_und_schluessel_als_zahl(self):
        code = 'Erstelle Tabelle namens T mit "a" als 1 und 2 als "zwei".\nZeige T.\nZeige Wert für 2 in T.'
        self.assertEqual(laufe(code), ["{a: 1, 2: zwei}", "zwei"])

    def test_wert_fuer_mit_variablen(self):
        code = ('Erstelle Tabelle namens T mit "x" als 10.\nMerke "x" als Schluessel.\n'
                'Zeige Wert für Schluessel in T.\nMerke T als Kopie_von_T.')
        self.assertEqual(laufe(code), ["10"])

    def test_durchgehen_ergibt_die_schluessel_in_der_reihenfolge(self):
        code = ('Erstelle Tabelle namens T mit "b" als 2 und "a" als 1.\n'
                'Für jedes S in T:\nZeige S und "=" und Wert für S in T.\nEnde.')
        self.assertEqual(laufe(code), ["b=2", "a=1"])

    def test_fehlender_eintrag(self):
        with self.assertRaisesRegex(LaufzeitFehler, "keinen Eintrag für „?x"):
            laufe('Erstelle Tabelle namens T.\nZeige Wert für "x" in T.')
        with self.assertRaisesRegex(LaufzeitFehler, "keinen Eintrag"):
            laufe('Erstelle Tabelle namens T.\nEntferne "x" aus T.')

    def test_falsche_arten(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Tabelle, keine Liste"):
            laufe("Erstelle Tabelle namens T.\nFüge 1 zu T hinzu.")
        with self.assertRaisesRegex(LaufzeitFehler, "brauche ich eine Tabelle"):
            laufe("Erstelle Liste namens L.\nTrage 1 mit 2 in L ein.")
        with self.assertRaisesRegex(LaufzeitFehler, "nur Texte und Zahlen"):
            laufe("Erstelle Tabelle namens T.\nErstelle Liste namens L.\nTrage L mit 1 in T ein.")
        with self.assertRaisesRegex(LaufzeitFehler, "nur Texte und Zahlen"):
            laufe("Erstelle Tabelle namens T.\nTrage wahr mit 1 in T ein.")

    def test_typtest_und_kopie(self):
        code = ('Erstelle Tabelle namens T mit "a" als 1.\nWenn T eine Tabelle ist, zeige "ja".\n'
                'Wenn T keine Liste ist, zeige "keine Liste".\nKopiere T als U.\nTrage "b" mit 2 in U ein.\n'
                'Zeige T.\nZeige U.')
        self.assertEqual(laufe(code), ["ja", "keine Liste", "{a: 1}", "{a: 1, b: 2}"])

    def test_werte_duerfen_listen_sein_und_zaehlen(self):
        code = ('Erstelle Tabelle namens Zaehler.\nErstelle Liste namens Woerter mit "a" und "b" und "a" und "c" und "a".\n'
                'Für jedes W in Woerter:\n'
                '    Wenn Zaehler enthält W, trage W mit (Wert für W in Zaehler) plus 1 in Zaehler ein.\n'
                '    Sonst trage W mit 1 in Zaehler ein.\nEnde.\nZeige Zaehler.')
        self.assertEqual(laufe(code), ["{a: 3, b: 1, c: 1}"])

    def test_tabelle_wird_nicht_zu_gross(self):
        from klarsatz.grenzen import Grenzen
        with self.assertRaisesRegex(LaufzeitFehler, "zu groß"):
            laufe('Erstelle Tabelle namens T.\nZähle von 1 bis 100 mit i:\nTrage i mit 0 in T ein.\nEnde.',
                  grenzen=Grenzen(liste=10))


class Listenwerkzeuge(unittest.TestCase):
    def test_kopiere_ist_unabhaengig(self):
        code = "Erstelle Liste namens A mit 1.\nKopiere A als B.\nFüge 2 zu B hinzu.\nZeige A.\nZeige B."
        self.assertEqual(laufe(code), ["[1]", "[1, 2]"])
        with self.assertRaisesRegex(LaufzeitFehler, "Listen und Tabellen"):
            laufe("Kopiere 5 als X.")

    def test_verkettet(self):
        code = ('Erstelle Liste namens L mit "a" und 2 und wahr.\nZeige Verkettet von L mit ", ".\n'
                'Zeige Verkettet von L mit "".\nErstelle Liste namens Leer.\nZeige "[" und Verkettet von Leer mit "-" und "]".')
        self.assertEqual(laufe(code), ["a, 2, wahr", "a2wahr", "[]"])
        with self.assertRaisesRegex(LaufzeitFehler, "Liste und einen Text"):
            laufe('Zeige Verkettet von "abc" mit ",".')

    def test_verkettet_und_grenzen(self):
        from klarsatz.grenzen import Grenzen
        with self.assertRaisesRegex(LaufzeitFehler, "zu lang"):
            laufe('Erstelle Liste namens L mit "aaaa" und "bbbb" und "cccc".\nZeige Verkettet von L mit ", ".',
                  grenzen=Grenzen(text=10))

    def test_entferne_nach_position(self):
        code = ('Erstelle Liste namens L mit "a" und "b" und "c" und "d" und "e".\n'
                'Entferne Element 2 aus L.\nZeige L.\nEntferne das erste Element aus L.\nZeige L.\n'
                'Entferne das letzte Element aus L.\nZeige L.\nMerke 1 als Nr.\nEntferne Element Nr aus L.\nZeige L.\n'
                'Entferne Element (Nr plus 0) aus L.\nZeige L.')
        self.assertEqual(laufe(code), ["[a, c, d, e]", "[c, d, e]", "[c, d]", "[d]", "[]"])

    def test_entferne_fehler(self):
        for code, muster in [("Erstelle Liste namens L.\nEntferne das erste Element aus L.", "ist leer"),
                             ("Erstelle Liste namens L mit 1.\nEntferne Element 2 aus L.", "Element 2 gibt es nicht"),
                             ("Erstelle Liste namens L mit 1.\nEntferne Element 0 aus L.", "Element 0 gibt es nicht"),
                             ("Erstelle Liste namens L mit 1.\nEntferne Element 1.5 aus L.", "ganze Zahl")]:
            with self.subTest(code=code), self.assertRaisesRegex(LaufzeitFehler, muster):
                laufe(code)

    def test_entferne_variable_namens_element_bleibt_moeglich(self):
        code = 'Erstelle Liste namens L mit "x" und "y".\nMerke "x" als Element.\nEntferne Element aus L.\nZeige L.'
        self.assertEqual(laufe(code), ["[y]"])

    def test_entfernen_verwechselt_wahr_nicht_mit_eins(self):
        self.assertEqual(laufe("Erstelle Liste namens L mit 1 und wahr.\nEntferne wahr aus L.\nZeige L."), ["[1]"])

    def test_ausschnitte(self):
        code = ('Zeige Zeichen 2 bis 4 von "Hallo".\nMerke 1 als a.\nMerke 3 als b.\nZeige Zeichen a bis b von "Hallo".\n'
                'Zeige Zeichen (a plus 1) bis 5 von "Hallo".\n'
                'Erstelle Liste namens L mit 1 und 2 und 3 und 4.\nZeige Elemente 2 bis 3 von L.')
        self.assertEqual(laufe(code), ["all", "Hal", "allo", "[2, 3]"])

    def test_ausschnitt_fehler(self):
        for code, muster in [('Zeige Zeichen 0 bis 2 von "abc".', "gibt es nicht"),
                             ('Zeige Zeichen 2 bis 9 von "abc".', "gibt es nicht"),
                             ('Zeige Zeichen 3 bis 2 von "abc".', "gibt es nicht"),
                             ("Zeige Zeichen 1 bis 2 von 5.", "bei Texten"),
                             ('Zeige Elemente 1 bis 2 von "ab".', "bei Listen"),
                             ('Zeige Zeichen 1.5 bis 2 von "abc".', "ganze Zahlen")]:
            with self.subTest(code=code), self.assertRaisesRegex(LaufzeitFehler, muster):
                laufe(code)

    def test_variable_namens_zeichen_bleibt_moeglich(self):
        self.assertEqual(laufe('Für jedes Zeichen in "ab":\nZeige Zeichen.\nEnde.\nMerke "x" als Zeichen.\nZeige Zeichen und Zeichen.'),
                         ["a", "b", "xx"])

    def test_zufaelliges_element(self):
        code = 'Erstelle Liste namens L mit 1 und 2 und 3.\nZähle von 1 bis 60 mit i:\nZeige ein zufälliges Element von L.\nEnde.'
        aus = laufe(code, seed=1)
        self.assertEqual(set(aus), {"1", "2", "3"})
        self.assertEqual(aus, laufe(code, seed=1))
        self.assertIn(laufe('Zeige zufälliges Element von "abc".', seed=2)[0], "abc")
        with self.assertRaisesRegex(LaufzeitFehler, "nichts drin"):
            laufe("Erstelle Liste namens L.\nZeige zufälliges Element von L.")
        with self.assertRaisesRegex(LaufzeitFehler, "Listen und Texten"):
            laufe("Zeige zufälliges Element von 5.")


class Textwerkzeuge(unittest.TestCase):
    def test_ersetze(self):
        code = 'Merke "Hallo Welt, Welt" als T.\nErsetze "Welt" durch "Klarsatz" in T.\nZeige T.\nErsetze "q" durch "z" in T.\nZeige T.'
        self.assertEqual(laufe(code), ["Hallo Klarsatz, Klarsatz", "Hallo Klarsatz, Klarsatz"])

    def test_ersetze_fehler(self):
        for code, muster in [('Merke 5 als T.\nErsetze "a" durch "b" in T.', "drei Texte"),
                             ('Merke "abc" als T.\nErsetze "" durch "b" in T.', "nicht leer"),
                             ('Ersetze "a" durch "b" in Nirgends.', "kenne 'Nirgends' nicht")]:
            with self.subTest(code=code), self.assertRaisesRegex(LaufzeitFehler, muster):
                laufe(code)

    def test_ersetze_wachstum_ist_begrenzt(self):
        from klarsatz.grenzen import Grenzen
        with self.assertRaisesRegex(LaufzeitFehler, "zu lang"):
            laufe('Merke "aaaaaaaaaa" als T.\nErsetze "a" durch "aaaaaaaaaa" in T.', grenzen=Grenzen(text=50))

    def test_zahlenwert(self):
        code = 'Zeige Zahlenwert von "12" plus 1.\nZeige Zahlenwert von " 3,5 " mal 2.\nZeige Zahlenwert von 7.\nZeige Zahlenwert von "-4".'
        self.assertEqual(laufe(code), ["13", "7", "7", "-4"])
        with self.assertRaisesRegex(LaufzeitFehler, "keine Zahl machen"):
            laufe('Zeige Zahlenwert von "abc".')
        with self.assertRaisesRegex(LaufzeitFehler, "keine Zahl machen"):
            laufe("Erstelle Liste namens L.\nZeige Zahlenwert von L.")

    def test_teile_und_zahlenwert_zusammen(self):
        code = ('Teile "3,4,5" bei "," zu Teile.\nMerke 0 als Summe.\n'
                'Für jedes T in Teile:\nErhöhe Summe um Zahlenwert von T.\nEnde.\nZeige Summe.')
        self.assertEqual(laufe(code), ["12"])


class Runden(unittest.TestCase):
    def test_kaufmaennisch(self):
        code = ("Zeige Gerundet von 2.675 auf 2 Stellen.\nZeige Gerundet von minus 2.5.\nZeige Gerundet von 2.5.\n"
                "Zeige Formatiert von 2.675 auf 2 Stellen.\nZeige Formatiert von 1000 auf 2 Stellen.\n"
                "Zeige Formatiert von minus 2.5 auf 0 Stellen.\nZeige Gerundet von 3.14159 auf 3 Stellen.")
        self.assertEqual(laufe(code), ["2,68", "-3", "3", "2,68", "1000,00", "-3", "3,142"])

    def test_gerundet_mit_stellen_in_setze(self):
        self.assertEqual(laufe("Merke 0 als x.\nSetze x auf Gerundet von 1.005 auf 2 Stellen.\nZeige x."), ["1,01"])

    def test_riesige_zahlen(self):
        aus = laufe("Merke 10 hoch 200 als g.\nZeige Länge von Formatiert von g auf 2 Stellen.")
        self.assertEqual(aus, ["204"])
        with self.assertRaisesRegex(LaufzeitFehler, "0 bis 12"):
            laufe("Zeige Formatiert von 1 auf 20 Stellen.")


class KlammernInBedingungen(unittest.TestCase):
    def test_gruppierung(self):
        code = """
        Merke 1 als a.  Merke 5 als b.  Merke 1 als c.
        Wenn (a gleich 9 oder b gleich 5) und c gleich 1 ist, zeige "1".
        Wenn a gleich 9 oder (b gleich 5 und c gleich 2) ist, zeige "nein".
        Sonst zeige "2".
        Wenn nicht (a gleich 1 und b gleich 5) ist, zeige "nein".
        Sonst zeige "3".
        Wenn (a gleich 1) ist, zeige "4".
        Wenn ((a gleich 1) und (b gleich 5 oder b gleich 6)) ist, zeige "5".
        """
        self.assertEqual(laufe(code), ["1", "2", "3", "4", "5"])

    def test_rechenklammern_bleiben_rechenklammern(self):
        code = ("Merke 2 als a.  Merke 3 als b.\nWenn (a plus b) größer als 4 ist, zeige 1.\n"
                "Wenn (a plus b) ist größer als 4, zeige 2.\nWenn (a plus b) mal 2 gleich 10 ist, zeige 3.\n"
                "Wenn (a plus b) nicht gleich 4 ist, zeige 4.\nWenn (a) eine Zahl ist, zeige 5.")
        self.assertEqual(laufe(code), ["1", "2", "3", "4", "5"])

    def test_bedingung_in_klammern_mit_ist_danach_als_block(self):
        self.assertEqual(laufe("Merke 1 als a.\nWenn (a gleich 1 oder a gleich 2) ist:\nZeige 1.\nEnde."), ["1"])

    def test_unbalancierte_klammer_gibt_fehler(self):
        with self.assertRaises(SyntaxFehler):
            laufe("Merke 1 als a.\nWenn (a gleich 1 ist, zeige 1.")


class Zusammenspiel(unittest.TestCase):
    def test_wortzaehler(self):
        code = ('Merke "das ist ein test das ist gut" als Satz.\nTeile Satz bei " " zu Woerter.\n'
                'Erstelle Tabelle namens Anzahl.\nFür jedes W in Woerter:\n'
                '    Wenn Anzahl enthält W:\n        Trage W mit (Wert für W in Anzahl) plus 1 in Anzahl ein.\n'
                '    Sonst:\n        Trage W mit 1 in Anzahl ein.\n    Ende.\nEnde.\n'
                'Für jedes W in Anzahl:\n    Zeige W und ": " und Wert für W in Anzahl.\nEnde.')
        self.assertEqual(laufe(code), ["das: 2", "ist: 2", "ein: 1", "test: 1", "gut: 1"])

    def test_stapel_mit_liste(self):
        code = ('Erstelle Liste namens Stapel.\nFüge 1 zu Stapel hinzu.\nFüge 2 zu Stapel hinzu.\nFüge 3 zu Stapel hinzu.\n'
                'Wiederhole solange Länge von Stapel größer als 0 ist:\n'
                '    Zeige das letzte Element von Stapel.\n    Entferne das letzte Element aus Stapel.\nEnde.')
        self.assertEqual(laufe(code), ["3", "2", "1"])


if __name__ == "__main__":
    unittest.main()
