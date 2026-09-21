"""Metadaten, strukturierte Daten und Rechtliches auf allen Seiten.

Ein Analysewerkzeug hat diese Dinge bemängelt; damit sie nicht beim nächsten Umbau
wieder verschwinden, stehen sie hier als Erwartung. Geprüft wird an den Quellen in
webseite/ und an den beiden Seitenbauern — nicht am Webordner, den es auf einem
fremden Rechner nicht gibt.
"""
import json
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SEITEN = sorted((WURZEL / "webseite" / "seiten").glob("*.html"))
BAUER = [WURZEL / "tools" / "baue_tutorial.py", WURZEL / "webseite" / "baue_doku.sh"]


def inhalte(text, muster):
    return re.findall(muster, text)


class JedeSeite(unittest.TestCase):
    def test_beschreibung_ist_da_und_nicht_zu_lang(self):
        """Suchmaschinen schneiden nach rund 160 Zeichen ab."""
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            if 'name="robots" content="noindex"' in text:
                continue                      # die Fehlerseite soll gar nicht gefunden werden
            treffer = re.search(r'<meta name="description" content="([^"]*)"', text)
            with self.subTest(seite=seite.name):
                self.assertIsNotNone(treffer, "keine Beschreibung")
                self.assertLessEqual(len(treffer.group(1)), 170,
                                     f"{len(treffer.group(1))} Zeichen — zu lang")
                self.assertGreater(len(treffer.group(1)), 60)

    def test_og_angaben_sind_vollstaendig_und_einmalig(self):
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            if 'name="robots" content="noindex"' in text:
                continue
            with self.subTest(seite=seite.name):
                for feld in ("og:title", "og:description", "og:url", "og:image", "og:site_name",
                             "og:locale", "og:image:width", "og:image:height", "og:image:alt"):
                    self.assertEqual(len(inhalte(text, f'property="{feld}"')), 1,
                                     f"{feld} fehlt oder steht doppelt")

    def test_twitter_angaben_sind_vollstaendig(self):
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            if 'name="robots" content="noindex"' in text:
                continue
            with self.subTest(seite=seite.name):
                for feld in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
                    self.assertEqual(len(inhalte(text, f'name="{feld}"')), 1, f"{feld} fehlt")

    def test_auch_die_erzeugten_seiten_bekommen_alles(self):
        for bauer in BAUER:
            text = bauer.read_text(encoding="utf-8")
            with self.subTest(bauer=bauer.name):
                for feld in ("og:image:alt", "og:site_name", "twitter:image", "BreadcrumbList",
                             "klarsatz.webmanifest", "color-scheme"):
                    self.assertIn(feld, text)

    def test_farbschema_und_manifest(self):
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            with self.subTest(seite=seite.name):
                self.assertIn('name="color-scheme"', text)
                self.assertIn('rel="manifest"', text)

    def test_rechtliches_in_jeder_fusszeile(self):
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            with self.subTest(seite=seite.name):
                self.assertIn('href="/impressum.html"', text)
                self.assertIn('href="/datenschutz.html"', text, "eigene Datenschutzseite fehlt")
                self.assertIn("LICENSE", text, "Link zur Lizenz fehlt")
                self.assertIn("<time datetime=", text, "Stand-Angabe ohne <time>")

    def test_das_kopfbild_wird_nicht_verzoegert_geladen(self):
        """Es ist der wahrscheinlichste LCP-Kandidat — lazy wäre hier verkehrt."""
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            if "monogram.png" not in text:
                continue
            with self.subTest(seite=seite.name):
                bild = re.search(r'<img src="assets/monogram\.png"[^>]*>', text).group(0)
                self.assertNotIn('loading="lazy"', bild)
                self.assertIn('fetchpriority="high"', bild)

    def test_eigene_skripte_blockieren_nicht(self):
        for seite in SEITEN:
            text = seite.read_text(encoding="utf-8")
            for skript in re.findall(r'<script (?!type="application)[^>]*src="assets/[^>]*>', text):
                with self.subTest(seite=seite.name, skript=skript[:60]):
                    self.assertTrue("defer" in skript or "async" in skript or 'type="module"' in skript)


