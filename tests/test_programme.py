"""Tests für die Programme in programme/ – ein simulierter Mensch beantwortet die 'Frage'-Zeilen.

    python3 -m unittest -v test_programme
"""
import os
import random
import re
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from klarsatz import Interpreter

PROGRAMME = Path(__file__).resolve().parent.parent / "programme"


class Sitzung:
    """Ablauf eines Programms wie im Terminal: Ausgaben, Fragen samt Antworten."""

    def __init__(self, protokoll, uebrig):
        self.zeilen = protokoll
        self.text = "\n".join(protokoll)
        self.uebrig = uebrig          # nicht verbrauchte Antworten

    def __contains__(self, s):
        return s in self.text

    def anzahl(self, s):
        return self.text.count(s)


def spiele(datei, antworten, seed=1, **kw):
    """antworten: Liste fester Antworten ODER Funktion f(frage, protokoll) -> Antwort."""
    quelle = (PROGRAMME / datei).read_text(encoding="utf-8")
    protokoll, rest = [], (list(antworten) if not callable(antworten) else [])

    def eingabe(frage=""):
        if callable(antworten):
            a = antworten(frage, protokoll)
        elif rest:
            a = rest.pop(0)
        else:
            raise EOFError
        a = str(a)
        protokoll.append(frage + a)
        return a

    Interpreter(ausgabe=protokoll.append, eingabe=eingabe, zufall=random.Random(seed),
                max_schritte=kw.pop("max_schritte", 5_000_000), **kw).lauf(quelle)
    return Sitzung(protokoll, rest)


@contextmanager
def leeres_verzeichnis():
    alt = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            yield Path(d)
        finally:
            os.chdir(alt)


class Taschenrechner(unittest.TestCase):
    def test_rechenarten_und_fehler(self):
        s = spiele("03_taschenrechner.klar", [
            "+", 2, 3,            "/", 7, 2,          "/", 1, 0,
            "%", 7, 3,            "^", 2, 10,         "x",
            "*", "abc", 4,        "-", "10", "4,5",   "ENDE"])
        self.assertIn("2 + 3 = 5", s)
        self.assertIn("7 / 2 = 3,5", s)
        self.assertIn("Das geht nicht: Durch null kann man nicht teilen.", s)
        self.assertIn("7 % 3 = 1", s)
        self.assertIn("2 ^ 10 = 1024", s)
        self.assertIn("Diese Rechenart kenne ich nicht.", s)
        self.assertIn("Das sind keine Zahlen.", s)
        self.assertIn("10 - 4,5 = 5,5", s)
        self.assertIn("Tschüss!", s)
        self.assertEqual(s.uebrig, [])


class Primzahlen(unittest.TestCase):
    def test_alle_menuepunkte(self):
        s = spiele("05_primzahlen.klar", [
            1, "abc", 2.5, 0, 200000, 7,      # ungültige Eingaben werden erneut gefragt
            1, 9,
            1, 1,
            2, 30,
            3, 12,
            3, 13,
            2, 1,
            9,                                # unbekannter Menüpunkt
            0])
        self.assertEqual(s.anzahl("Bitte eine ganze Zahl ab 1 eingeben."), 3)
        self.assertIn("zu groß", s)
        self.assertIn("7 ist eine Primzahl.", s)
        self.assertIn("9 ist keine Primzahl.", s)
        self.assertIn("1 ist keine Primzahl.", s)
        self.assertIn("[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]", s)
        self.assertIn("Anzahl: 10", s)
        self.assertIn("Teiler von 12: [1, 2, 3, 4, 6, 12]", s)
        self.assertIn("Teiler von 13: [1, 13]", s)
        self.assertIn("also ist 13 eine Primzahl", s)
        self.assertIn("Anzahl: 0", s)
        self.assertIn("Das habe ich nicht verstanden.", s)
        self.assertEqual(s.uebrig, [])

    def test_gegen_python_nachgerechnet(self):
        def prim(n):
            return n > 1 and all(n % t for t in range(2, int(n ** 0.5) + 1))
        s = spiele("05_primzahlen.klar", [2, 500, 0])
        erwartet = [n for n in range(2, 501) if prim(n)]
        self.assertIn("[" + ", ".join(map(str, erwartet)) + "]", s)
        self.assertIn(f"Anzahl: {len(erwartet)}", s)


