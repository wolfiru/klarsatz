"""Lernstufen: nur so viel Sprache zeigen, wie gerade gelernt wurde."""
import unittest
from pathlib import Path

from klarsatz import stufen, web
from klarsatz.fehler import StufenFehler
from klarsatz.interpreter import Interpreter
from klarsatz.lexer import lexer
from klarsatz.parser import RESERVIERT, STARTER
from klarsatz.sprachdaten import (FUNKTIONEN, HOECHSTE_STUFE, KONSTANTEN, KONTROLLE, STUFEN,
                                  STUFEN_NAMEN, STUFE_VON_WORT, _EXTRA)

WURZEL = Path(__file__).resolve().parent.parent


class Einteilung(unittest.TestCase):
    def test_jedes_wort_der_sprache_hat_eine_stufe(self):
        """Der wichtigste Test: Ohne ihn wird die Sperre löchrig, sobald die Sprache wächst."""
        alle = set(RESERVIERT) | set(STARTER) | KONTROLLE | FUNKTIONEN | _EXTRA | KONSTANTEN
        self.assertEqual(sorted(alle - set(STUFE_VON_WORT)), [],
                         "Diese Wörter haben keine Lernstufe — bitte in sprachdaten.STUFEN eintragen.")

    def test_keine_stufe_kennt_ein_wort_das_es_nicht_gibt(self):
        alle = set(RESERVIERT) | set(STARTER) | KONTROLLE | FUNKTIONEN | _EXTRA | KONSTANTEN
        self.assertEqual(sorted(set(STUFE_VON_WORT) - alle), [],
                         "Diese Wörter stehen in einer Stufe, gibt es in der Sprache aber nicht.")

    def test_jede_stufe_hat_einen_namen(self):
        self.assertEqual(sorted(STUFEN), sorted(STUFEN_NAMEN))

    def test_kein_wort_steht_in_zwei_stufen(self):
        gesehen = set()
        for nr, woerter in STUFEN.items():
            doppelt = gesehen & woerter
            self.assertEqual(doppelt, set(), f"Stufe {nr} wiederholt: {doppelt}")
            gesehen |= woerter


class Sperre(unittest.TestCase):
    def laufe(self, quelltext, stufe, antworten=()):
        return web.laufe(quelltext, antworten=antworten, seed=0, stufe=stufe)

    def test_stufe_1_kann_zeigen_fragen_merken(self):
        e = self.laufe('Merke "Rocco" als Hund.\nZeige "Mein Hund heißt " und Hund und ".".', 1)
        self.assertEqual(e.zustand, "fertig")
        self.assertEqual(e.ausgabe, ["Mein Hund heißt Rocco."])

    def test_stufe_1_sperrt_das_rechnen(self):
        e = self.laufe("Zeige 1 plus 1.", 1)
        self.assertEqual(e.fehlerart, "stufe")
        self.assertIn("Stufe 2 (Rechnen)", e.fehler)
        self.assertIn("Stufe 1 (Zeigen, fragen, merken)", e.fehler)

    def test_die_meldung_zeigt_auf_das_wort(self):
        e = self.laufe("Merke 5 als Zahl.\nWenn Zahl gleich 5 ist:\n    Zeige Zahl.\nEnde.", 2)
        self.assertEqual(e.fehler_zeile, 2)
        self.assertEqual(e.fehler_spalte, 0)
        self.assertIn("'Wenn'", e.fehler)

    def test_hoechste_stufe_erlaubt_alles(self):
        quelle = (WURZEL / "programme" / "20_grafisches_adventure.klar").read_text(encoding="utf-8")
        Interpreter(stufe=HOECHSTE_STUFE).parse(quelle)          # darf nicht werfen

    def test_ohne_angabe_ist_nichts_gesperrt(self):
        quelle = (WURZEL / "programme" / "16_uhr.klar").read_text(encoding="utf-8")
        Interpreter().parse(quelle)
        Interpreter(stufe=None).parse(quelle)

    def test_stufe_sperrt_nur_nach_oben(self):
        """Was auf Stufe n läuft, läuft auch auf jeder höheren."""
        quelltext = "Merke 3 als a.\nZeige a mal a.\n"
        for stufe in range(2, HOECHSTE_STUFE + 1):
            with self.subTest(stufe=stufe):
                self.assertEqual(self.laufe(quelltext, stufe).zustand, "fertig")

    def test_unsinnige_stufe_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            stufen.pruefe(lexer("Zeige 1."), 0)


