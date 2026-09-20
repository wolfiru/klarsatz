"""Was an mehreren Stellen steht, muss überall dasselbe sagen.

Die Version steht in sieben Dateien, die Zahl der Programme in vier. Solche Angaben
veralten leise: Beim Sprung auf 0.8.1 blieb die Übergabe auf 0.8.0 stehen, und das
fiel erst beim Nachfragen auf. Hier wird alles gegen eine einzige Quelle geprüft —
pyproject.toml für die Version, die Ordner für die Zahlen.
"""
import json
import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent


def version():
    text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)


class Version(unittest.TestCase):
    def test_das_paket_nennt_dieselbe(self):
        import klarsatz
        self.assertEqual(klarsatz.__version__, version())

    def test_die_editor_erweiterung_nennt_dieselbe(self):
        paket = json.loads((WURZEL / "editor" / "vscode-klarsatz" / "package.json")
                           .read_text(encoding="utf-8"))
        self.assertEqual(paket["version"], version())

    def test_die_uebergabe_nennt_dieselbe(self):
        kopf = (WURZEL / "ÜBERGABE.md").read_text(encoding="utf-8").splitlines()[0]
        self.assertIn(version(), kopf, f"Die Kopfzeile der Übergabe lautet: {kopf}")

    def test_die_sprachdefinition_nennt_dieselbe(self):
        kopf = (WURZEL / "docs" / "SPRACHE.md").read_text(encoding="utf-8").splitlines()[0]
        self.assertIn(version(), kopf, f"Die Kopfzeile der Sprachdefinition lautet: {kopf}")

    def test_der_changelog_fuehrt_sie_ganz_oben(self):
        zeilen = (WURZEL / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
        ueberschriften = [z for z in zeilen if z.startswith("## ")]
        self.assertEqual(ueberschriften[0], f"## {version()}",
                         "Die neueste Version steht nicht als erste im Changelog.")

    def test_keine_alte_nummer_in_den_quellen_der_webseite(self):
        """Die Seiten tragen die Nummer selbst, damit zwischen Veröffentlichen und
        Archivbau nie eine alte sichtbar ist — auch die Doku-Kapitel."""
        quellen = (sorted((WURZEL / "webseite" / "seiten").glob("*.html"))
                   + sorted((WURZEL / "webseite" / "kapitel").glob("*.html")))
        for seite in quellen:
            text = seite.read_text(encoding="utf-8")
            for gefunden in re.findall(r'data-download="version">([^<]+)<', text):
                with self.subTest(seite=seite.name):
                    self.assertEqual(gefunden, version())


class Zahlen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programme = len(list((WURZEL / "programme").glob("*.klar")))

    def test_die_uebergabe_zaehlt_die_programme_richtig(self):
        wort = {20: "zwanzig", 21: "einundzwanzig", 22: "zweiundzwanzig",
                23: "dreiundzwanzig"}[self.programme]
        self.assertIn(f"{wort} Beispielprogramme",
                      (WURZEL / "ÜBERGABE.md").read_text(encoding="utf-8"))

    def test_jedes_programm_steht_in_der_programmliste(self):
        doku = (WURZEL / "docs" / "PROGRAMME.md").read_text(encoding="utf-8")
        for datei in sorted((WURZEL / "programme").glob("*.klar")):
            with self.subTest(programm=datei.name):
                self.assertIn(f"`{datei.name}`", doku)

    def test_die_programmliste_erfindet_nichts(self):
        doku = (WURZEL / "docs" / "PROGRAMME.md").read_text(encoding="utf-8")
        vorhanden = {p.name for p in (WURZEL / "programme").glob("*.klar")}
        for genannt in re.findall(r"`(\d\d_[a-z_]+\.klar)`", doku):
            with self.subTest(programm=genannt):
                self.assertIn(genannt, vorhanden)


class JederSatzDerSpracheStehtInDerDoku(unittest.TestCase):
    """Ein neuer Satz, den niemand nachschlagen kann, ist ein halber Satz."""

    @classmethod
    def setUpClass(cls):
        def lies(*pfade):
            return " ".join(re.sub(r"\s+", " ", (WURZEL / p).read_text(encoding="utf-8")).lower()
                            for p in pfade)
        cls.sprache = lies("docs/SPRACHE.md")
        cls.referenz = lies("webseite/kapitel/referenz.html")
        cls.kapitel = lies(*[f"webseite/kapitel/{d.name}" for d in
                             sorted((WURZEL / "webseite" / "kapitel").glob("*.html"))])

    def test_jeder_satzanfang_ist_nachschlagbar(self):
        from klarsatz.parser import STARTER
        for _norm, (_fn, anzeige) in sorted(STARTER.items()):
            with self.subTest(satz=anzeige):
                self.assertIn(anzeige.lower(), self.sprache, "fehlt in docs/SPRACHE.md")
                self.assertIn(anzeige.lower(), self.referenz, "fehlt im Referenzkapitel")
                self.assertIn(anzeige.lower(), self.kapitel, "fehlt in den Doku-Kapiteln")



class Gliederung(unittest.TestCase):
    def test_die_sprachdefinition_ist_lueckenlos_nummeriert(self):
        """Kapitel wie „Zeichnen (neu)" standen jahrelang ohne Nummer hinten dran."""
        text = (WURZEL / "docs" / "SPRACHE.md").read_text(encoding="utf-8")
        nummern = [int(n) for n in re.findall(r"^## (\d+)\. ", text, re.M)]
        self.assertEqual(nummern, list(range(1, len(nummern) + 1)))
        ohne_nummer = [z for z in re.findall(r"^## (?!\d)(.*)$", text, re.M)]
        self.assertEqual(ohne_nummer, [], "Diese Kapitel haben keine Nummer.")

    def test_die_grenzen_stehen_am_ende(self):
        text = (WURZEL / "docs" / "SPRACHE.md").read_text(encoding="utf-8")
        kapitel = re.findall(r"^## .*$", text, re.M)
        self.assertIn("Bekannte Grenzen", kapitel[-1])


class BehauptungenDerDoku(unittest.TestCase):
    """Was die Doku unter „Bekannte Grenzen" behauptet, wird hier ausgeführt.

    Drei dieser Sätze stimmten nicht mehr: Bedingungen ließen sich längst klammern,
    eine Liste ließ sich längst zu Text verketten, und ein Komma in der *Antwort* war
    längst erlaubt. Solche Sätze altern lautlos — also führt der Test sie aus.
    """

    def laufe(self, quelle, antworten=()):
        from klarsatz import Interpreter
        aus, vorrat = [], iter(antworten)
        Interpreter(ausgabe=aus.append, eingabe=lambda f="": next(vorrat)).lauf(quelle)
        return aus

    def test_im_quelltext_der_punkt_in_der_antwort_das_komma(self):
        self.assertEqual(self.laufe("Zeige 3.5 plus 1."), ["4,5"])
        self.assertEqual(
            self.laufe('Frage "Zahl?" und merke die Antwort als Zahl.\nZeige Zahl plus 1.', ["3,5"]),
            ["4,5"])

    def test_bedingungen_lassen_sich_klammern(self):
        self.assertEqual(
            self.laufe("Merke 1 als a.\nMerke 3 als b.\n"
                       'Wenn (a gleich 1 oder a gleich 2) und b gleich 3 ist:\n'
                       '    Zeige "ja".\nEnde.'),
            ["ja"])

    def test_eine_liste_wird_zu_text(self):
        self.assertEqual(
            self.laufe('Erstelle eine Liste namens L mit "a" und "b".\n'
                       'Zeige Verkettet von L mit ", ".'),
            ["a, b"])

    def test_die_kurzform_von_wenn_fuehrt_genau_einen_satz_aus(self):
        self.assertEqual(self.laufe('Wenn 1 gleich 2 ist, zeige "a". Zeige "b".'), ["b"])

    def test_aufgabenargumente_binden_enger_als_das_rechnen(self):
        """Quadrat von x plus 1 heißt (Quadrat von x) plus 1."""
        self.assertEqual(
            self.laufe("Definiere Aufgabe Quadrat von x:\n    Gib x mal x zurück.\nEnde.\n"
                       "Zeige Quadrat von 3 plus 1."),
            ["10"])

    def test_abwaerts_zaehlt_nur_wer_rueckwaerts_sagt(self):
        self.assertEqual(self.laufe("Zähle von 5 bis 1 mit i:\n    Zeige i.\nEnde."), [])
        self.assertEqual(
            self.laufe("Zähle von 3 bis 1 rückwärts mit i:\n    Zeige i.\nEnde."), ["3", "2", "1"])

    def test_feldnamen_stehen_wie_in_der_definition(self):
        self.assertEqual(
            self.laufe("Ein Hund hat einen Namen und ein Alter.\n"
                       'Erschaffe einen Hund mit Name "Rocco" und Alter 5 als R.\nZeige R.'),
            ["Hund(Namen: Rocco, Alter: 5)"])


if __name__ == "__main__":
    unittest.main()