class Umrechner(unittest.TestCase):
    def test_umrechnungen(self):
        s = spiele("04_umrechner.klar", [
            1, 100,
            1, "36,6",
            2, 212,
            3, 10,
            4, "26.2",
            5, 100, 0, "1,1",         # Kurs 0 wird abgelehnt
            6, "abc", 55, "1,1",      # 'abc' ist keine Zahl
            0])
        self.assertIn("100 °C = 212,00 °F", s)
        self.assertIn("36,6 °C = 97,88 °F", s)
        self.assertIn("212 °F = 100,00 °C", s)
        self.assertIn("10 km = 6,21 Meilen", s)
        self.assertIn("26,2 Meilen = 42,16 km", s)
        self.assertIn("Der Kurs muss größer als 0 sein.", s)
        self.assertIn("100,00 Euro = 110,00 Fremdwährung", s)
        self.assertIn("Das ist keine Zahl – bitte nochmal.", s)
        self.assertIn("55,00 Fremdwährung = 50,00 Euro", s)
        self.assertEqual(s.uebrig, [])


class Notenrechner(unittest.TestCase):
    def test_auswertung(self):
        s = spiele("06_notenrechner.klar", [1, 2, "x", 6, 0, 5, "2", ""])
        self.assertIn("Das ist keine Zahl.", s)
        self.assertEqual(s.anzahl("Bitte eine Note von 1 bis 5."), 2)
        self.assertIn("Anzahl der Noten: 4", s)
        self.assertIn("Sortiert: [1, 2, 2, 5]", s)
        self.assertIn("Beste Note: 1", s)
        self.assertIn("Schlechteste Note: 5", s)
        self.assertIn("Durchschnitt: 2,50", s)
        self.assertIn("Achtung: 1 x Nicht genügend.", s)

    def test_keine_noten(self):
        self.assertIn("Es wurden keine Noten eingegeben.", spiele("06_notenrechner.klar", [""]))

    def test_ohne_fuenfer_keine_warnung(self):
        s = spiele("06_notenrechner.klar", [1, 1, "1,5", ""])
        self.assertNotIn("Achtung", s)
        self.assertIn("Durchschnitt: 1,17", s)


class Palindrom(unittest.TestCase):
    def test_palindrome(self):
        s = spiele("09_palindrom.klar", [
            1, "Trug Tim eine so helle Hose nie mit Gurt",
            1, "Reliefpfeiler",
            1, "Klarsatz",
            1, "!!!",
            1, 12321,
            0])
        self.assertEqual(s.anzahl("Ja, das ist ein Palindrom!"), 3)
        self.assertIn("(trugtimeinesohellehoseniemitgurt)", s)
        self.assertIn("Nein. Rückwärts steht dort: ztasralk", s)
        self.assertIn("Da sind gar keine Buchstaben drin.", s)
        self.assertIn("(12321)", s)

    def test_zaehlen(self):
        s = spiele("09_palindrom.klar", [2, "Hallo  schöne Welt", 0])
        self.assertIn("Wörter: 3", s)
        self.assertIn("Buchstaben: 15", s)
        self.assertIn("Vokale: 5", s)
        self.assertIn("Konsonanten: 10", s)


VOKABELN = {"Hund": "dog", "Katze": "cat", "Haus": "house", "Buch": "book", "Wasser": "water",
            "Apfel": "apple", "Schule": "school", "Freund": "friend", "Fenster": "window",
            "Straße": "street", "Tisch": "table"}


