"""Die Übungsaufgaben prüfen sich selbst — und dieser Test prüft die Prüfung.

Eine Aufgabe ist nur so gut wie ihre Regeln. Zwei Fehler liegen nahe: Die Regeln sind
zu streng, dann fällt die Musterlösung durch; oder sie sind zu lasch, dann besteht auch
Unsinn. Gegen beides steht hier je eine Probe — jede Aufgabe bringt ihre Musterlösung
**und** eine absichtlich unzureichende Gegenprobe mit, die durchfallen muss.
"""
import unittest
from pathlib import Path

from klarsatz import web
from klarsatz.aufgaben import REGELN, Regel, lies, pruefe
from klarsatz.grenzen import Grenzen
from klarsatz.sprachdaten import HOECHSTE_STUFE

WURZEL = Path(__file__).resolve().parent.parent
DATEI = WURZEL / "docs" / "AUFGABEN.md"
AUFGABEN = lies(DATEI.read_text(encoding="utf-8"))


def laufe(quelltext, antworten=(), stufe=None):
    return web.laufe(quelltext, antworten=antworten, seed=0, grenzen=Grenzen(warte=0), stufe=stufe)


class JedeAufgabe(unittest.TestCase):
    def test_es_gibt_welche(self):
        self.assertGreaterEqual(len(AUFGABEN), 12)

    def test_die_musterloesung_besteht(self):
        for a in AUFGABEN:
            with self.subTest(aufgabe=a.kennung):
                befund = pruefe(a, a.loesung, laufe)
                self.assertTrue(befund.bestanden,
                                f"{a.kennung}: offen ist {befund.offen}, Fehler: "
                                + str([p[2] for p in befund.proben if p[2]]))

    def test_die_gegenprobe_faellt_durch(self):
        """Sonst wären die Regeln zu lasch — dann bestünde auch, wer nichts kann."""
        for a in AUFGABEN:
            with self.subTest(aufgabe=a.kennung):
                self.assertTrue(a.gegenprobe, "Diese Aufgabe hat keine Gegenprobe.")
                self.assertFalse(pruefe(a, a.gegenprobe, laufe).bestanden)

    def test_die_gegenprobe_scheitert_an_einer_regel_nicht_an_einem_fehler(self):
        """Eine kaputte Gegenprobe prüft den Parser, nicht die Regeln."""
        for a in AUFGABEN:
            with self.subTest(aufgabe=a.kennung):
                befund = pruefe(a, a.gegenprobe, laufe)
                self.assertEqual([p[2] for p in befund.proben if p[2]], [])

    def test_keine_aufgabe_verlangt_mehr_als_ihre_stufe(self):
        """Die Stufe ist ein Versprechen: Du brauchst nichts, was noch nicht dran war."""
        for a in AUFGABEN:
            with self.subTest(aufgabe=a.kennung, stufe=a.stufe):
                self.assertTrue(1 <= a.stufe <= HOECHSTE_STUFE)
                ergebnis = laufe(a.loesung, a.proben[0].eingaben, stufe=a.stufe)
                self.assertNotEqual(ergebnis.fehlerart, "stufe",
                                    f"{a.kennung} braucht mehr als Stufe {a.stufe}: {ergebnis.fehler}")

    def test_jede_aufgabe_ist_vollstaendig(self):
        for a in AUFGABEN:
            with self.subTest(aufgabe=a.kennung):
                self.assertTrue(a.titel and a.angabe and a.loesung and a.proben)
                self.assertGreater(len(a.angabe), 40, "Die Angabe ist zu knapp.")
                for probe in a.proben:
                    self.assertTrue(probe.regeln, "Eine Probe ohne Regel prüft nichts.")

    def test_die_nummern_sind_lueckenlos(self):
        self.assertEqual([a.nummer for a in AUFGABEN],
                         [str(i) for i in range(1, len(AUFGABEN) + 1)])

    def test_die_stufen_steigen(self):
        stufen = [a.stufe for a in AUFGABEN]
        self.assertEqual(stufen, sorted(stufen), "Die Aufgaben sollen nicht zurückspringen.")


class AufDerSeite(unittest.TestCase):
    """Was der Browser bekommt, muss dasselbe sein wie das, was hier geprüft wird."""

    @classmethod
    def setUpClass(cls):
        import json
        cls.json = json.loads((WURZEL / "playground" / "aufgaben.json").read_text(encoding="utf-8"))
        cls.seite = (WURZEL / "webseite" / "seiten" / "aufgaben.html").read_text(encoding="utf-8")

    def test_die_datei_fuer_den_browser_ist_aktuell(self):
        """Sonst zeigt die Seite Aufgaben, die es so nicht mehr gibt."""
        self.assertEqual([a["nummer"] for a in self.json], [a.nummer for a in AUFGABEN])
        for daten, aufgabe in zip(self.json, AUFGABEN):
            with self.subTest(aufgabe=aufgabe.kennung):
                self.assertEqual(daten["titel"], aufgabe.titel)
                self.assertEqual(daten["angabe"], aufgabe.angabe)
                self.assertEqual(len(daten["proben"]), len(aufgabe.proben))
                for pd, pa in zip(daten["proben"], aufgabe.proben):
                    self.assertEqual(pd["eingaben"], pa.eingaben)
                    self.assertEqual([tuple(r) for r in pd["regeln"]],
                                     [(r.art, r.wert) for r in pa.regeln])

    def test_die_seite_hat_alles_was_das_skript_sucht(self):
        for kennung in ("auf-liste", "auf-nummer", "auf-titel", "auf-text", "auf-regeln",
                        "auf-abgeben", "auf-loesung", "auf-befund", "auf-fortschritt", "spielwiese"):
            with self.subTest(element=kennung):
                self.assertIn(f'id="{kennung}"', self.seite)

    def test_die_seite_ist_verlinkt(self):
        for name in ("index.html", "spielplatz.html", "tutorial.html"):
            datei = WURZEL / "webseite" / "seiten" / name
            if not datei.exists():
                continue
            with self.subTest(seite=name):
                self.assertIn("aufgaben.html", datei.read_text(encoding="utf-8"))

    def test_die_musterloesung_geht_mit_an_den_browser(self):
        """Sie steckt hinter einem Knopf — verstecken wäre eine Schnitzeljagd."""
        self.assertTrue(all(a["loesung"].strip() for a in self.json))
        self.assertIn("Musterlösung zeigen", self.seite)


