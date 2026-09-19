"""Hervorhebung: Pygments, TextMate (VS Code) und JavaScript-Regeln stammen aus derselben Regelliste."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from klarsatz.hervorhebung import TEXTMATE, js_regeln, pygments_lexer, regeln, textmate_grammatik
from klarsatz.parser import RESERVIERT, STARTER
from klarsatz.sprachdaten import (ANWEISUNGEN, BINDEWOERTER, KONSTANTEN, KONTROLLE, alternative, wort_regex)

WURZEL = Path(__file__).resolve().parent.parent
PROGRAMME = sorted(list((WURZEL / "programme").glob("*.klar")) + list((WURZEL / "beispiele").glob("*.klar")))


def pygments_kategorien(text):
    from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String
    tabelle = [(Comment.Single, "kommentar"), (String.Double, "text"), (Number, "zahl"), (Keyword.Reserved, "anweisung"),
               (Keyword.Constant, "konstante"), (Keyword, "steuerung"), (Name.Builtin, "funktion"),
               (Operator.Word, "operator"), (Name.Function, "funktionsname"), (Name.Class, "typname"),
               (Punctuation, "zeichen")]
    aus = []
    for typ, wert in pygments_lexer()().get_tokens(text):
        for kandidat, name in tabelle:
            if typ in kandidat:
                aus.append((wert, name))
                break
    return aus


class Sprachdaten(unittest.TestCase):
    def test_jedes_reservierte_wort_ist_einer_gruppe_zugeordnet(self):
        offen = set(RESERVIERT) - (KONTROLLE | BINDEWOERTER | KONSTANTEN)
        self.assertEqual(offen, set())

    def test_jeder_satzanfang_ist_eingeordnet(self):
        self.assertEqual(set(STARTER) - (ANWEISUNGEN | KONTROLLE), set())

    def test_gruppen_ueberschneiden_sich_nicht(self):
        gruppen = [KONTROLLE, ANWEISUNGEN, BINDEWOERTER, KONSTANTEN]
        for i, a in enumerate(gruppen):
            for b in gruppen[i + 1:]:
                self.assertEqual(a & b, set())

    def test_wortmuster_kennen_umlaute_und_ersatzschreibung(self):
        r = re.compile(wort_regex("groesser"), re.I)
        for w in ("größer", "groesser", "GRÖSSER", "grösser"):
            self.assertTrue(r.fullmatch(w), w)
        self.assertFalse(r.fullmatch("groesse"))
        r = re.compile(alternative({"zaehle", "fuer"}), re.I)
        for w in ("Zähle", "zaehle", "für", "FUER"):
            self.assertTrue(r.fullmatch(w), w)


class PygmentsLexer(unittest.TestCase):
    def test_verlustfrei_fuer_alle_programme(self):
        for datei in PROGRAMME:
            with self.subTest(programm=datei.name):
                text = datei.read_text(encoding="utf-8")
                self.assertEqual("".join(v for _, v in pygments_lexer()().get_tokens(text)), text)

    def test_keine_fehlertokens(self):
        from pygments.token import Error
        for datei in PROGRAMME:
            with self.subTest(programm=datei.name):
                tokens = pygments_lexer()().get_tokens(datei.read_text(encoding="utf-8"))
                self.assertFalse([v for t, v in tokens if t is Error])

    def test_kategorien(self):
        text = ('Anmerkung: Kommentar mit Zeige\nHund hat Namen.\nDefiniere Aufgabe Quadrat von x:\n'
                '    Gib x mal x zurück.\nEnde.\nMerke für immer -3.5 als Pi.\nZeige Länge von "abc" und „hallo“.\n'
                'Wenn Antwort eine Zahl ist:\nEnde.')
        k = dict((w, c) for w, c in pygments_kategorien(text) if c != "zeichen")
        self.assertEqual(k["Anmerkung: Kommentar mit Zeige"], "kommentar")
        self.assertEqual((k["Hund"], k["hat"]), ("typname", "operator"))
        self.assertEqual((k["Definiere"], k["Aufgabe"], k["Quadrat"]), ("steuerung", "steuerung", "funktionsname"))
        self.assertEqual((k["Gib"], k["mal"], k["zurück"], k["Ende"]), ("steuerung", "operator", "steuerung", "steuerung"))
        self.assertEqual((k["Merke"], k["für"], k["immer"], k["-3.5"]), ("anweisung", "steuerung", "operator", "zahl"))
        self.assertEqual((k["Länge"], k['"abc"'], k["„hallo“"]), ("funktion", "text", "text"))
        self.assertEqual((k["eine"], k["Zahl"]), ("operator", "typname"))

    def test_alltagswoerter_sind_nur_im_zusammenhang_hervorgehoben(self):
        text = ('Für jedes Zeichen in Wort:\n    Zeige Zeichen und Element und Rest und Wert und Zahl und Text.\nEnde.\n'
                'Merke 5 als Zahl.\nMerke "x" als Text.\nZeige Element 2 von L und Rest von 7 geteilt durch 2.')
        k = pygments_kategorien(text)
        self.assertNotIn(("Zeichen", "funktion"), k)              # Schleifenvariable, keine Funktion
        self.assertEqual([c for w, c in k if w in ("Zahl", "Text")], [])
        self.assertIn(("Element", "funktion"), k)                 # 'Element 2 von L'
        self.assertIn(("Rest", "funktion"), k)                    # 'Rest von 7 …'
        self.assertNotIn(("Wert", "funktion"), k)


class GeneriertesIstAktuell(unittest.TestCase):
    def test_dateien_entsprechen_der_regelliste(self):
        gramm = json.loads((WURZEL / "editor/vscode-klarsatz/syntaxes/klarsatz.tmLanguage.json").read_text(encoding="utf-8"))
        self.assertEqual(gramm, textmate_grammatik(), "Bitte 'python3 tools/baue_editor.py' ausführen.")
        js = json.loads((WURZEL / "editor/hervorhebung.json").read_text(encoding="utf-8"))
        self.assertEqual(js["regeln"], js_regeln())
        self.assertEqual(js["namen"], TEXTMATE)

    def test_erweiterungsdateien_sind_gueltig(self):
        ordner = WURZEL / "editor/vscode-klarsatz"
        paket = json.loads((ordner / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(paket["contributes"]["languages"][0]["extensions"], [".klar"])
        for pfad in (ordner / "language-configuration.json", ordner / "snippets/klarsatz.json"):
            json.loads(pfad.read_text(encoding="utf-8"))
        from klarsatz import __version__
        self.assertEqual(paket["version"], __version__)

    def test_snippets_erzeugen_gueltige_programme(self):
        from klarsatz.pruefer import pruefe
        snippets = json.loads((WURZEL / "editor/vscode-klarsatz/snippets/klarsatz.json").read_text(encoding="utf-8"))
        for name, s in snippets.items():
            with self.subTest(snippet=name):
                text = "\n".join(s["body"])
                # Platzhalter ${1:Vorgabe} durch die Vorgabe ersetzen, dann muss es lesbar sein
                text = re.sub(r"\$\{\d+:((?:[^{}]|\{[^{}]*\})*)\}", lambda m: re.sub(r"\$\{\d+:([^{}]*)\}", r"\1", m.group(1)), text)
                text = re.sub(r"\$\{\d+:([^{}]*)\}", r"\1", text).replace("$0", "")
                syntax = [b for b in pruefe(text) if b.code == "syntax"]
                self.assertEqual(syntax, [], text)

    def test_regeln_sind_in_javascript_und_python_schreibweise_gleich_lang(self):
        self.assertEqual(len(regeln(r"\p{L}")), len(regeln(r"[^\W\d_]")))


@unittest.skipUnless(shutil.which("node") and (WURZEL / "tools/node_modules/vscode-textmate").exists(),
                     "node oder tools/node_modules fehlt (cd tools && npm install)")
class MitEchtemVSCodeTokenizer(unittest.TestCase):
    def test_pygments_und_textmate_faerben_gleich(self):
        umgekehrt = {v: k for k, v in TEXTMATE.items()}
        dateien = [str(p) for p in PROGRAMME]
        roh = subprocess.run(["node", str(WURZEL / "tools/tokenisiere_textmate.js"), *dateien],
                             capture_output=True, text=True, check=True, cwd=WURZEL).stdout
        tm = json.loads(roh)
        for datei in PROGRAMME:
            with self.subTest(programm=datei.name):
                text = datei.read_text(encoding="utf-8")
                a = [(w, umgekehrt[s]) for w, s in tm[str(datei)] if s in umgekehrt and w.strip()]
                b = [(w, c) for w, c in pygments_kategorien(text) if w.strip()]
                self.assertEqual(a, b)


@unittest.skipUnless(shutil.which("node"), "node fehlt")
class MitJavaScript(unittest.TestCase):
    def test_javascript_und_pygments_faerben_gleich(self):
        roh = subprocess.run(["node", str(WURZEL / "tools/tokenisiere_js.mjs"), *[str(p) for p in PROGRAMME]],
                             capture_output=True, text=True, check=True, cwd=WURZEL).stdout
        js = json.loads(roh)
        for datei in PROGRAMME:
            with self.subTest(programm=datei.name):
                text = datei.read_text(encoding="utf-8")
                tokens = js[str(datei)]
                self.assertEqual("".join(t for t, _ in tokens), text)              # verlustfrei
                a = [(w, c) for w, c in tokens if c and w.strip()]
                b = [(w, c) for w, c in pygments_kategorien(text) if w.strip()]
                self.assertEqual(a, b)

    def test_umlaut_am_wortrand_wird_nicht_zerhackt(self):
        eintrag = "Endeä Größe Zähler Über\nEnde."
        (WURZEL / "tools").exists()
        roh = subprocess.run(["node", "--input-type=module", "-e", (
            "import fs from 'node:fs';"
            "import {kompiliere,tokenisiere} from './playground/klarsatz-hervorhebung.js';"
            "const r=kompiliere(JSON.parse(fs.readFileSync('./editor/hervorhebung.json','utf8')));"
            f"process.stdout.write(JSON.stringify(tokenisiere({json.dumps(eintrag)},r)));")],
            capture_output=True, text=True, check=True, cwd=WURZEL).stdout
        tokens = [t for t in json.loads(roh) if t[1]]
        self.assertEqual(tokens, [["Ende", "steuerung"], [".", "zeichen"]])          # nur das echte Ende


if __name__ == "__main__":
    unittest.main()