def vokabel_antwort(frage):
    m = re.search(r"„(.+)“", frage)
    return VOKABELN[m.group(1)] if m else None


class Vokabeltrainer(unittest.TestCase):
    def spieler(self, fehlerfrei=True):
        schritte = []

        def antwort(frage, protokoll):
            if frage.startswith("Auswahl"):
                if not schritte:
                    schritte.append(1)
                    return 1
                return 0
            w = vokabel_antwort(frage)
            return w.upper() if fehlerfrei else "keine Ahnung"
        return antwort

    def test_alles_richtig_auch_gross_geschrieben(self):
        for seed in range(1, 6):
            with self.subTest(seed=seed):
                s = spiele("10_vokabeltrainer.klar", self.spieler(True), seed=seed)
                self.assertEqual(s.anzahl("Richtig!"), 5)
                self.assertIn("Ergebnis: 5 von 5 richtig.", s)

    def test_alles_falsch(self):
        s = spiele("10_vokabeltrainer.klar", self.spieler(False))
        self.assertEqual(s.anzahl("Leider falsch. Richtig ist: "), 5)
        self.assertIn("Ergebnis: 0 von 5 richtig.", s)

    def test_eigene_woerter_lernen_und_anzeigen(self):
        s = spiele("10_vokabeltrainer.klar", [2, "Tisch", "table", 2, "", "x", 3, 0])
        self.assertIn("Gespeichert: Tisch = table", s)
        self.assertIn("Bitte beides ausfüllen.", s)
        self.assertIn("Hund = dog", s)
        self.assertIn("Straße = street", s)
        self.assertIn("Tisch = table", s.text.split("Gespeichert")[1])
        self.assertEqual(s.uebrig, [])

    def test_gefragte_woerter_streuen(self):
        s = spiele("10_vokabeltrainer.klar", self.spieler(True), seed=3)
        gefragt = set(re.findall(r"„(.+?)“", s.text))
        self.assertGreaterEqual(len(gefragt), 2)


class Galgenmaennchen(unittest.TestCase):
    def test_zwei_spieler_gewinn(self):
        s = spiele("11_galgenmaennchen.klar", [2, "KlarSatz", *"klarstz"])
        self.assertIn("Gewonnen! Das Wort war: klarsatz", s)
        self.assertIn("Fehler: 0 von 6", s)
        self.assertGreaterEqual(s.zeilen.count(""), 40)             # Wort ist nicht mehr zu sehen
        zwischen = s.text.split("Spieler 2 ist dran!")[1].split("Gewonnen!")[0]
        self.assertNotIn("klarsatz", zwischen)                      # nach dem Eintippen ist das Wort nur als _ _ _ zu sehen

    def test_zwei_spieler_verloren(self):
        s = spiele("11_galgenmaennchen.klar", [2, "aa", *"zyxwvu"])
        self.assertIn("Verloren. Das Wort war: aa", s)
        self.assertIn("Fehler: 6 von 6", s)
        self.assertIn("/ \\  |", s)                                 # Bild mit beiden Beinen

    def test_fehleingaben(self):
        s = spiele("11_galgenmaennchen.klar", [2, "ab", 5, "", "a", "a", "b"])
        self.assertEqual(s.anzahl("Bitte einen Buchstaben eingeben."), 2)
        self.assertIn("Den hattest du schon.", s)
        self.assertIn("Gewonnen!", s)

    def test_wort_mit_leerzeichen_und_umlaut(self):
        s = spiele("11_galgenmaennchen.klar", [2, "Bär so", *"bärso"])
        self.assertIn("Wort: b ä r   s o", s)
        self.assertIn("Gewonnen! Das Wort war: bär so", s)

    def test_gegen_den_computer(self):
        woerter = {"programm", "computer", "tastatur", "bildschirm", "schleife",
                   "variable", "aufgabe", "klarsatz", "wolke", "gebirge"}
        gefundene = set()
        for seed in range(1, 21):
            buchstaben = iter("abcdefghijklmnopqrstuvwxyz")
            s = spiele("11_galgenmaennchen.klar",
                       lambda f, p: 1 if f.startswith("1 =") else next(buchstaben), seed=seed)
            m = re.search(r"Das Wort war: (\w+)", s.text)
            self.assertIn(m.group(1), woerter)
            gefundene.add(m.group(1))
        self.assertGreaterEqual(len(gefundene), 4)                  # es wird wirklich zufällig gewählt