class DieRegeln(unittest.TestCase):
    """Jede Regelart einzeln — sie sind die Messlatte, also müssen sie stimmen."""

    def probiere(self, regel, wert, quelltext, eingaben=()):
        return Regel(regel, wert).pruefe(laufe(quelltext, eingaben), quelltext)

    def test_enthaelt(self):
        self.assertTrue(self.probiere("enthält", "Hallo", 'Zeige "Hallo Welt".'))
        self.assertTrue(self.probiere("enthält", "hallo", 'Zeige "Hallo Welt".'), "Groß/klein egal")
        self.assertFalse(self.probiere("enthält", "Tschüss", 'Zeige "Hallo Welt".'))

    def test_enthaelt_nicht(self):
        self.assertTrue(self.probiere("enthält nicht", "Tschüss", 'Zeige "Hallo".'))
        self.assertFalse(self.probiere("enthält nicht", "Hallo", 'Zeige "Hallo".'))

    def test_letzte_zeile(self):
        self.assertTrue(self.probiere("letzte zeile", "42", 'Zeige "erst".\nZeige 42.'))
        self.assertFalse(self.probiere("letzte zeile", "erst", 'Zeige "erst".\nZeige 42.'))
        self.assertFalse(self.probiere("letzte zeile", "4", 'Zeige 42.'), "genau, nicht enthalten")

    def test_zeilen(self):
        self.assertTrue(self.probiere("zeilen", "2", 'Zeige 1.\nZeige 2.'))
        self.assertFalse(self.probiere("zeilen", "3", 'Zeige 1.\nZeige 2.'))

    def test_fragt(self):
        quelle = 'Frage "a" und merke die Antwort als A.\nZeige A.'
        self.assertTrue(self.probiere("fragt", "1", quelle, ["x"]))
        self.assertFalse(self.probiere("fragt", "2", quelle, ["x"]))

    def test_striche(self):
        self.assertTrue(self.probiere("striche", "2", "Gehe 10 Schritte vor.\nGehe 5 Schritte vor."))
        self.assertFalse(self.probiere("striche", "2", "Gehe 10 Schritte vor."))

    def test_benutzt(self):
        self.assertTrue(self.probiere("benutzt", "Wiederhole", "Wiederhole 2 Mal:\n    Zeige 1.\nEnde."))
        self.assertFalse(self.probiere("benutzt", "Zähle", "Wiederhole 2 Mal:\n    Zeige 1.\nEnde."))

    def test_benutzt_nicht(self):
        """Damit niemand die Antwort einfach hinschreibt."""
        self.assertFalse(self.probiere("benutzt nicht", "55", "Zeige 55."))
        self.assertTrue(self.probiere("benutzt nicht", "55", "Zeige 5 mal 11."))

    def test_alle_regelarten_sind_dokumentiert(self):
        from klarsatz import aufgaben
        for art in REGELN:
            with self.subTest(regel=art):
                self.assertIn(art, aufgaben.__doc__.lower())
                self.assertTrue(Regel(art, "1").text)

    def test_eine_unbekannte_regel_wird_gemeldet(self):
        from klarsatz.aufgaben import lies as lies_text
        with self.assertRaisesRegex(ValueError, "unbekannte Regel"):
            lies_text("## 1 — Test\n\nAngabe.\n\n```probe\nzauberei: 1\n```\n")


class WennEtwasSchiefgeht(unittest.TestCase):
    """Die Rückmeldung muss dem Lernenden helfen, nicht nur 'falsch' sagen."""

    def setUp(self):
        self.aufgabe = AUFGABEN[0]

    def test_ein_syntaxfehler_kommt_als_meldung_durch(self):
        befund = pruefe(self.aufgabe, "Zeig mal her.", laufe)
        self.assertFalse(befund.bestanden)
        self.assertIn("Zeige", befund.proben[0][2], "Der Vorschlag des Parsers fehlt.")

    def test_zu_viele_fragen_werden_erklaert(self):
        befund = pruefe(self.aufgabe, 'Frage "a" und merke die Antwort als A.\n'
                                      'Frage "b" und merke die Antwort als B.\nZeige A und B.', laufe)
        self.assertFalse(befund.bestanden)
        self.assertIn("fragt öfter", befund.proben[0][2])

    def test_offen_nennt_die_unerfuellten_regeln(self):
        befund = pruefe(self.aufgabe, 'Zeige "nichts".', laufe)
        self.assertIn("Das Programm fragt einmal.", befund.offen)


if __name__ == "__main__":
    unittest.main()