class KeineFehlalarme(unittest.TestCase):
    """Funktionswörter sind erlaubte Variablennamen — die dürfen nicht gesperrt werden."""

    def test_variable_darf_wie_eine_funktion_heissen(self):
        for name in ("Wurzel", "Element", "Wert", "Laenge", "Rest", "Zeichen", "Erste"):
            with self.subTest(name=name):
                e = web.laufe(f'Merke "x" als {name}.\nZeige {name}.', seed=0, stufe=1)
                self.assertEqual(e.zustand, "fertig", e.fehler)
                self.assertEqual(e.ausgabe, ["x"])

    def test_dasselbe_wort_als_funktion_wird_sehr_wohl_gesperrt(self):
        e = web.laufe("Zeige die Wurzel von 4.", seed=0, stufe=1)
        self.assertEqual(e.fehlerart, "stufe")
        self.assertIn("Wurzel", e.fehler)

    def test_woerter_in_texten_zaehlen_nicht(self):
        e = web.laufe('Zeige "Wenn und Aber, plus mal geteilt".', seed=0, stufe=1)
        self.assertEqual(e.zustand, "fertig")
        self.assertEqual(e.ausgabe, ["Wenn und Aber, plus mal geteilt"])


class PasstZumTutorial(unittest.TestCase):
    """Die Stufen sind nur dann sinnvoll, wenn sie der Reihenfolge des Tutorials folgen."""

    def kleinste_stufe(self, quelltext, antworten):
        for s in range(1, HOECHSTE_STUFE + 1):
            if web.laufe(quelltext, antworten=antworten, seed=0, stufe=s).fehlerart != "stufe":
                return s
        return HOECHSTE_STUFE

    def test_jede_lektion_bleibt_auf_ihrer_stufe_oder_darueber(self):
        from tests.test_tutorial import TUTORIAL, lies_bloecke
        je_lektion = {}
        for block in lies_bloecke(TUTORIAL.read_text(encoding="utf-8")):
            if not block.lektion.startswith("Lektion"):
                continue
            nr = int(block.lektion.split()[1])
            je_lektion[nr] = max(je_lektion.get(nr, 0),
                                 self.kleinste_stufe(block.quelltext, block.eingaben))

        vorher = 0
        for nr in sorted(je_lektion):
            with self.subTest(lektion=nr):
                self.assertGreaterEqual(
                    je_lektion[nr], vorher,
                    f"Lektion {nr} braucht nur Stufe {je_lektion[nr]}, die Lektion davor schon "
                    f"{vorher} — dann passen Stufen und Tutorial nicht mehr zusammen.")
            vorher = je_lektion[nr]

    def test_die_letzte_lektion_braucht_die_hoechste_stufe(self):
        from tests.test_tutorial import TUTORIAL, lies_bloecke
        letzte = [b for b in lies_bloecke(TUTORIAL.read_text(encoding="utf-8"))
                  if b.lektion.startswith("Lektion 11")]
        self.assertTrue(letzte)
        self.assertEqual(max(self.kleinste_stufe(b.quelltext, b.eingaben) for b in letzte),
                         HOECHSTE_STUFE)


class Uebersicht(unittest.TestCase):
    def test_uebersicht_nennt_alle_stufen(self):
        text = stufen.uebersicht()
        for nr, titel in STUFEN_NAMEN.items():
            self.assertIn(f"Stufe {nr} — {titel}", text)
        self.assertIn("zeige", text)

    def test_kommandozeile_kennt_stufe_und_stufen(self):
        from klarsatz.cli import baue_parser
        args = baue_parser().parse_args(["--stufe", "3", "x.klar"])
        self.assertEqual(args.stufe, 3)
        self.assertTrue(baue_parser().parse_args(["--stufen"]).stufen)


if __name__ == "__main__":
    unittest.main()