def zahlen_spieler(stufe, aufgeben=False):
    """Rät mit Halbieren; liest 'Zu klein/Zu groß' aus der letzten Ausgabe."""
    zustand = {"lo": 1, "hi": {1: 10, 2: 100, 3: 1000}[stufe], "letzter": None, "phase": 0}

    def antwort(frage, protokoll):
        z = zustand
        if frage.startswith("Welche Stufe"):
            return stufe
        if frage.startswith("Noch eine Runde"):
            return "n"
        if aufgeben:
            return "ende"
        if z["letzter"] is not None:
            hinweis = protokoll[-1]
            if hinweis.startswith("Zu klein"):
                z["lo"] = z["letzter"] + 1
            elif hinweis.startswith("Zu groß"):
                z["hi"] = z["letzter"] - 1
        tipp = (z["lo"] + z["hi"]) // 2
        z["letzter"] = tipp
        return tipp
    return antwort


class ZahlenratenDuRaetst(unittest.TestCase):
    def test_halbieren_schafft_jede_stufe_in_der_bestzeit(self):
        for stufe, optimal in ((1, 4), (2, 7), (3, 10)):
            for seed in range(1, 16):
                with self.subTest(stufe=stufe, seed=seed):
                    s = spiele("01_zahlenraten_du_raetst.klar", zahlen_spieler(stufe), seed=seed)
                    m = re.search(r"du hast (\d+) Versuche gebraucht", s.text)
                    self.assertLessEqual(int(m.group(1)), optimal)
                    self.assertIn("Besser geht es mit Halbieren kaum", s)

    def test_zufallszahl_liegt_im_bereich_und_schwankt(self):
        zahlen = set()
        for seed in range(1, 40):
            s = spiele("01_zahlenraten_du_raetst.klar", zahlen_spieler(1), seed=seed)
            zahlen.add(int(re.search(r"Richtig! Die Zahl war (\d+)", s.text).group(1)))
        self.assertTrue(zahlen <= set(range(1, 11)))
        self.assertGreaterEqual(len(zahlen), 6)

    def test_ungueltige_eingaben_und_aufgeben(self):
        s = spiele("01_zahlenraten_du_raetst.klar",
                   ["7", "0", "abc", 2, "abc", 0, 101, "ENDE", "n"], seed=2)
        self.assertEqual(s.anzahl("Bitte 1, 2 oder 3 eingeben."), 3)      # "7", "0" und "abc"
        self.assertIn("Das ist keine Zahl.", s)
        self.assertIn("Bitte eine Zahl von 1 bis 100.", s)
        self.assertRegex(s.text, r"Schade! Die Zahl war \d+\.")

    def test_schlechtes_raten_bekommt_einen_tipp(self):
        gesehen = set()
        for seed in range(1, 11):
            antworten = iter([1] + list(range(1, 11)) + ["n"])          # Stufe 1, dann von unten durchprobieren
            s = spiele("01_zahlenraten_du_raetst.klar", lambda f, p: next(antworten), seed=seed)
            versuche = int(re.search(r"du hast (\d+) Versuche gebraucht", s.text).group(1))
            if versuche <= 4:
                self.assertIn("Besser geht es mit Halbieren kaum", s)
            else:
                self.assertIn("Rate immer die Mitte, dann schaffst du es in höchstens 4 Versuchen.", s)
            gesehen.add(versuche <= 4)
        self.assertEqual(gesehen, {True, False})                        # beide Rückmeldungen kommen vor


