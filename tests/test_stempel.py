"""Der Versionsstempel muss jede nachgeladene Datei erreichen.

Der Anlass ist ein echter Fehler: Die Startseite lud die Spielwiese über
`await import('./../spielwiese/klarsatz-playground.js')` nach. Das Werkzeug kannte
nur die feste Form `import … from '…'` und ließ diese Zeile ungestempelt. Der
Browser nahm daraufhin den Interpreter aus dem Zwischenspeicher — eine alte Fassung,
die `Beschrifte` noch nicht kannte, während die Seite schon ein Programm damit anbot.
Fehlermeldung: „Ich verstehe den Satz nicht: er beginnt mit 'Beschrifte'."
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
WERKZEUG = WURZEL / "tools" / "stempel_webseite.py"


class Stempeln(unittest.TestCase):
    def baue(self, skript):
        """Legt einen kleinen Webordner an und stempelt ihn."""
        ordner = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, ordner)
        (ordner / "assets").mkdir()
        (ordner / "spielwiese").mkdir()
        (ordner / "index.html").write_text(
            '<script type="module" src="assets/mini.js"></script>', encoding="utf-8")
        (ordner / "assets" / "mini.js").write_text(skript, encoding="utf-8")
        (ordner / "assets" / "design.css").write_text("body { color: red }", encoding="utf-8")
        (ordner / "spielwiese" / "spiel.js").write_text("export const a = 1;", encoding="utf-8")
        (ordner / "spielwiese" / "daten.json").write_text("[]", encoding="utf-8")
        (ordner / "spielwiese" / "paket.zip").write_bytes(b"PK\x03\x04alt")
        self.stempele(ordner)
        return ordner

    def stempele(self, ordner):
        ergebnis = subprocess.run([sys.executable, str(WERKZEUG), str(ordner)],
                                  capture_output=True, text=True)
        self.assertEqual(ergebnis.returncode, 0, ergebnis.stderr)
        return ergebnis.stdout

    def test_nachgeladene_module_bekommen_einen_stempel(self):
        ordner = self.baue("await import('./../spielwiese/spiel.js');")
        self.assertRegex((ordner / "assets" / "mini.js").read_text(encoding="utf-8"),
                         r"spielwiese/spiel\.js\?v=[0-9a-f]{8}")

    def test_feste_einbindungen_auch(self):
        ordner = self.baue("import { a } from '../spielwiese/spiel.js';")
        self.assertRegex((ordner / "assets" / "mini.js").read_text(encoding="utf-8"),
                         r"spielwiese/spiel\.js\?v=[0-9a-f]{8}")

    def test_pfade_in_zeichenketten_auch(self):
        """new URL('spielwiese/daten.json', document.baseURI) — gegen die Seite aufgelöst."""
        ordner = self.baue("fetch(new URL('spielwiese/daten.json', document.baseURI));")
        self.assertRegex((ordner / "assets" / "mini.js").read_text(encoding="utf-8"),
                         r"spielwiese/daten\.json\?v=[0-9a-f]{8}")

    def test_auch_stylesheets_aus_dem_eigenen_ordner(self):
        ordner = self.baue("lade('assets/design.css');")
        self.assertRegex((ordner / "assets" / "mini.js").read_text(encoding="utf-8"),
                         r"assets/design\.css\?v=[0-9a-f]{8}")

    def test_der_stempel_aendert_sich_wenn_sich_die_spielwiese_aendert(self):
        """Entscheidend: Auch eine Datei, auf die niemand direkt verweist — der
        Interpreter als ZIP — muss den Stempel verschieben, denn die Spielwiese
        reicht ihn an ihre eigenen Dateien weiter."""
        skript = "await import('./../spielwiese/spiel.js');"
        ordner = self.baue(skript)
        vorher = re.search(r"\?v=([0-9a-f]{8})", (ordner / "assets" / "mini.js").read_text()).group(1)

        (ordner / "spielwiese" / "paket.zip").write_bytes(b"PK\x03\x04neu und anders")
        (ordner / "assets" / "mini.js").write_text(skript, encoding="utf-8")
        self.stempele(ordner)
        nachher = re.search(r"\?v=([0-9a-f]{8})", (ordner / "assets" / "mini.js").read_text()).group(1)
        self.assertNotEqual(vorher, nachher, "Ein neuer Interpreter muss einen neuen Stempel ergeben.")

    def test_unveraenderte_dateien_behalten_ihren_stempel(self):
        """Sonst lüde jeder Besucher nach jeder Veröffentlichung alles neu."""
        skript = "await import('./../spielwiese/spiel.js');"
        ordner = self.baue(skript)
        vorher = (ordner / "assets" / "mini.js").read_text(encoding="utf-8")
        self.stempele(ordner)
        self.assertEqual((ordner / "assets" / "mini.js").read_text(encoding="utf-8"), vorher)

    def test_fehlende_ziele_werden_gemeldet_und_nicht_gestempelt(self):
        ordner = self.baue("await import('./../spielwiese/gibtsnicht.js');")
        text = (ordner / "assets" / "mini.js").read_text(encoding="utf-8")
        self.assertNotIn("?v=", text)


class DieEchteSeite(unittest.TestCase):
    """Was im Projekt liegt, muss stempelbar sein — sonst nützt das beste Werkzeug nichts."""

    def test_jede_nachgeladene_spielwiesendatei_ist_auffindbar(self):
        from tools.stempel_webseite import IN_JS
        for skript in sorted((WURZEL / "webseite" / "assets").glob("*.js")):
            for _q, pfad, in [(m.group(1), m.group(2)) for m in
                              IN_JS.finditer(skript.read_text(encoding="utf-8"))]:
                with self.subTest(skript=skript.name, pfad=pfad):
                    name = pfad.split("/")[-1]
                    orte = [WURZEL / "playground" / name, WURZEL / "webseite" / "assets" / name]
                    self.assertTrue(any(o.exists() for o in orte),
                                    f"{pfad} wird nachgeladen, liegt aber nirgends im Projekt.")


if __name__ == "__main__":
    unittest.main()
