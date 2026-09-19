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


def lies_bloecke(text):
    """Sammelt die ```klar-Blöcke samt der unmittelbar folgenden eingabe/ausgabe-Blöcke."""
    zeilen = text.split("\n")
    bloecke, lektion, i = [], "(vor der ersten Lektion)", 0
    while i < len(zeilen):
        zeile = zeilen[i]
        if zeile.startswith("## "):
            lektion = zeile[3:].strip()
        treffer = re.match(r"^(\s*)```(klar|eingabe|ausgabe)\s*$", zeile)
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
        if art == "klar":
            bloecke.append(Block(start + 1, lektion, "\n".join(inhalt) + "\n"))
        elif bloecke:
            if art == "eingabe":
                bloecke[-1].eingaben = [z for z in inhalt]
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

    def test_jede_lektion_hat_beispiele(self):
        lektionen = {b.lektion for b in self.bloecke if b.lektion.startswith("Lektion")}
        self.assertEqual(len(lektionen), 11, f"Erwartet werden 11 Lektionen, gefunden: {sorted(lektionen)}")


if __name__ == "__main__":
    unittest.main()
