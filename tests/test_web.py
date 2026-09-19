"""Web-Schnittstelle: Abspielen statt Blockieren."""
import json
import random
import unittest
from pathlib import Path

from klarsatz import Interpreter
from klarsatz.grenzen import Grenzen
from klarsatz.web import Sitzung, formatiere_json, laufe, laufe_json, pruefe_json

PROGRAMME = Path(__file__).resolve().parent.parent / "programme"


def programm(name):
    return (PROGRAMME / name).read_text(encoding="utf-8")


class Ablauf(unittest.TestCase):
    def test_wartet_auf_antworten_und_endet(self):
        code = 'Zeige "Hallo".\nFrage "Name?" und merke die Antwort als N.\nZeige "Hi, " und N.\nFrage "Alter?" und merke die Antwort als A.\nZeige A plus 1.'
        s = Sitzung(code, seed=1)
        e = s.start()
        self.assertEqual((e.zustand, e.frage, e.ausgabe), ("wartet", "Name? ", ["Hallo"]))
        e = s.antworte("Emil")
        self.assertEqual((e.zustand, e.frage, e.ausgabe), ("wartet", "Alter? ", ["Hallo", "Hi, Emil"]))
        e = s.antworte("41")
        self.assertEqual(e.zustand, "fertig")
        self.assertEqual(e.ausgabe, ["Hallo", "Hi, Emil", "42"])
        self.assertEqual(e.verlauf, [("aus", "Hallo"), ("frage", "Name? "), ("antwort", "Emil"), ("aus", "Hi, Emil"),
                                     ("frage", "Alter? "), ("antwort", "41"), ("aus", "42")])

    def test_programm_ohne_fragen_ist_sofort_fertig(self):
        e = Sitzung('Zeige 1 plus 1.').start()
        self.assertEqual((e.zustand, e.ausgabe), ("fertig", ["2"]))

    def test_antwort_ohne_frage_ist_ein_fehler(self):
        s = Sitzung("Zeige 1.")
        s.start()
        with self.assertRaises(ValueError):
            s.antworte("x")
        with self.assertRaises(ValueError):
            Sitzung("Zeige 1.").antworte("x")

    def test_neustart_beginnt_von_vorn(self):
        s = Sitzung('Frage "?" und merke die Antwort als A.\nZeige A.')
        s.start()
        s.antworte("x")
        e = s.start()
        self.assertEqual((e.zustand, e.frage), ("wartet", "? "))

    def test_zufall_ist_bei_gleichem_seed_gleich(self):
        code = 'Zeige Zufallszahl von 1 bis 1000.\nFrage "?" und merke die Antwort als A.\nZeige Zufallszahl von 1 bis 1000.'
        a = Sitzung(code, seed=7)
        b = Sitzung(code, seed=7)
        a.start(), b.start()
        self.assertEqual(a.antworte("x").ausgabe, b.antworte("y").ausgabe)
        self.assertNotEqual(Sitzung(code, seed=8).start().ausgabe, Sitzung(code, seed=7).start().ausgabe)

    def test_ohne_seed_wird_einer_gewuerfelt_und_gemerkt(self):
        s = Sitzung('Zeige Zufallszahl von 1 bis 1000000.\nFrage "?" und merke die Antwort als A.')
        erste = s.start().ausgabe
        self.assertEqual(s.antworte("x").ausgabe, erste)            # beim Abspielen bleibt es dieselbe Zahl


class GleichesVerhaltenWieDirekterLauf(unittest.TestCase):
    def test_zahlenraten_du_raetst(self):
        quelle = programm("01_zahlenraten_du_raetst.klar")
        antworten = ["2", "50", "25", "75", "12", "37", "ende", "n"]
        # direkt
        vorrat, direkt = iter(antworten), []
        Interpreter(ausgabe=direkt.append, eingabe=lambda p="": next(vorrat), zufall=random.Random(3)).lauf(quelle)
        # über die Web-Schnittstelle, Antwort für Antwort
        s = Sitzung(quelle, seed=3)
        e = s.start()
        for a in antworten:
            self.assertEqual(e.zustand, "wartet")
            e = s.antworte(a)
        self.assertEqual(e.zustand, "fertig")
        self.assertEqual(e.ausgabe, direkt)

    def test_alle_programme_laufen_bis_zur_ersten_frage_oder_zum_ende(self):
        # Knappe Grenzen und kein echtes Warten: Dauerprogramme wie die Uhr laufen sonst
        # endlos weiter. Sie dürfen hier am Schrittlimit enden — Hauptsache ohne Absturz.
        from dataclasses import replace
        knapp = replace(Grenzen.streng(), schritte=3000, warte=0)
        for datei in sorted(PROGRAMME.glob("*.klar")):
            with self.subTest(programm=datei.name):
                e = laufe(datei.read_text(encoding="utf-8"), seed=1, grenzen=knapp)
                if e.zustand == "fehler":
                    self.assertEqual(e.fehlerart, "limit", e.fehler)
                else:
                    self.assertIn(e.zustand, ("wartet", "fertig"), e.fehler)

    def test_taschenrechner_komplett(self):
        e = laufe(programm("03_taschenrechner.klar"), ["+", "2", "3", "ende"])
        self.assertEqual(e.zustand, "fertig")
        self.assertIn("2 + 3 = 5", e.ausgabe)


