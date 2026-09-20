"""Der Abschnitt „Was damit geht" darf nicht von den Programmen abweichen.

Auf der Startseite steht ein Ausschnitt aus einem echten Programm, dazu Zahlen
(Gitter, Generationen, Leinwand) und ein Knopf, der genau dieses Programm lädt.
Alle vier Angaben stammen aus derselben Datei — dieser Test rechnet nach, dass sie
es auch bleiben. Sonst zeigt die Seite irgendwann etwas, das es nicht mehr gibt.
"""
import json
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITE = WURZEL / "webseite" / "seiten" / "index.html"
PROGRAMM = WURZEL / "programme" / "21_spiel_des_lebens.klar"


def abschnitt():
    t = SEITE.read_text(encoding="utf-8")
    anfang = t.index('<section class="section" id="komplex">')
    return t[anfang:t.index("</section>", anfang)]


def entschluesselt(html):
    return (html.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
                .replace("&amp;", "&").replace("&#8209;", "-"))


class DerAusschnittStammtAusDemProgramm(unittest.TestCase):
    def setUp(self):
        self.a = abschnitt()
        self.quelle = PROGRAMM.read_text(encoding="utf-8")

    def test_jede_gezeigte_zeile_steht_so_im_programm(self):
        block = re.search(r'<pre class="klar"[^>]*>(.*?)</pre>', self.a, re.S).group(1)
        zeilen = [z.strip() for z in entschluesselt(block).strip().split("\n")]
        self.assertEqual(len(zeilen), 3, "Der gezeigte Ausschnitt hat sich geändert.")
        for zeile in zeilen:
            with self.subTest(zeile=zeile):
                self.assertIn(zeile, self.quelle,
                              "Diese Zeile steht so nicht mehr im Programm.")

    def test_der_ausschnitt_wird_nicht_ausgefuehrt_und_nicht_verlinkt(self):
        """Drei Zeilen aus der Mitte laufen für sich allein nicht — beides muss abgeschaltet sein."""
        pre = re.search(r'<pre class="klar"([^>]*)>', self.a).group(1)
        self.assertIn('data-pruefung="nein"', pre)
        self.assertIn('data-probieren="nein"', pre)


class DieZahlenStimmen(unittest.TestCase):
    def setUp(self):
        self.a = abschnitt()
        quelle = PROGRAMM.read_text(encoding="utf-8")
        self.wert = {name: int(wert) for wert, name in
                     re.findall(r"^Merke (\d+) als (\w+)\.", quelle, re.M)}

    def test_das_gitter(self):
        b, h = self.wert["Breite"], self.wert["Hoehe"]
        self.assertIn(f"{b} mal {h} Zellen", self.a)
        self.assertIn(f"{b * h} Zellen,", self.a)

    def test_die_generationen(self):
        self.assertEqual(self.wert["Generationen"], 30,
                         "Steht hier eine andere Zahl, muss auch 'dreißig' auf der Seite weichen.")
        self.assertIn("dreißig Generationen", self.a)

    def test_die_leinwand(self):
        b = self.wert["Breite"] * self.wert["Zelle"]
        h = self.wert["Hoehe"] * self.wert["Zelle"]
        self.assertIn(f"Nimm die Leinwand {b} mal {h}.", entschluesselt(self.a))


class DerKnopfLaedtEinEchtesBeispiel(unittest.TestCase):
    def test_jedes_genannte_beispiel_gibt_es(self):
        ids = {e["id"] for e in json.loads(
            (WURZEL / "playground" / "beispiele.json").read_text(encoding="utf-8"))}
        genannt = re.findall(r'data-beispiel="([^"]+)"', SEITE.read_text(encoding="utf-8"))
        self.assertTrue(genannt, "Kein Werkstück lädt mehr ein Beispiel.")
        for name in genannt:
            with self.subTest(beispiel=name):
                self.assertIn(name, ids)

    def test_der_weiterfuehrende_link_zeigt_auf_dasselbe_programm(self):
        a = abschnitt()
        beispiel = re.search(r'data-beispiel="([^"]+)"', a).group(1)
        self.assertIn(f'spielplatz.html#beispiel={beispiel}', a)

    def test_die_demo_hat_alles_was_das_skript_braucht(self):
        a = abschnitt()
        for teil in ("mini-start", "mini-buehne", "mini-hinweis"):
            with self.subTest(teil=teil):
                self.assertIn(teil, a)


if __name__ == "__main__":
    unittest.main()