BEATS = {("Stein", "Schere"), ("Papier", "Stein"), ("Schere", "Papier")}


class SchereSteinPapier(unittest.TestCase):
    def test_regeln_und_punktestand(self):
        wahl = iter(["schere", "STEIN", "Papier"] * 10 + ["blub", "ende"])
        s = spiele("07_schere_stein_papier.klar", lambda f, p: next(wahl), seed=7)
        runden = re.findall(r"Du: (\w+)   Computer: (\w+)", s.text)
        self.assertEqual(len(runden), 30)
        ich = comp = 0
        zeilen = s.zeilen
        for nr, zeile in enumerate(zeilen):
            m = re.match(r"Du: (\w+)   Computer: (\w+)$", zeile)
            if m:
                du, pc = m.groups()
                naechste = zeilen[nr + 1]
                if du == pc:
                    self.assertEqual(naechste, "Unentschieden.")
                elif (du, pc) in BEATS:
                    self.assertEqual(naechste, "Du gewinnst diese Runde!")
                    ich += 1
                else:
                    self.assertEqual(naechste, "Der Computer gewinnt diese Runde.")
                    comp += 1
        self.assertIn(f"Endstand {ich}:{comp}", s)
        self.assertIn("Das kenne ich nicht", s)
        self.assertGreater(ich + comp, 5)

    def test_computer_waehlt_alle_drei(self):
        wahl = iter(["stein"] * 60 + ["ende"])
        s = spiele("07_schere_stein_papier.klar", lambda f, p: next(wahl), seed=3)
        self.assertEqual(set(re.findall(r"Du: \w+   Computer: (\w+)", s.text)), {"Schere", "Stein", "Papier"})

    def test_sofort_beenden(self):
        s = spiele("07_schere_stein_papier.klar", ["ende"])
        self.assertIn("Endstand 0:0 – unentschieden.", s)


class TodoListe(unittest.TestCase):
    def test_anlegen_abhaken_loeschen_und_speichern(self):
        with leeres_verzeichnis() as d:
            s = spiele("18_todo_liste.klar", [
                1, "Milch kaufen",
                1, "Brot",
                1, "a;b",              # Semikolon ist nicht erlaubt
                1, "",                 # leer geht nicht
                2, 1,                  # Milch abhaken
                2, 5,                  # Nummer gibt es nicht
                2, "x",
                3, 2,                  # Brot löschen
                7,
                0])
            self.assertIn("(Die Liste ist leer.)", s)
            self.assertIn("1. [ ] Milch kaufen", s)
            self.assertIn("2. [ ] Brot", s)
            self.assertIn("1. [x] Milch kaufen", s)
            self.assertIn("Bitte ohne Semikolon schreiben.", s)
            self.assertIn("Leer geht nicht.", s)
            self.assertEqual(s.anzahl("Diese Nummer gibt es nicht."), 2)
            self.assertIn("Das habe ich nicht verstanden.", s)
            self.assertEqual((d / "todo.txt").read_text(encoding="utf-8"), "1;Milch kaufen\n")

    def test_beim_naechsten_start_ist_alles_wieder_da(self):
        with leeres_verzeichnis() as d:
            (d / "todo.txt").write_text("1;Milch kaufen\n0;Zeitung\n", encoding="utf-8")
            s = spiele("18_todo_liste.klar", [1, "Post holen", 0])
            self.assertIn("1. [x] Milch kaufen", s)
            self.assertIn("2. [ ] Zeitung", s)
            self.assertIn("3. [ ] Post holen", s)
            self.assertEqual((d / "todo.txt").read_text(encoding="utf-8"),
                             "1;Milch kaufen\n0;Zeitung\n0;Post holen\n")

    def test_ohne_dateizugriff_laeuft_es_weiter(self):
        with leeres_verzeichnis() as d:
            s = spiele("18_todo_liste.klar", [1, "Test", 0], dateien=False)
            self.assertIn("Speichern hat nicht geklappt: Dateizugriff ist in diesem Lauf abgeschaltet.", s)
            self.assertIn("1. [ ] Test", s)
            self.assertFalse((d / "todo.txt").exists())


