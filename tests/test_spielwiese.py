"""Die Beispiele der Spielwiese: vollständig, ladbar, lauffähig.

Der Browser-Test prüft dasselbe noch einmal durch die Oberfläche — aber nur, wenn Chromium
da ist. Hier geht es ohne Browser, damit die Zusage bei *jedem* Testlauf gilt: Alles, was in
der Auswahlliste steht, lässt sich hineinladen und läuft los.
"""
import json
import unittest
from pathlib import Path

from klarsatz import web
from klarsatz.grenzen import Grenzen
from klarsatz.interpreter import Interpreter

WURZEL = Path(__file__).resolve().parent.parent
LISTE = WURZEL / "playground" / "beispiele.json"

# Antworten für Beispiele, die fragen — sie sollen über die erste Frage hinauskommen.
ANTWORTEN = ["5", "7", "ja", "nein", "1", "2", "Rocco", "42", "n", "x", "ende", "q"]

# Dieses Beispiel führt absichtlich einen Laufzeitfehler vor (Teilen durch null).
ABSICHTLICH_FEHLERHAFT = {"fehler"}

# Die Uhr tickt von sich aus weiter – sie endet nie. Dass sie ins Schrittlimit läuft,
# ist bei ihr der Beweis, dass sie läuft, und kein Fehler.
TICKT_ENDLOS = {"16_uhr"}


class Beispielliste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beispiele = json.loads(LISTE.read_text(encoding="utf-8"))

    def test_die_liste_ist_vollstaendig(self):
        """Jedes .klar aus programme/ und beispiele/ steht in der Auswahl — und nichts sonst."""
        dateien = {p.stem for p in (WURZEL / "programme").glob("*.klar")}
        dateien |= {p.stem for p in (WURZEL / "beispiele").glob("*.klar")}
        in_liste = {b["id"] for b in self.beispiele}
        self.assertEqual(sorted(dateien - in_liste), [],
                         "Diese Programme fehlen in der Spielwiese — tools/baue_playground.py laufen lassen.")
        self.assertEqual(sorted(in_liste - dateien), [],
                         "Diese Einträge der Spielwiese haben keine Datei mehr.")

    def test_jeder_eintrag_hat_was_er_braucht(self):
        for b in self.beispiele:
            with self.subTest(beispiel=b.get("id")):
                for feld in ("id", "gruppe", "titel", "code"):
                    self.assertTrue(b.get(feld) not in (None, ""), f"'{feld}' fehlt")
                self.assertIn("fragt", b)

    def test_der_code_stimmt_mit_der_datei_ueberein(self):
        for b in self.beispiele:
            with self.subTest(beispiel=b["id"]):
                for ordner in ("programme", "beispiele"):
                    datei = WURZEL / ordner / f"{b['id']}.klar"
                    if datei.exists():
                        self.assertEqual(b["code"], datei.read_text(encoding="utf-8"))
                        break
                else:
                    self.fail("keine Datei gefunden")

    def test_jedes_beispiel_laesst_sich_lesen(self):
        """Hineinladen heißt: Der Parser versteht es. Das muss für alle gelten."""
        for b in self.beispiele:
            with self.subTest(beispiel=b["id"]):
                Interpreter().parse(b["code"])

    def test_jedes_beispiel_laeuft_los(self):
        """Bis zum Ende, bis zur ersten Frage oder bis zum Takt — nur nicht mit einem Fehler."""
        grenzen = Grenzen(schritte=300_000, sekunden=5, warte=0)
        for b in self.beispiele:
            with self.subTest(beispiel=b["id"]):
                ergebnis = web.laufe(b["code"], antworten=ANTWORTEN, seed=42, grenzen=grenzen)
                if b["id"] in ABSICHTLICH_FEHLERHAFT:
                    self.assertEqual(ergebnis.zustand, "fehler")
                    continue
                if b["id"] in TICKT_ENDLOS:
                    self.assertEqual(ergebnis.fehlerart, "limit")
                    self.assertTrue(ergebnis.verlauf, "auch eine tickende Uhr muss etwas anzeigen")
                    continue
                self.assertIn(ergebnis.zustand, ("fertig", "wartet"),
                              f"{b['id']} bricht ab:\n{ergebnis.fehler}")

    def test_die_angabe_ob_gefragt_wird_stimmt(self):
        """Die Spielwiese blendet das Antwortfeld danach ein."""
        for b in self.beispiele:
            with self.subTest(beispiel=b["id"]):
                self.assertEqual(b["fragt"], "Frage " in b["code"])

    def test_beispiele_sind_ohne_lernstufe_gedacht(self):
        """Ein geladenes Beispiel darf nie an einer Lernstufe scheitern — die Spielwiese
        setzt die Stufe beim Laden zurück. Hier wird geprüft, dass ohne Stufe wirklich
        nichts gesperrt ist."""
        for b in self.beispiele:
            with self.subTest(beispiel=b["id"]):
                ergebnis = web.laufe(b["code"], antworten=ANTWORTEN, seed=42,
                                     grenzen=Grenzen(schritte=50_000, sekunden=5, warte=0), stufe=None)
                self.assertNotEqual(ergebnis.fehlerart, "stufe")


if __name__ == "__main__":
    unittest.main()
