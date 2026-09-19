"""Die Brücke auf der Startseite: Konzept — Klarsatz — Python.

Die Python-Spalte darf nicht abgetippt sein, sonst wäre die Brücke eine Behauptung. Sie muss
aus demselben Übersetzer kommen, den auch der Knopf „Als Python" benutzt. Genau das wird hier
nachgerechnet: für jede Zeile der Tabelle.
"""
import html
import re
import unittest
from pathlib import Path

from klarsatz.nach_python import nach_python

SEITE = Path(__file__).resolve().parent.parent / "webseite" / "seiten" / "index.html"

ZEILE = re.compile(
    r'<tr>\s*<th scope="row">(?P<konzept>[^<]+)</th>\s*'
    r'<td><pre class="klar"[^>]*>(?P<klar>.*?)</pre></td>\s*'
    r'<td><pre class="schale"><code>(?P<python>.*?)</code></pre></td>\s*</tr>', re.S)


def zeilen():
    text = SEITE.read_text(encoding="utf-8")
    m = re.search(r'<table class="bruecke-tabelle">.*?</table>', text, re.S)
    assert m, "Die Brücken-Tabelle fehlt."
    return [(t.group("konzept"), html.unescape(t.group("klar")), html.unescape(t.group("python")))
            for t in ZEILE.finditer(m.group(0))]


class Bruecke(unittest.TestCase):
    def test_die_tabelle_hat_zeilen(self):
        self.assertGreaterEqual(len(zeilen()), 5)

    def test_jede_zeile_zeigt_die_echte_uebersetzung(self):
        for konzept, klar, python in zeilen():
            with self.subTest(konzept=konzept):
                self.assertEqual(nach_python(klar).strip(), python.strip(),
                                 f"'{konzept}': Die Python-Spalte passt nicht mehr zum Übersetzer.")

    def test_kein_hinweiskopf_in_der_tabelle(self):
        """Erzeugt der Übersetzer Hinweise, stünden sie als Kommentar mit in der Zelle —
        in einer Gegenüberstellung wäre das nur Lärm. Dann lieber das Beispiel ändern."""
        for konzept, klar, _ in zeilen():
            with self.subTest(konzept=konzept):
                self.assertFalse(nach_python(klar).lstrip().startswith("#"),
                                 f"'{konzept}' erzeugt einen Hinweiskopf.")

    def test_die_klarsatz_seite_ist_gueltig(self):
        from klarsatz.interpreter import Interpreter
        for konzept, klar, _ in zeilen():
            with self.subTest(konzept=konzept):
                Interpreter().parse(klar)
