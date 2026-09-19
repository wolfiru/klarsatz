"""Die Eignungstabelle steht an zwei Stellen — sie muss dasselbe sagen.

`README.md` und die Webseite nennen dieselben Zielgruppen mit derselben Punktzahl. Zwei
Fassungen laufen sonst auseinander, und dann stimmt eine davon nicht mehr. Der Test hält
sie zusammen.
"""
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
README = WURZEL / "README.md"
SEITE = WURZEL / "webseite" / "seiten" / "index.html"


def aus_readme():
    """| ✓ | **Zielgruppe** | `●●●●●●●●●○` 9/10 | Begründung |"""
    zeilen = {}
    for treffer in re.finditer(r"^\| [✓~✗] \| \*\*(.+?)\*\* \| `[●○]+` (\d+)/10 \|", 
                               README.read_text(encoding="utf-8"), re.M):
        zeilen[treffer.group(1)] = int(treffer.group(2))
    return zeilen


def aus_webseite():
    text = SEITE.read_text(encoding="utf-8")
    # Nur innerhalb der Eignungstabelle suchen. Die Seite hat inzwischen weitere
    # Tabellen mit <th scope="row">, und ein Muster über die ganze Datei läuft
    # sonst quer durch sie hindurch.
    tabelle = re.search(r'<table class="eignung">.*?</table>', text, re.S)
    assert tabelle, "Die Eignungstabelle fehlt auf der Seite."
    zeilen = {}
    for treffer in re.finditer(r'<th scope="row">(.+?)</th>\s*<td><span class="eig-messer"[^>]*'
                               r'aria-label="(\d+) von 10"', tabelle.group(0), re.S):
        zeilen[treffer.group(1)] = int(treffer.group(2))
    return zeilen


class Zielgruppen(unittest.TestCase):
    def test_beide_fassungen_nennen_dieselben_gruppen(self):
        self.assertEqual(sorted(aus_readme()), sorted(aus_webseite()),
                         "README und Webseite listen verschiedene Zielgruppen.")

    def test_beide_fassungen_geben_dieselbe_punktzahl(self):
        self.assertEqual(aus_readme(), aus_webseite())

    def test_es_gibt_ueberhaupt_eintraege(self):
        self.assertGreaterEqual(len(aus_readme()), 8, "Die Tabelle wird nicht richtig gelesen.")

    def test_die_punkte_liegen_zwischen_1_und_10(self):
        for wer, punkte in aus_readme().items():
            with self.subTest(zielgruppe=wer):
                self.assertTrue(1 <= punkte <= 10)

    def test_die_gefuellten_punkte_stimmen_mit_der_zahl(self):
        """Im Maß müssen so viele Punkte gefüllt sein, wie die Zahl sagt."""
        text = SEITE.read_text(encoding="utf-8")
        # Bis zum Ende des Maßes lesen, nicht bis zum ersten </span> — das gehört zum
        # ersten Punkt und ergäbe immer 1.
        for messer, punkte in re.findall(
                r'aria-label="(\d+) von 10">(.*?)</span><span class="eig-zahl"', text, re.S):
            with self.subTest(punkte=messer):
                self.assertEqual(punkte.count("ist-voll"), int(messer))
                self.assertEqual(punkte.count("eig-punkt"), 10)

    def test_die_readme_zeigt_ebenso_viele_gefuellte_kreise(self):
        for kreise, zahl in re.findall(r"`([●○]+)` (\d+)/10", README.read_text(encoding="utf-8")):
            with self.subTest(zahl=zahl):
                self.assertEqual(kreise.count("●"), int(zahl))
                self.assertEqual(len(kreise), 10)


if __name__ == "__main__":
    unittest.main()
