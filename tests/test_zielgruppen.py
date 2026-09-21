"""Die Eignungstabelle steht an zwei Stellen — sie muss dasselbe sagen.

`README.md` und die Webseite nennen dieselben Zielgruppen mit derselben Einstufung. Zwei
Fassungen laufen sonst auseinander, und dann stimmt eine davon nicht mehr. Der Test hält
sie zusammen.

Bis 0.11.1 stand hier eine Punktzahl von 1 bis 10 mit Punkte-Maß — ein externer Reviewer
hat zu Recht bemängelt, dass das nach einer Messung aussieht, direkt neben dem Satz "kein
Messergebnis". Seit 0.11.2 steht hier nur noch eine von drei Textstufen: Die Zahlen hatten
ohnehin nie mehr Auflösung als diese drei Stufen hergaben (9/8/7 waren immer "gut" gefärbt,
3/2/1 immer "weniger geeignet") — es ging also keine echte Information verloren.
"""
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
README = WURZEL / "README.md"
SEITE = WURZEL / "webseite" / "seiten" / "fuerwen.html"

STUFEN = {"Gut geeignet", "Bedingt geeignet", "Weniger geeignet"}


def aus_readme():
    """| **Zielgruppe** | Gut geeignet | Begründung |"""
    zeilen = {}
    for treffer in re.finditer(r"^\| \*\*(.+?)\*\* \| (Gut geeignet|Bedingt geeignet|Weniger geeignet) \|",
                               README.read_text(encoding="utf-8"), re.M):
        zeilen[treffer.group(1)] = treffer.group(2)
    return zeilen


def aus_webseite():
    text = SEITE.read_text(encoding="utf-8")
    tabelle = re.search(r'<table class="eignung">.*?</table>', text, re.S)
    assert tabelle, "Die Eignungstabelle fehlt auf der Seite."
    zeilen = {}
    for treffer in re.finditer(r'<th scope="row">(.+?)</th>\s*<td><span class="eig-stufe">([^<]+)</span>',
                               tabelle.group(0), re.S):
        zeilen[treffer.group(1)] = treffer.group(2)
    return zeilen


def zeilen_mit_klasse():
    """(Zielgruppe, Zeilen-Klasse eig-gut/-mittel/-schlecht, Stufentext) je Zeile."""
    text = SEITE.read_text(encoding="utf-8")
    tabelle = re.search(r'<table class="eignung">.*?</table>', text, re.S).group(0)
    return re.findall(
        r'<tr class="eig-(gut|mittel|schlecht)">\s*<th scope="row">(.+?)</th>\s*'
        r'<td><span class="eig-stufe">([^<]+)</span>', tabelle, re.S)


class Zielgruppen(unittest.TestCase):
    def test_beide_fassungen_nennen_dieselben_gruppen(self):
        self.assertEqual(sorted(aus_readme()), sorted(aus_webseite()),
                         "README und Webseite listen verschiedene Zielgruppen.")

    def test_beide_fassungen_geben_dieselbe_stufe(self):
        self.assertEqual(aus_readme(), aus_webseite())

    def test_es_gibt_ueberhaupt_eintraege(self):
        self.assertGreaterEqual(len(aus_readme()), 8, "Die Tabelle wird nicht richtig gelesen.")

    def test_nur_die_drei_vorgesehenen_stufen_kommen_vor(self):
        for wer, stufe in aus_readme().items():
            with self.subTest(zielgruppe=wer):
                self.assertIn(stufe, STUFEN)

    def test_die_zeilenfarbe_passt_zur_stufe(self):
        """Grün/Gelb/Rot (eig-gut/-mittel/-schlecht) und der Text müssen dieselbe Aussage
        treffen — sonst widerspricht sich die Zeile selbst."""
        erwartet = {"gut": "Gut geeignet", "mittel": "Bedingt geeignet", "schlecht": "Weniger geeignet"}
        zeilen = zeilen_mit_klasse()
        self.assertGreaterEqual(len(zeilen), 8, "Die Tabelle wird nicht richtig gelesen.")
        for klasse, wer, stufe in zeilen:
            with self.subTest(zielgruppe=wer):
                self.assertEqual(stufe, erwartet[klasse])

    def test_die_punkte_sind_als_selbsteinschaetzung_gekennzeichnet(self):
        """Auch eine Textstufe wie "Gut geeignet" ist noch eine eigene Einschätzung, kein
        Messergebnis — das muss weiterhin dabeistehen."""
        text = SEITE.read_text(encoding="utf-8")
        self.assertIn('<th scope="col">Meine Einschätzung</th>', text)
        self.assertIn("meine eigene Einschätzung", text)
        self.assertIn("kein Messergebnis", text)
        for stelle in ("mit Punkten von 1 bis 10", "meiner Einschätzung von 1 bis 10", "/10"):
            with self.subTest(satz=stelle):
                self.assertNotIn(stelle, text,
                                 "Das behauptet wieder eine Messgenauigkeit, die es nicht gibt.")


if __name__ == "__main__":
    unittest.main()
