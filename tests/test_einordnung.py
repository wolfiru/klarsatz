"""Der Abschnitt „Wo Klarsatz steht“ — Vergleich und Karte der Lernsprachen.

Der Abschnitt ordnet Klarsatz zwischen anderen Lernsprachen ein. Das ist heikler als
es aussieht: Sobald jemand eine Zeile ergänzt, muss sie auch in der Karte und in der
Liste für schmale Bildschirme auftauchen, sonst zeigen die drei Darstellungen
Verschiedenes. Und der Abschnitt darf nicht in Werbung kippen — deshalb steht hier
auch eine Liste von Sätzen, die er nicht sagen darf.
"""
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITE = WURZEL / "webseite" / "seiten" / "index.html"

PROJEKTE = ["Logo", "Niki, der Roboter", "Robot Karol", "Scratch",
            "Guido van Robot", "Python", "Klarsatz"]


def quelltext():
    return SEITE.read_text(encoding="utf-8")


def abschnitt():
    t = quelltext()
    anfang = t.index('<section class="section" id="einordnung">')
    return t[anfang:t.index("</section>", anfang)]


def ohne_tags(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class Aufbau(unittest.TestCase):
    def test_der_abschnitt_steht_auf_der_seite_und_im_menue(self):
        t = quelltext()
        self.assertIn('id="einordnung"', t)
        self.assertIn('<a href="#einordnung">Einordnung</a>', t)

    def test_die_abschnitte_sind_lueckenlos_durchnummeriert(self):
        """Ein eingeschobener Abschnitt verschiebt alle folgenden Nummern."""
        nummern = [int(n) for n in re.findall(r'class="eyebrow">(\d\d) — ', quelltext())]
        self.assertEqual(nummern, list(range(1, len(nummern) + 1)))

    def test_der_abschnitt_steht_vor_der_sprache_und_nach_fuer_wen(self):
        t = quelltext()
        self.assertLess(t.index('id="fuerwen"'), t.index('id="einordnung"'))
        self.assertLess(t.index('id="einordnung"'), t.index('id="bausteine"'))


class Tabelle(unittest.TestCase):
    def setUp(self):
        self.a = abschnitt()
        self.tabelle = self.a[self.a.index('<table class="einordnung">'):self.a.index("</table>")]

    def test_jedes_projekt_hat_eine_zeile(self):
        koepfe = [ohne_tags(z).split("  ")[0]
                  for z in re.findall(r'<th scope="row">(.*?)</th>', self.tabelle, re.S)]
        for name in PROJEKTE:
            with self.subTest(projekt=name):
                self.assertTrue(any(k.startswith(name) for k in koepfe),
                                f"{name} fehlt in der Vergleichstabelle.")
        self.assertEqual(len(koepfe), len(PROJEKTE))

    def test_jede_zelle_traegt_ihre_spalte_mit(self):
        """Auf schmalen Bildschirmen fällt die Kopfzeile weg — dann steht die Spalte
        über data-spalte vor dem Wert. Fehlt sie, steht dort nur noch „deutsch“."""
        spalten = re.findall(r'<th scope="col">([^<]+)</th>', self.tabelle)[1:]
        zeilen = re.findall(r"<tr[^>]*>(.*?)</tr>", self.tabelle, re.S)[1:]
        self.assertEqual(len(zeilen), len(PROJEKTE))
        for zeile in zeilen:
            gefunden = re.findall(r'<td data-spalte="([^"]+)"', zeile)
            self.assertEqual(gefunden, spalten)

    def test_klarsatz_ist_markiert_aber_nicht_nur_durch_farbe(self):
        zeile = [z for z in re.findall(r"<tr[^>]*>.*?</tr>", self.tabelle, re.S)
                 if "Klarsatz" in z][0]
        self.assertIn('class="ist-klarsatz"', zeile)
        self.assertIn("diese Seite", ohne_tags(zeile))


class Karte(unittest.TestCase):
    def setUp(self):
        self.a = abschnitt()
        self.svg = self.a[self.a.index("<svg"):self.a.index("</svg>")]

    def test_die_karte_ist_beschriftet(self):
        self.assertIn('role="img"', self.svg)
        self.assertIn('aria-labelledby="ein-karte-titel ein-karte-text"', self.svg)
        self.assertIn('<title id="ein-karte-titel">', self.svg)
        self.assertIn('<desc id="ein-karte-text">', self.svg)

    def test_die_textfassung_nennt_jedes_projekt(self):
        """Wer die Karte nicht sehen kann, bekommt dieselbe Aussage als Text."""
        beschreibung = ohne_tags(re.search(r"<desc[^>]*>(.*?)</desc>", self.svg, re.S).group(1))
        for name in PROJEKTE:
            with self.subTest(projekt=name):
                self.assertIn(name.split(",")[0], beschreibung)

    def test_karte_liste_und_tabelle_zeigen_dieselben_projekte(self):
        in_karte = re.findall(r'<text class="d-name"[^>]*>([^<]+)</text>', self.svg)
        liste = self.a[self.a.index('<ul class="ein-liste">'):self.a.index("</ul>")]
        in_liste = re.findall(r'<span class="ein-liste-wer">([^<]+)</span>', liste)
        self.assertEqual(sorted(in_karte), sorted(PROJEKTE))
        self.assertEqual(sorted(in_liste), sorted(PROJEKTE))

    def test_die_achsen_haben_zwei_pole_und_keine_richtung(self):
        """Ein einzelner Pfeil nach oben würde behaupten, oben sei mehr wert."""
        self.assertEqual(self.svg.count('class="d-spitze"'), 4)

    def test_die_positionen_sind_als_schematisch_gekennzeichnet(self):
        text = ohne_tags(self.a)
        self.assertIn("schematisch", text)
        self.assertIn("keine Messwerte", text)


class Fairness(unittest.TestCase):
    """Der Abschnitt vergleicht — er darf nicht werten."""

    VERBOTEN = [
        "die beste", "am besten", "Zukunft des Programmierens", "ungeeignet",
        "Spielzeug", "veraltet", "überlegen", "Sieger", "Konkurrenz",
        "löst das Syntaxproblem", "ersetzt Python", "ersetzt Scratch",
    ]

    def test_keine_wertenden_saetze(self):
        text = ohne_tags(abschnitt())
        for satz in self.VERBOTEN:
            with self.subTest(formulierung=satz):
                self.assertNotIn(satz.lower(), text.lower())

    def test_besser_als_kommt_nur_in_der_verneinung_vor(self):
        """„Oben ist nicht besser als unten“ darf stehen — „besser als Scratch“ nicht."""
        text = ohne_tags(abschnitt()).lower()
        for stelle in re.finditer(r"besser als", text):
            davor = text[max(0, stelle.start() - 6):stelle.start()]
            with self.subTest(stelle=text[stelle.start() - 30:stelle.end() + 20]):
                self.assertIn("nicht ", davor)

    def test_der_anspruch_ist_als_annahme_gekennzeichnet(self):
        text = ohne_tags(abschnitt())
        self.assertIn("kein nachgewiesener Vorteil", text)
        self.assertIn("Annahme", text)

    def test_klarsatz_tritt_nicht_als_ersatz_fuer_python_auf(self):
        text = ohne_tags(abschnitt())
        self.assertIn("auch nicht, Python zu ersetzen", text)
        self.assertIn("erster Schritt", text)

    def test_die_quellen_sind_verlinkt(self):
        quellen = abschnitt()
        for ziel in ("de.wikipedia.org/wiki/Bildungsorientierte_Programmiersprache",
                     "de.wikipedia.org/wiki/Logo_(Programmiersprache)",
                     "de.wikipedia.org/wiki/Robot_Karol",
                     "gvr.sourceforge.net",
                     "scratch.mit.edu"):
            with self.subTest(quelle=ziel):
                self.assertIn(ziel, quellen)

    def test_externe_links_sind_abgesichert(self):
        for link in re.findall(r'<a href="https?://[^"]+"[^>]*>', abschnitt()):
            with self.subTest(link=link):
                self.assertIn('rel="noopener"', link)


if __name__ == "__main__":
    unittest.main()
