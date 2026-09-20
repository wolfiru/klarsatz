"""Der Abschnitt „Was damit geht" darf nicht von den Programmen abweichen.

Auf der Startseite steht zu jedem Werkstück ein Ausschnitt aus einem echten Programm,
dazu Zahlen (Gitter, Generationen, Orte, Straßen) und ein Knopf, der genau dieses
Programm lädt. Alle diese Angaben stammen aus einer Datei im Ordner programme/ —
dieser Test rechnet nach, dass sie es auch bleiben. Sonst zeigt die Seite irgendwann
einen Ausschnitt, den es so nicht mehr gibt.
"""
import json
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITE = WURZEL / "webseite" / "seiten" / "index.html"


def abschnitt():
    t = SEITE.read_text(encoding="utf-8")
    anfang = t.index('<section class="section" id="komplex">')
    return t[anfang:t.index("</section>", anfang)]


def werkstuecke():
    """Jedes Werkstück mit seinem Programm: [(Kennung, HTML, Quelltext), …]"""
    stuecke = re.findall(r'<article class="werk">(.*?)</article>', abschnitt(), re.S)
    ergebnis = []
    for html in stuecke:
        kennung = re.search(r'data-beispiel="([^"]+)"', html).group(1)
        quelle = (WURZEL / "programme" / f"{kennung}.klar").read_text(encoding="utf-8")
        ergebnis.append((kennung, html, quelle))
    return ergebnis


def ohne_entities(html):
    return (html.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
                .replace("&amp;", "&").replace("&#8209;", "-"))


class JedesWerkstueck(unittest.TestCase):
    def setUp(self):
        self.werke = werkstuecke()

    def test_es_gibt_welche(self):
        self.assertGreaterEqual(len(self.werke), 2)

    def test_jede_gezeigte_zeile_steht_so_im_programm(self):
        for kennung, html, quelle in self.werke:
            block = re.search(r'<pre class="klar"[^>]*>(.*?)</pre>', html, re.S).group(1)
            for zeile in ohne_entities(block).strip().split("\n"):
                with self.subTest(werk=kennung, zeile=zeile.strip()):
                    self.assertIn(zeile.strip(), quelle,
                                  "Diese Zeile steht so nicht mehr im Programm.")

    def test_der_ausschnitt_wird_nicht_ausgefuehrt_und_nicht_verlinkt(self):
        """Ein paar Zeilen aus der Mitte laufen für sich allein nicht."""
        for kennung, html, _quelle in self.werke:
            with self.subTest(werk=kennung):
                pre = re.search(r'<pre class="klar"([^>]*)>', html).group(1)
                self.assertIn('data-pruefung="nein"', pre)
                self.assertIn('data-probieren="nein"', pre)

    def test_das_beispiel_gibt_es_wirklich(self):
        ids = {e["id"] for e in json.loads(
            (WURZEL / "playground" / "beispiele.json").read_text(encoding="utf-8"))}
        for kennung, html, _quelle in self.werke:
            with self.subTest(werk=kennung):
                self.assertIn(kennung, ids)
                self.assertIn(f'spielplatz.html#beispiel={kennung}', html)

    def test_die_demo_hat_alles_was_das_skript_braucht(self):
        for kennung, html, _quelle in self.werke:
            for teil in ("mini-start", "mini-buehne", "mini-hinweis"):
                with self.subTest(werk=kennung, teil=teil):
                    self.assertIn(teil, html)


class DieZahlenStimmen(unittest.TestCase):
    """Was die Seite über ein Programm behauptet, muss im Programm nachzählbar sein."""

    def werk(self, kennung):
        return next(w for w in werkstuecke() if w[0] == kennung)

    def test_spiel_des_lebens(self):
        _k, html, quelle = self.werk("21_spiel_des_lebens")
        wert = {name: int(w) for w, name in re.findall(r"^Merke (\d+) als (\w+)\.", quelle, re.M)}
        self.assertIn(f"{wert['Breite']} mal {wert['Hoehe']} Zellen", html)
        self.assertIn(f"{wert['Breite'] * wert['Hoehe']} Zellen,", html)
        self.assertEqual(wert["Generationen"], 30)
        self.assertIn("dreißig Generationen", html)
        self.assertIn(f"Nimm die Leinwand {wert['Breite'] * wert['Zelle']} "
                      f"mal {wert['Hoehe'] * wert['Zelle']}.", ohne_entities(html))

    def test_routenplaner(self):
        _k, html, quelle = self.werk("22_routenplaner")
        orte = re.findall(r'"([^"]+)" als (-?\d+)',
                          quelle[quelle.index("namens Ostwert"):quelle.index("namens Nordwert")])
        strassen = re.findall(r'"([^"|]+\|[^"]+)" als \d+',
                              quelle[quelle.index("namens Strecken"):])
        self.assertEqual(len(orte), 12, "Die Seite sagt „Zwölf Orte“.")
        self.assertEqual(len(strassen), 19, "Die Seite sagt „neunzehn Straßen“.")
        self.assertIn("Zwölf Orte", html)
        self.assertIn("neunzehn Straßen", html)

    def test_die_karte_wird_nicht_fuer_mehr_ausgegeben_als_sie_ist(self):
        """Erfundene Kilometer wären die unangenehmste Art, falsch zu liegen."""
        _k, html, _q = self.werk("22_routenplaner")
        self.assertIn("gerundete", html)


if __name__ == "__main__":
    unittest.main()