class StrukturierteDaten(unittest.TestCase):
    def bloecke(self, seite):
        text = seite.read_text(encoding="utf-8")
        return [json.loads(b) for b in
                re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', text, re.S)]

    def test_die_startseite_beschreibt_sich_maschinenlesbar(self):
        daten = self.bloecke(WURZEL / "webseite" / "seiten" / "index.html")
        self.assertTrue(daten, "kein JSON-LD")
        arten = {e["@type"] for block in daten for e in (block if isinstance(block, list) else [block])}
        for art in ("WebSite", "SoftwareSourceCode"):
            self.assertIn(art, arten)

    def test_die_fragen_seite_beschreibt_sich_maschinenlesbar(self):
        """Seit dem Umbau der Startseite (21.09.2026) steht das FAQPage-JSON-LD auf
        fragen.html, wo die Fragen jetzt tatsächlich stehen."""
        daten = self.bloecke(WURZEL / "webseite" / "seiten" / "fragen.html")
        arten = {e["@type"] for block in daten for e in (block if isinstance(block, list) else [block])}
        self.assertIn("FAQPage", arten)

    def test_die_fragen_stammen_von_der_seite(self):
        """Erfundene Antworten in den Daten wären schlimmer als gar keine."""
        seite = WURZEL / "webseite" / "seiten" / "fragen.html"
        text = seite.read_text(encoding="utf-8")
        faq = [e for block in self.bloecke(seite) for e in (block if isinstance(block, list) else [block])
               if e["@type"] == "FAQPage"][0]
        sichtbar = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
        for frage in faq["mainEntity"]:
            with self.subTest(frage=frage["name"][:40]):
                self.assertIn(frage["name"], sichtbar)
                self.assertIn(frage["acceptedAnswer"]["text"][:60], sichtbar)

    def test_die_version_im_json_ld_stimmt(self):
        pyproject = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
        version = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.M).group(1)
        daten = self.bloecke(WURZEL / "webseite" / "seiten" / "index.html")
        software = [e for block in daten for e in (block if isinstance(block, list) else [block])
                    if e["@type"] == "SoftwareSourceCode"][0]
        self.assertEqual(software["version"], version)
        self.assertEqual(software["codeRepository"], "https://github.com/wolfiru/klarsatz")

    def test_unterseiten_haben_brotkrumen(self):
        for name in ("tutorial.html", "doku.html", "aufgaben.html", "spielplatz.html",
                     "einordnung.html", "programme.html", "fuerwen.html", "fragen.html"):
            seite = WURZEL / "webseite" / "seiten" / name
            if not seite.exists():
                continue
            with self.subTest(seite=name):
                arten = {e.get("@type") for block in self.bloecke(seite)
                         for e in (block if isinstance(block, list) else [block])}
                self.assertIn("BreadcrumbList", arten)


class ZahlenImUeberblick(unittest.TestCase):
    """Der Fakten-Block auf der Startseite muss im Projekt nachzählbar sein."""

    def setUp(self):
        self.text = (WURZEL / "webseite" / "seiten" / "index.html").read_text(encoding="utf-8")
        anfang = self.text.index('<dl class="zahlen">')
        self.block = self.text[anfang:self.text.index("</dl>", anfang)]

    def test_die_zahlen_stimmen(self):
        programme = len(list((WURZEL / "programme").glob("*.klar")))
        beispiele = len(list((WURZEL / "beispiele").glob("*.klar")))
        aufgaben = len(json.loads((WURZEL / "playground" / "aufgaben.json").read_text(encoding="utf-8")))
        from klarsatz.sprachdaten import STUFEN
        lektionen = sum(len(re.findall(r"^## Lektion ", (WURZEL / "docs" / d).read_text(encoding="utf-8"), re.M))
                        for d in ("TUTORIAL.md", "TUTORIAL-ZEICHNEN.md"))
        self.assertIn(f"<dt>{programme + beispiele}</dt>", self.block)
        self.assertIn(f"({programme} große, {beispiele} kleine)", self.block)
        self.assertIn(f"<dt>{lektionen}</dt>", self.block)
        self.assertIn(f"<dt>{aufgaben}</dt>", self.block)
        self.assertIn(f"<dt>{len(STUFEN)}</dt>", self.block)


if __name__ == "__main__":
    unittest.main()
