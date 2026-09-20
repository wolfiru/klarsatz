"""Signet und Wortmarke — sie müssen da sein und überall hinzeigen, wo sie sollen.

Eine Marke ist der Teil des Projekts, den man zuerst sieht und zuletzt prüft. Hier wird
nachgesehen, dass die Dateien existieren, gültig sind und von den Seiten auch benutzt
werden — sonst zeigt irgendwann ein Favicon ins Leere, und niemand merkt es.
"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ASSETS = WURZEL / "webseite" / "assets"

SVGS = ["klarsatz-signet.svg", "klarsatz-signet-klein.svg", "klarsatz-signet-blank.svg",
        "klarsatz-signet-auf-hell.svg", "klarsatz-signet-einfarbig.svg",
        "klarsatz-wortmarke.svg", "klarsatz-wortmarke-auf-hell.svg"]
PNGS = ["klarsatz-avatar-512.png", "apple-touch-icon.png", "editor-icon-128.png",
        "klarsatz-vorschau.png"]


class DieDateien(unittest.TestCase):
    def test_alles_da(self):
        for name in SVGS + PNGS:
            with self.subTest(datei=name):
                self.assertTrue((ASSETS / name).exists(), f"{name} fehlt — tools/baue_logo.py läuft.")
                self.assertGreater((ASSETS / name).stat().st_size, 200)

    def test_die_svgs_sind_gueltig_und_beschriftet(self):
        for name in SVGS:
            with self.subTest(datei=name):
                baum = ET.parse(ASSETS / name).getroot()
                self.assertTrue(baum.tag.endswith("svg"))
                text = (ASSETS / name).read_text(encoding="utf-8")
                self.assertIn("<title>Klarsatz</title>", text,
                              "Ohne Titel weiß ein Vorleseprogramm nicht, was das Bild zeigt.")

    def test_die_wortmarke_braucht_keine_schrift(self):
        """Als <text> sähe sie überall anders aus, wo Fraunces fehlt — auf GitHub etwa."""
        text = (ASSETS / "klarsatz-wortmarke.svg").read_text(encoding="utf-8")
        self.assertNotIn("<text", text)
        self.assertNotIn("font-family", text)
        self.assertGreater(text.count("<path"), 6, "Für 'Klarsatz' braucht es acht Buchstaben.")

    def test_die_pngs_sind_pngs_und_quadratisch_wo_noetig(self):
        import struct
        for name, erwartet in (("klarsatz-avatar-512.png", (512, 512)),
                               ("apple-touch-icon.png", (180, 180)),
                               ("editor-icon-128.png", (128, 128)),
                               ("klarsatz-vorschau.png", (1200, 630))):
            with self.subTest(datei=name):
                roh = (ASSETS / name).read_bytes()
                self.assertTrue(roh.startswith(b"\x89PNG"))
                breite, hoehe = struct.unpack(">II", roh[16:24])
                self.assertEqual((breite, hoehe), erwartet)


class WirdAuchBenutzt(unittest.TestCase):
    def test_jede_seite_zeigt_auf_das_signet(self):
        for seite in sorted((WURZEL / "webseite" / "seiten").glob("*.html")):
            with self.subTest(seite=seite.name):
                text = seite.read_text(encoding="utf-8")
                self.assertIn('rel="icon" href="assets/klarsatz-signet-klein.svg"', text)
                self.assertIn('rel="apple-touch-icon"', text)
                self.assertNotIn("data:image/svg+xml,<svg", text,
                                 "Hier steckt noch das alte Favicon im Quelltext.")

    def test_auch_die_erzeugten_seiten(self):
        for bauer in (WURZEL / "webseite" / "baue_doku.sh", WURZEL / "tools" / "baue_tutorial.py"):
            with self.subTest(bauer=bauer.name):
                self.assertIn("klarsatz-signet-klein.svg", bauer.read_text(encoding="utf-8"))

    def test_das_vorschaubild_haengt_an_der_startseite(self):
        text = (WURZEL / "webseite" / "seiten" / "index.html").read_text(encoding="utf-8")
        self.assertIn("klarsatz-vorschau.png", text)
        self.assertIn('name="twitter:card"', text)

    def test_die_readme_zeigt_die_wortmarke_in_beiden_fassungen(self):
        text = (WURZEL / "README.md").read_text(encoding="utf-8")
        self.assertIn("klarsatz-wortmarke.svg", text)
        self.assertIn("klarsatz-wortmarke-auf-hell.svg", text)
        self.assertIn("prefers-color-scheme: dark", text)



class UeberallEingesetzt(unittest.TestCase):
    """Eine Marke wirkt erst, wenn sie an jeder Stelle auftaucht, an der jemand ankommt."""

    def test_die_editor_erweiterung_traegt_das_signet(self):
        import json
        ext = WURZEL / "editor" / "vscode-klarsatz"
        self.assertTrue((ext / "icon.png").exists(), "tools/baue_logo.py legt es an.")
        self.assertEqual(json.loads((ext / "package.json").read_text(encoding="utf-8")).get("icon"),
                         "icon.png")

    def test_es_gibt_eine_einfarbige_fassung(self):
        """Für alles, was nur eine Farbe kennt — Stempel, Ausdruck, Stickerei."""
        text = (ASSETS / "klarsatz-signet-einfarbig.svg").read_text(encoding="utf-8")
        self.assertIn("currentColor", text)
        for farbe in ("#d9b45a", "#f3efe6", "#0c0e0b"):
            self.assertNotIn(farbe, text)

    def test_jede_seite_nennt_ihre_eigene_adresse(self):
        """Ohne canonical zählt eine geteilte Adresse mit Anhängsel als eigene Seite."""
        for seite in sorted((WURZEL / "webseite" / "seiten").glob("*.html")):
            with self.subTest(seite=seite.name):
                text = seite.read_text(encoding="utf-8")
                treffer = re.search(r'rel="canonical" href="([^"]+)"', text)
                self.assertIsNotNone(treffer, "Keine canonical-Angabe.")
                erwartet = "" if seite.name == "index.html" else seite.name
                self.assertEqual(treffer.group(1), f"https://www.ruthner.at/klarsatz/{erwartet}")

    def test_auch_die_erzeugten_seiten_nennen_sie(self):
        for bauer in (WURZEL / "webseite" / "baue_doku.sh", WURZEL / "tools" / "baue_tutorial.py"):
            with self.subTest(bauer=bauer.name):
                self.assertIn('rel="canonical"', bauer.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
