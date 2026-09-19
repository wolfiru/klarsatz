"""Fuzz-Test: Verdorbene Programme dürfen nur Klarsatz-Fehler erzeugen.

Die Zusage lautet: Egal wie kaputt ein Programm ist, es kommt eine freundliche deutsche
Meldung heraus — nie ein Python-Traceback, nie ein Hänger. Hier wird das nachgewiesen,
indem gültige Programme zufällig zerhackt und an alle Stellen verfüttert werden, die
Quelltext entgegennehmen: Ausführen, Prüfen, Formatieren, Übersetzen nach Python.

Der Lauf ist **deterministisch** (feste Saat) und kurz, damit er bei jedem Testlauf
mitkommt. Für lange Läufe mit Zufallssaat gibt es `python3 tools/fuzze.py`.
"""
import os
import unittest

from klarsatz.fehler import KlarsatzFehler
from tests import fuzzer

# So viele Beschüsse, dass alle Verderber und alle Stellen mehrfach drankommen,
# und so wenige, dass der Test in wenigen Sekunden durch ist. Wer die Suite eilig
# braucht, setzt KLARSATZ_KEIN_FUZZ=1 — die Gegenproben laufen dann trotzdem, denn
# sie kosten fast nichts und halten den Fuzzer ehrlich.
LAEUFE = 600
SAAT = 20260919
EILIG = bool(os.environ.get("KLARSATZ_KEIN_FUZZ"))


class FuzzTest(unittest.TestCase):
    @unittest.skipIf(EILIG, "KLARSATZ_KEIN_FUZZ gesetzt")
    def test_verdorbene_programme_ergeben_nur_klarsatz_fehler(self):
        pannen = fuzzer.beschiesse(saat=SAAT, laeufe=LAEUFE)
        if pannen:
            bericht = "\n".join(p.kurz() for p in pannen[:10])
            self.fail(f"{len(pannen)} von {LAEUFE} Beschüssen sind nicht sauber ausgegangen:\n{bericht}\n\n"
                      f"Einen davon wiederholen: python3 tools/fuzze.py --wiederhole {pannen[0].saat}")

    def test_der_fuzzer_wuerde_einen_python_fehler_auch_merken(self):
        """Gegenprobe: Ein Test, der nie etwas findet, kann auch schlicht blind sein."""
        def kaputt(text, grenzen):
            raise ZeroDivisionError("absichtlich")

        echt = fuzzer.STELLEN
        fuzzer.STELLEN = [("gegenprobe", kaputt)]
        try:
            pannen = fuzzer.beschiesse(saat=1, laeufe=3)
        finally:
            fuzzer.STELLEN = echt
        self.assertEqual(len(pannen), 3)
        self.assertEqual(pannen[0].ausnahme, "ZeroDivisionError")

    def test_der_fuzzer_wuerde_einen_haenger_auch_merken(self):
        """Gegenprobe für die Zeitwache — ein Hänger soll als Fund erscheinen,
        nicht die Testsuite anhalten."""
        def haenger(text, grenzen):
            import time
            time.sleep(10)

        echt = fuzzer.STELLEN
        fuzzer.STELLEN = [("gegenprobe", haenger)]
        try:
            pannen = fuzzer.beschiesse(saat=1, laeufe=1, zeitgrenze=0.5)
        finally:
            fuzzer.STELLEN = echt
        self.assertEqual(len(pannen), 1)
        self.assertEqual(pannen[0].ausnahme, "Hänger")

    def test_gleiche_saat_ergibt_gleichen_mutanten(self):
        """Ohne Wiederholbarkeit wäre ein Fund nicht nachstellbar."""
        eins = fuzzer.baue(987654)
        zwei = fuzzer.baue(987654)
        self.assertEqual(eins[1], zwei[1])
        self.assertEqual(eins[3], zwei[3])

    @unittest.skipIf(EILIG, "KLARSATZ_KEIN_FUZZ gesetzt")
    def test_der_beschuss_dringt_bis_in_den_interpreter_vor(self):
        """Wenn alle Mutanten schon am Parser abprallten, prüfte der Test nur den Parser.

        Erwartet wird, dass ein nennenswerter Teil wirklich ausgeführt wird."""
        from klarsatz import web
        ausgefuehrt = 0
        versuche = 100
        import random
        vergabe = random.Random(SAAT)
        grenzen = fuzzer.knappe_grenzen()
        for _ in range(versuche):
            _, text, _, _, _ = fuzzer.baue(vergabe.randrange(2 ** 32))
            try:
                ergebnis = web.laufe(text, antworten=fuzzer.ANTWORTEN, grenzen=grenzen)
            except KlarsatzFehler:
                continue
            if ergebnis.zustand != "fehler" or ergebnis.fehlerart != "syntax":
                ausgefuehrt += 1
        self.assertGreater(ausgefuehrt, versuche // 10,
                           "Fast alles bleibt am Parser hängen — der Fuzzer kommt nicht tief genug.")


