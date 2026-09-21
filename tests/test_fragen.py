"""Der Abschnitt „Harte Fragen" — er ist nur etwas wert, wenn er ehrlich bleibt.

Eine FAQ, die sich selbst lobt, ist schlimmer als keine: Sie nimmt den Platz ein, an
dem ein Leser die Einwände erwartet. Deshalb wird hier geprüft, dass die unbequemen
Fragen wirklich dastehen — und dass die Antworten die Grenzen des Projekts benennen,
statt sie wegzureden.
"""
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITE = WURZEL / "webseite" / "seiten" / "fragen.html"
STARTSEITE = WURZEL / "webseite" / "seiten" / "index.html"


def abschnitt():
    t = SEITE.read_text(encoding="utf-8")
    anfang = t.index('<section class="section" id="fragen">')
    return t[anfang:t.index("</section>", anfang)]


def text(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class DieFragen(unittest.TestCase):
    def setUp(self):
        self.a = abschnitt()
        self.fragen = re.findall(r"<h3>([^<]+)</h3>", self.a)

    def test_der_abschnitt_steht_auf_der_eigenen_seite_und_ist_von_der_startseite_verlinkt(self):
        """Seit dem Umbau der Startseite (21.09.2026) ist „Harte Fragen" eine eigene Seite —
        die Startseite verweist über eine Kachel im Abschnitt „Weiterlesen" dorthin."""
        self.assertIn('id="fragen"', SEITE.read_text(encoding="utf-8"))
        self.assertIn('href="fragen.html"', STARTSEITE.read_text(encoding="utf-8"))

    def test_die_unbequemen_fragen_werden_gestellt(self):
        gestellt = " ".join(self.fragen).lower()
        for thema in ("python", "scratch", "deutsch", "erprobt", "unterricht",
                      "neue programmiersprache", "für wen"):
            with self.subTest(thema=thema):
                self.assertIn(thema, gestellt, f"Zu '{thema}' wird keine Frage gestellt.")

    def test_es_sind_wirklich_fragen(self):
        """Eine Überschrift darf zwei Sätze haben — ein Fragezeichen muss aber vorkommen."""
        for frage in self.fragen[:8]:
            with self.subTest(frage=frage):
                self.assertIn("?", frage, "Das ist keine Frage.")

    def test_jede_frage_bekommt_eine_antwort(self):
        for stueck in re.findall(r"<article>(.*?)</article>", self.a, re.S):
            if "<h3>" not in stueck:
                continue
            with self.subTest(frage=re.search(r"<h3>([^<]+)</h3>", stueck).group(1)):
                self.assertGreater(len(text(re.sub(r"<h3>.*?</h3>", "", stueck, flags=re.S))), 120,
                                   "Die Antwort ist zu kurz, um ehrlich zu sein.")


class DieAntwortenBleibenEhrlich(unittest.TestCase):
    def setUp(self):
        self.text = text(abschnitt())

    def test_das_projekt_gibt_seine_grenzen_zu(self):
        for zugestaendnis in ("Bewiesen ist sie nicht", "keine Studie", "Hobbyprojekt",
                              "bleibt offen"):
            with self.subTest(satz=zugestaendnis):
                self.assertIn(zugestaendnis, self.text)

    def test_die_erprobtheit_wird_nicht_behauptet(self):
        stelle = self.text[self.text.index("erprobt") + len("erprobt"):]
        self.assertTrue(stelle.lstrip("? ").startswith("Nein"),
                        "Auf die Frage nach der Erprobung muss als Erstes 'Nein' stehen.")

    def test_die_anderen_ansaetze_werden_nicht_abgewertet(self):
        for abwertung in ("besser als", "die beste", "veraltet", "Spielzeug", "ungeeignet",
                          "überlegen"):
            with self.subTest(wort=abwertung):
                self.assertNotIn(abwertung.lower(), self.text.lower())
        self.assertIn("ein anderer Weg, und ein bewährter", self.text)

    def test_der_ausgang_nach_python_wird_genannt(self):
        self.assertIn("nach Python", self.text)
        self.assertIn("verlassen will", self.text)


class Mitmachen(unittest.TestCase):
    def setUp(self):
        a = abschnitt()
        self.block = a[a.index('<div class="mitmachen">'):]

    def test_die_drei_wege_stehen_da(self):
        for was in ("Unterricht", "Fehler und Ideen", "forken"):
            with self.subTest(weg=was):
                self.assertIn(was, self.block)

    def test_sie_fuehren_wirklich_irgendwohin(self):
        ziele = re.findall(r'href="([^"]+)"', self.block)
        self.assertIn("tutorial.html", ziele)
        self.assertIn("https://github.com/wolfiru/klarsatz/issues", ziele)
        self.assertIn("https://github.com/wolfiru/klarsatz", ziele)

    def test_externe_links_sind_abgesichert(self):
        for link in re.findall(r'<a [^>]*href="https?://[^"]+"[^>]*>', self.block):
            with self.subTest(link=link):
                self.assertIn('rel="noopener"', link)


if __name__ == "__main__":
    unittest.main()
