"""Das Tutorial rechnet sich selbst nach.

`docs/TUTORIAL.md` enthält Lektionen mit lauffähigen Programmen. Jeder ```klar-Block wird hier
ausgeführt — mit den Eingaben aus dem zugehörigen ```eingabe-Block — und die Ausgabe mit dem
```ausgabe-Block verglichen. Stimmt etwas nicht mehr, schlägt dieser Test an, und zwar mit der
Lektion und der Zeilennummer im Tutorial.

So kann das Tutorial nicht veralten: Wer die Sprache ändert, merkt es hier.
"""
import re
import unittest
from dataclasses import dataclass, field
from pathlib import Path

from klarsatz import web
from klarsatz.grenzen import Grenzen
from klarsatz.nach_python import nach_python

TUTORIAL = Path(__file__).resolve().parent.parent / "docs" / "TUTORIAL.md"

# Fester Startwert, damit `Zufallszahl` im Tutorial reproduzierbar ist.
SAAT = 0


@dataclass
class Block:
    zeile: int
    lektion: str
    quelltext: str
    eingaben: list = field(default_factory=list)
    ausgabe: list = field(default_factory=list)
    hat_ausgabe: bool = False
    fehler: list = field(default_factory=list)      # absichtlich kaputt: erwartete Meldung
    python: list = field(default_factory=list)      # erwartete Übersetzung
    zeichnung: list = field(default_factory=list)   # erwartetes Bild (striche/farben/geschlossen)


def lies_bloecke(text):
    """Sammelt die ```klar-Blöcke samt der unmittelbar folgenden eingabe/ausgabe-Blöcke."""
    zeilen = text.split("\n")
    bloecke, lektion, i = [], "(vor der ersten Lektion)", 0
    while i < len(zeilen):
        zeile = zeilen[i]
        if zeile.startswith("## "):
            lektion = zeile[3:].strip()
        treffer = re.match(r"^(\s*)```(klar|vorlage|eingabe|ausgabe|fehler|python|zeichnung)\s*$", zeile)
        if not treffer:
            i += 1
            continue
        einzug, art = treffer.group(1), treffer.group(2)
        start = i
        inhalt = []
        i += 1
        while i < len(zeilen) and zeilen[i].strip() != "```":
            inhalt.append(zeilen[i][len(einzug):] if zeilen[i].startswith(einzug) else zeilen[i])
            i += 1
        i += 1                       # schließende ``` überspringen
        if art in ("klar", "vorlage"):
            bloecke.append(Block(start + 1, lektion, "\n".join(inhalt) + "\n"))
        elif bloecke:
            if art == "eingabe":
                bloecke[-1].eingaben = [z for z in inhalt]
            elif art == "fehler":
                bloecke[-1].fehler = inhalt
            elif art == "python":
                bloecke[-1].python = inhalt
            elif art == "zeichnung":
                bloecke[-1].zeichnung = inhalt
            else:
                bloecke[-1].ausgabe = inhalt
                bloecke[-1].hat_ausgabe = True
    return bloecke


class Tutorial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bloecke = lies_bloecke(TUTORIAL.read_text(encoding="utf-8"))

    def test_tutorial_ist_vorhanden(self):
        self.assertTrue(TUTORIAL.exists(), "docs/TUTORIAL.md fehlt")
        self.assertGreaterEqual(len(self.bloecke), 30,
                                "Auffällig wenige Beispiele — wird die Datei richtig gelesen?")

    def test_jeder_block_laeuft_und_gibt_aus_was_dasteht(self):
        for block in self.bloecke:
            if block.fehler:
                continue                      # eigener Test weiter unten
            with self.subTest(lektion=block.lektion, zeile=block.zeile):
                ergebnis = web.laufe(block.quelltext, antworten=block.eingaben, seed=SAAT,
                                     grenzen=Grenzen.streng())
                if ergebnis.zustand == "fehler":
                    self.fail(f"Zeile {block.zeile} ({block.lektion}) läuft nicht:\n{ergebnis.fehler}")
                if ergebnis.zustand == "wartet":
                    self.fail(f"Zeile {block.zeile} ({block.lektion}) wartet auf eine Eingabe, "
                              f"die im Tutorial nicht dasteht: {ergebnis.frage!r}")
                if not block.hat_ausgabe:
                    continue
                self.assertEqual(ergebnis.ausgabe, block.ausgabe,
                                 f"Zeile {block.zeile} ({block.lektion}): Ausgabe stimmt nicht mit "
                                 f"dem überein, was im Tutorial steht")

    def test_absichtliche_fehler_melden_genau_das_was_dasteht(self):
        """Die Lektion über Fehlermeldungen zeigt echte Meldungen — also müssen sie stimmen."""
        geprueft = 0
        for block in self.bloecke:
            if not block.fehler:
                continue
            with self.subTest(lektion=block.lektion, zeile=block.zeile):
                ergebnis = web.laufe(block.quelltext, antworten=block.eingaben, seed=SAAT,
                                     grenzen=Grenzen.streng())
                self.assertEqual(ergebnis.zustand, "fehler",
                                 f"Zeile {block.zeile}: Das Programm sollte einen Fehler zeigen, "
                                 f"läuft aber durch.")
                erwartet = "\n".join(block.fehler).strip()
                self.assertIn(erwartet, ergebnis.fehler,
                              f"Zeile {block.zeile}: Die Meldung lautet anders als im Tutorial.")
                geprueft += 1
        self.assertGreater(geprueft, 0, "Kein einziger Fehlerblock — wird die Datei richtig gelesen?")

    def test_die_python_gegenueberstellung_stimmt(self):
        """Lektion 11 zeigt dieselben Programme in Python. Das darf nicht von Hand abgetippt sein."""
        geprueft = 0
        for block in self.bloecke:
            if not block.python:
                continue
            with self.subTest(lektion=block.lektion, zeile=block.zeile):
                self.assertEqual(nach_python(block.quelltext).strip(),
                                 "\n".join(block.python).strip(),
                                 f"Zeile {block.zeile}: Die Übersetzung sieht inzwischen anders aus.")
                geprueft += 1
        self.assertGreater(geprueft, 0, "Kein einziger Python-Block gefunden.")

    def test_es_gibt_elf_lektionen(self):
        ueberschriften = [z[3:].strip() for z in TUTORIAL.read_text(encoding="utf-8").split("\n")
                          if z.startswith("## Lektion ")]
        self.assertEqual(len(ueberschriften), 11, f"gefunden: {ueberschriften}")

    def test_jede_lektion_hat_beispiele(self):
        """Ausnahme: Das Abschlussprojekt gibt absichtlich keine Lösung vor."""
        OHNE_CODE = {10}
        mit_bloecken = {int(b.lektion.split()[1]) for b in self.bloecke if b.lektion.startswith("Lektion")}
        fehlen = set(range(1, 12)) - mit_bloecken - OHNE_CODE
        self.assertEqual(fehlen, set(), f"Diese Lektionen haben kein einziges Beispiel: {sorted(fehlen)}")