@unittest.skipIf(EILIG, "KLARSATZ_KEIN_FUZZ gesetzt")
class EinzelneGemeinheiten(unittest.TestCase):
    """Handverlesene Bösartigkeiten, die ein Zufallsfuzzer nur selten trifft."""

    def pruefe_sauber(self, quelltext, was="laufen"):
        grenzen = fuzzer.knappe_grenzen()
        for name, stelle in fuzzer.STELLEN:
            with self.subTest(stelle=name, was=was):
                try:
                    with fuzzer.zeitwache(20.0):
                        stelle(quelltext, grenzen)
                except KlarsatzFehler:
                    pass
                except fuzzer.Zeitueberschreitung:
                    self.fail("hängt")

    def test_leerer_und_fast_leerer_quelltext(self):
        for text in ["", " ", "\n", ".", ":", "\t", "\n\n\n", "..." , "…", "\x00", "\ufeff"]:
            with self.subTest(text=repr(text)):
                self.pruefe_sauber(text)

    def test_tiefe_verschachtelung(self):
        self.pruefe_sauber("Zeige " + "(" * 5000 + "1" + ")" * 5000 + ".")

    def test_tiefe_bloecke(self):
        zeilen = []
        for i in range(500):
            zeilen.append(" " * (4 * i) + "Wenn 1 gleich 1 ist:")
        zeilen.append(" " * 2000 + 'Zeige "tief".')
        zeilen += [" " * (4 * i) + "Ende." for i in range(499, -1, -1)]
        self.pruefe_sauber("\n".join(zeilen))

    def test_sehr_langer_satz(self):
        self.pruefe_sauber("Zeige " + " und ".join(['"x"'] * 20000) + ".")

    def test_sehr_viele_zeilen(self):
        self.pruefe_sauber('Zeige "x".\n' * 20000)

    def test_riesige_zahlen(self):
        self.pruefe_sauber("Merke 9" + "9" * 400 + " als Zahl.\nZeige Zahl hoch 99999.")

    def test_unvollstaendige_saetze(self):
        for text in ["Zeige", "Zeige.", "Merke", "Merke als", "Wenn", "Wenn:", "Ende.", "Sonst:",
                     "Definiere Aufgabe", "Definiere Aufgabe:", "Für jedes", "Wiederhole Mal:",
                     'Frage "" und merke', "Gib zurück.", "Ein Hund hat", "Erschaffe einen"]:
            with self.subTest(text=text):
                self.pruefe_sauber(text)

    def test_seltsame_zeichen(self):
        for text in ['Zeige "\x00".', "Zeige 1\x00.", "Zeige\u00a01.", "Zeige 1\u2028Zeige 2.",
                     "Zeige \U0001F600.", "Merke 1 als \U0001F600.", "Zeige " + "\u0301" * 100 + "."]:
            with self.subTest(text=repr(text)):
                self.pruefe_sauber(text)

    def test_endlosschleife_wird_begrenzt(self):
        """Nicht abfangbar: Ein Limit muss durchschlagen, auch durch `Versuche`."""
        from klarsatz import web
        quelltext = ("Versuche:\n"
                     "    Wiederhole solange 1 gleich 1 ist:\n"
                     "        Merke 1 als x.\n"
                     "    Ende.\n"
                     "Bei Fehler:\n"
                     '    Zeige "abgefangen".\n'
                     "Ende.")
        ergebnis = web.laufe(quelltext, grenzen=fuzzer.knappe_grenzen())
        self.assertEqual(ergebnis.zustand, "fehler")
        self.assertEqual(ergebnis.fehlerart, "limit")
        self.assertNotIn("abgefangen", ergebnis.ausgabe)

    def test_rekursion_ohne_ende_endet_als_klarsatz_fehler(self):
        from klarsatz import web
        quelltext = ("Definiere Aufgabe Tief von n:\n"
                     "    Gib (Tief von (n plus 1)) zurück.\n"
                     "Ende.\n"
                     "Zeige Tief von 1.")
        ergebnis = web.laufe(quelltext, grenzen=fuzzer.knappe_grenzen())
        self.assertEqual(ergebnis.zustand, "fehler")
        self.assertIn(ergebnis.fehlerart, {"laufzeit", "limit"})


if __name__ == "__main__":
    unittest.main()