class Zahlenraten_Computer_raet(unittest.TestCase):
    """Programm 11 (Computer errät deine Zahl) – ausführlich getestet in test_klarsatz.py."""

    def test_alle_zahlen(self):
        for z in range(1, 11):
            with self.subTest(zahl=z):
                def antwort(frage, protokoll, z=z):
                    if frage.startswith("Noch eine Runde"):
                        return "n"
                    tipp = int(re.search(r"die (\d+)\?", frage).group(1))
                    return "r" if tipp == z else ("h" if tipp < z else "n")
                s = spiele("08_zahlenraten_computer_raet.klar", antwort)
                self.assertIn(f"Deine Zahl ist die {z} ", s)


class Kopfrechnen(unittest.TestCase):
    @staticmethod
    def loesung(frage):
        a, op, b = re.search(r"(\d+) ([+\-x]) (\d+) = ", frage).groups()
        a, b = int(a), int(b)
        return {"+": a + b, "-": a - b, "x": a * b}[op]

    def test_alles_richtig(self):
        for seed in range(1, 8):
            with self.subTest(seed=seed):
                s = spiele("02_kopfrechnen.klar", lambda f, p: self.loesung(f), seed=seed)
                self.assertIn("Du hast 10 von 10 Aufgaben richtig gelöst.", s)
                self.assertIn("Perfekt!", s)

    def test_aufgaben_sind_sinnvoll(self):
        s = spiele("02_kopfrechnen.klar", lambda f, p: self.loesung(f), seed=11)
        aufgaben = re.findall(r"(\d+) ([+\-x]) (\d+) = ", s.text)
        self.assertEqual(len(aufgaben), 10)
        for a, op, b in aufgaben:
            a, b = int(a), int(b)
            if op == "-":
                self.assertGreaterEqual(a - b, 0)
            if op == "x":
                self.assertTrue(2 <= a <= 12 and 2 <= b <= 12)

    def test_alles_falsch(self):
        s = spiele("02_kopfrechnen.klar", lambda f, p: "abc")
        self.assertIn("Du hast 0 von 10 Aufgaben richtig gelöst.", s)
        self.assertIn("Übung macht den Meister", s)
        self.assertEqual(s.anzahl("Leider falsch – richtig ist"), 10)

    def test_halb_richtig(self):
        zaehler = {"n": 0}

        def antwort(frage, protokoll):
            zaehler["n"] += 1
            return self.loesung(frage) if zaehler["n"] % 2 else -1
        s = spiele("02_kopfrechnen.klar", antwort)
        self.assertIn("Du hast 5 von 10 Aufgaben richtig gelöst.", s)
        self.assertIn("Gut gemacht", s)


class AlleProgramme(unittest.TestCase):
    def test_jedes_programm_endet_sauber_ohne_eingabe(self):
        """Ohne Eingabe darf kein Programm mit einem Syntaxfehler oder Absturz enden –
        nur mit der Meldung 'Es kam keine Eingabe.'"""
        from klarsatz import KlarsatzFehler
        for datei in sorted(PROGRAMME.glob("*.klar")):
            with self.subTest(programm=datei.name), leeres_verzeichnis():
                try:
                    # Dauerprogramme wie die Uhr laufen absichtlich endlos: knappe Schrittzahl,
                    # kein echtes Warten – hier zählt nur, dass sie sauber starten und enden.
                    from klarsatz.grenzen import Grenzen
                    spiele(datei.name, [], dateien=False, max_schritte=3000,
                           grenzen=Grenzen(warte=0))
                except KlarsatzFehler as e:
                    self.assertTrue("keine Eingabe" in e.meldung or "Schrittlimit" in e.meldung,
                                    f"{datei.name}: {e.meldung}")


if __name__ == "__main__":
    unittest.main()