class DateienImArbeitsspeicher(unittest.TestCase):
    def test_todo_liste_speichert_im_speicher(self):
        e = laufe(programm("18_todo_liste.klar"), ["1", "Milch", "0"])
        self.assertEqual(e.zustand, "fertig")
        self.assertEqual(e.dateien, {"todo.txt": "0;Milch\n"})

    def test_dateien_ueberleben_das_abspielen_nicht_doppelt(self):
        s = Sitzung(programm("18_todo_liste.klar"))
        e = s.start()
        for a in ["1", "Milch", "1", "Brot", "0"]:
            e = s.antworte(a)
        self.assertEqual(e.dateien["todo.txt"], "0;Milch\n0;Brot\n")

    def test_vorhandene_dateien_werden_geladen(self):
        e = laufe(programm("18_todo_liste.klar"), ["0"], dateien={"todo.txt": "1;Alt\n"})
        self.assertIn("1. [x] Alt", e.ausgabe)

    def test_dateizugriff_ausserhalb_gibt_es_nicht(self):
        e = laufe('Lies die Datei "/etc/hostname" als X.\nZeige X.')
        self.assertEqual(e.zustand, "fehler")


class Fehler(unittest.TestCase):
    def test_syntaxfehler(self):
        e = laufe("Merke 5 als Zahl.\nZeigee Zahl.")
        self.assertEqual((e.zustand, e.fehlerart, e.fehler_zeile, e.fehler_spalte), ("fehler", "syntax", 2, 0))
        self.assertIn("Meintest du 'Zeige'?", e.fehler)

    def test_laufzeitfehler_behaelt_die_bisherige_ausgabe(self):
        e = laufe('Zeige "vorher".\nZeige 1 geteilt durch 0.')
        self.assertEqual((e.zustand, e.fehlerart), ("fehler", "laufzeit"))
        self.assertEqual(e.ausgabe, ["vorher"])

    def test_fehler_nach_einer_antwort(self):
        e = laufe('Frage "?" und merke die Antwort als A.\nZeige A geteilt durch 0.', ["1"])
        self.assertEqual(e.fehlerart, "laufzeit")

    def test_endlosschleife_wird_gestoppt(self):
        e = laufe("Wiederhole solange wahr ist:\nEnde.", grenzen=Grenzen(schritte=1000))
        self.assertEqual((e.zustand, e.fehlerart), ("fehler", "limit"))

    def test_standardgrenzen_sind_streng(self):
        e = laufe("Wiederhole solange wahr ist:\n    Merke 1 als a.\nEnde.")
        self.assertEqual(e.fehlerart, "limit")

    def test_versuche_faengt_die_wartepause_nicht_ab(self):
        code = 'Versuche:\n    Frage "?" und merke die Antwort als A.\nBei Fehler:\n    Zeige "gefangen".\nEnde.\nZeige "danach".'
        e = laufe(code)
        self.assertEqual((e.zustand, e.frage), ("wartet", "? "))
        e = laufe(code, ["x"])
        self.assertEqual((e.zustand, e.ausgabe), ("fertig", ["danach"]))


class JsonSchnittstelle(unittest.TestCase):
    def test_laufe_json(self):
        d = json.loads(laufe_json('Frage "Wie?" und merke die Antwort als A.\nZeige A.', '["gut"]', 5))
        self.assertEqual(d["zustand"], "fertig")
        self.assertEqual(d["verlauf"], [["frage", "Wie? "], ["antwort", "gut"], ["aus", "gut"]])
        d = json.loads(laufe_json('Frage "Wie?" und merke die Antwort als A.'))
        self.assertEqual((d["zustand"], d["frage"]), ("wartet", "Wie? "))

    def test_umlaute_bleiben_erhalten(self):
        self.assertIn("Grüße", laufe_json('Zeige "Grüße".'))

    def test_pruefe_json(self):
        liste = json.loads(pruefe_json("Merke 5 als Zahl.\nZeige Zahll."))
        fehler = [b for b in liste if b["schwere"] == "Fehler"]
        self.assertEqual([b["zeile"] for b in fehler], [2])
        self.assertEqual(json.loads(pruefe_json('Zeige "ok".')), [])

    def test_formatiere_json(self):
        d = json.loads(formatiere_json("Wenn wahr ist:\nZeige 1.\nEnde."))
        self.assertEqual((d["ok"], d["text"]), (True, "Wenn wahr ist:\n    Zeige 1.\nEnde.\n"))
        d = json.loads(formatiere_json('Zeige "offen.'))
        self.assertEqual((d["ok"], d["zeile"]), (False, 1))


if __name__ == "__main__":
    unittest.main()