class Seitenbau(unittest.TestCase):
    """Der Markdown-Leser von tools/baue_tutorial.py.

    Er ist absichtlich klein gehalten — aber genau deshalb muss er bei allem, was er nicht
    kennt, trotzdem weiterlaufen. Ein Bauwerkzeug, das hängt, ist schlimmer als eines, das
    sich beschwert: Es blockiert das Veröffentlichen, ohne zu sagen warum. Das ist genau
    einmal passiert, an einer Zeile, die nur aus '>' bestand.
    """

    def baue(self, text):
        import importlib.util
        pfad = Path(__file__).resolve().parent.parent / "tools" / "baue_tutorial.py"
        spec = importlib.util.spec_from_file_location("baue_tutorial", pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.nach_html(text)

    def test_sperrige_zeilen_lassen_den_bau_nicht_haengen(self):
        import signal
        from tests import fuzzer

        sperrig = [
            "> ein Zitat\n>\n> nach einer leeren Zitatzeile",   # der echte Fall
            ">",
            ">>> tief",
            "####### sieben Rauten",
            "- [ ] eine Aufgabenliste",
            "***",
            "|unvollständige Tabelle",
            "```klar\nZeige 1.",                                  # nie geschlossen
            "\t eingerückt mit Tab",
            "",
            "   ",
            "*kursiv am Zeilenanfang*",
        ]
        for text in sperrig:
            with self.subTest(text=repr(text[:30])):
                try:
                    with fuzzer.zeitwache(10.0):
                        self.baue(text)
                except fuzzer.Zeitueberschreitung:
                    self.fail("Der Seitenbau hängt an dieser Zeile.")

    def test_das_zitat_mit_leerzeile_wird_zu_zwei_absaetzen(self):
        html, _ = self.baue("> erster Teil\n>\n> zweiter Teil")
        self.assertEqual(html.count("<p>"), 2)
        self.assertIn("erster Teil", html)
        self.assertIn("zweiter Teil", html)

    def test_kaputte_beispiele_werden_von_der_webpruefung_ausgenommen(self):
        html, _ = self.baue('```klar\nZeige "Hallo"\n```\n```fehler\nfehlt ein Punkt\n```')
        self.assertIn('data-pruefung="nein"', html)

    def test_heile_beispiele_bleiben_in_der_webpruefung(self):
        html, _ = self.baue('```klar\nZeige "Hallo".\n```\n```ausgabe\nHallo\n```')
        self.assertNotIn('data-pruefung="nein"', html)

    def test_die_aufgabe_bekommt_eine_flaeche_zum_loesen(self):
        html, _ = self.baue("**Deine Aufgabe:** Zeig deinen Namen.")
        self.assertIn('class="aufgabe-flaeche"', html)
        self.assertIn("Zeig deinen Namen.", html)
        self.assertIn("Leeres Blatt", html)

    def test_eine_vorlage_landet_in_der_aufgabenflaeche(self):
        """Aufgaben wie „bau drei Fehler ein" brauchen etwas, das schon läuft."""
        html, _ = self.baue('**Deine Aufgabe:** Bau Fehler ein.\n\n```vorlage\nZeige "Hallo".\n```')
        self.assertIn('data-vorlage="Zeige &quot;Hallo&quot;."', html)
        self.assertIn("aufgabe-vorlage", html)
        self.assertIn("Programm öffnen", html)
        self.assertNotIn("Leeres Blatt", html)
        self.assertEqual(html.count("aufgabe-flaeche"), 1,
                         "Die Vorlage steht neben der Fläche statt darin.")

    def test_eine_vorlage_ohne_aufgabe_bleibt_ein_normaler_block(self):
        html, _ = self.baue('```vorlage\nZeige "Hallo".\n```')
        self.assertNotIn("aufgabe-flaeche", html)
        self.assertIn("Hallo", html)


if __name__ == "__main__":
    unittest.main()
