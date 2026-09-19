#!/usr/bin/env python3
"""Erzeugt die Editor-Unterstützung aus den Sprachdaten des Parsers:
  editor/vscode-klarsatz/…      VS-Code-Erweiterung (auch für Shiki/GitHub nutzbar: syntaxes/klarsatz.tmLanguage.json)
  editor/hervorhebung.json      Regeln für die Hervorhebung in JavaScript (Webseite, Playground)

Aufruf:  python3 tools/baue_editor.py"""
import json
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from klarsatz import __version__                                    # noqa: E402
from klarsatz.hervorhebung import TEXTMATE, js_regeln, textmate_grammatik   # noqa: E402

EXT = WURZEL / "editor" / "vscode-klarsatz"


def schreibe(pfad, daten):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("geschrieben:", pfad.relative_to(WURZEL))


PAKET = {
    "name": "klarsatz", "displayName": "Klarsatz", "version": __version__, "publisher": "klarsatz",
    "description": "Syntax-Hervorhebung, Einrückung und Snippets für Klarsatz – die Programmiersprache, die wie Deutsch klingt.",
    "engines": {"vscode": "^1.75.0"}, "categories": ["Programming Languages", "Snippets"],
    "keywords": ["klarsatz", "deutsch", "programmiersprache"],
    "contributes": {
        "languages": [{"id": "klarsatz", "aliases": ["Klarsatz", "klarsatz"], "extensions": [".klar"],
                       "configuration": "./language-configuration.json"}],
        "grammars": [{"language": "klarsatz", "scopeName": "source.klarsatz", "path": "./syntaxes/klarsatz.tmLanguage.json"}],
        "snippets": [{"language": "klarsatz", "path": "./snippets/klarsatz.json"}],
    },
}

SPRACHKONFIGURATION = {
    "comments": {"lineComment": "Anmerkung:"},
    "brackets": [["(", ")"]],
    "autoClosingPairs": [{"open": "(", "close": ")"}, {"open": "\"", "close": "\"", "notIn": ["string", "comment"]},
                         {"open": "„", "close": "“", "notIn": ["string", "comment"]}],
    "surroundingPairs": [["(", ")"], ["\"", "\""], ["„", "“"]],
    "wordPattern": "[A-Za-zÄÖÜäöüß_][A-Za-zÄÖÜäöüß0-9_]*",
    "indentationRules": {
        "increaseIndentPattern": "^.*:\\s*$",
        "decreaseIndentPattern": "^\\s*(?i:ende|sonst|bei)\\b",
    },
    "onEnterRules": [
        {"beforeText": "^\\s*(?i:sonst|bei)\\b.*:\\s*$", "action": {"indent": "indent"}},
    ],
}


def snippet(prefix, beschreibung, *zeilen):
    return {"prefix": prefix, "description": beschreibung, "body": list(zeilen)}


SNIPPETS = {
    "Ausgabe": snippet("zeige", "Text oder Wert ausgeben", "Zeige ${1:\"Hallo\"}."),
    "Eingabe": snippet("frage", "Eine Eingabe abfragen", "Frage \"${1:Wie heißt du?} \" und merke die Antwort als ${2:Name}."),
    "Wenn": snippet("wenn", "Bedingung mit Block", "Wenn ${1:Zahl größer als 10} ist:", "    ${0:Zeige \"groß\".}", "Ende."),
    "Wenn … Sonst": snippet("wennsonst", "Bedingung mit Sonst-Zweig", "Wenn ${1:Zahl größer als 10} ist:",
                            "    ${2:Zeige \"groß\".}", "Sonst:", "    ${0:Zeige \"klein\".}", "Ende."),
    "Wenn … Sonst wenn": snippet("wennsonstwenn", "Mehrere Fälle", "Wenn ${1:a gleich 1} ist:", "    ${2:Zeige \"eins\".}",
                                 "Sonst wenn ${3:a gleich 2} ist:", "    ${4:Zeige \"zwei\".}", "Sonst:", "    ${0:Zeige \"anders\".}", "Ende."),
    "Wiederhole": snippet("wiederhole", "Schleife mit fester Anzahl", "Wiederhole ${1:5} Mal:", "    ${0:Zeige \"Hallo\".}", "Ende."),
    "Solange": snippet("solange", "Schleife mit Bedingung", "Wiederhole solange ${1:Zahl kleiner als 10} ist:",
                       "    ${0:Erhöhe Zahl um 1.}", "Ende."),
    "Zähle": snippet("zaehle", "Zählschleife", "Zähle von ${1:1} bis ${2:10} mit ${3:i}:", "    ${0:Zeige ${3:i}.}", "Ende."),
    "Für jedes": snippet("fuer", "Durch eine Liste gehen", "Für jedes ${1:Element} in ${2:Liste}:", "    ${0:Zeige ${1:Element}.}", "Ende."),
    "Aufgabe": snippet("aufgabe", "Aufgabe (Funktion) mit Rückgabewert", "Definiere Aufgabe ${1:Quadrat} von ${2:x}:",
                       "    Gib ${0:x mal x} zurück.", "Ende."),
    "Aufgabe ohne Wert": snippet("aufgabeohne", "Aufgabe ohne Rückgabewert", "Definiere Aufgabe ${1:Begrüße} mit ${2:Name}:",
                                 "    ${0:Zeige \"Hallo, \" und ${2:Name}.}", "Ende."),
    "Versuche": snippet("versuche", "Fehler abfangen", "Versuche:", "    ${1:Zeige 1 geteilt durch 0.}", "Bei Fehler:",
                        "    ${0:Zeige \"Problem: \" und Fehlermeldung.}", "Ende."),
    "Ding": snippet("ding", "Ein Ding (Struktur) beschreiben", "${1:Hund} hat ${2:einen Namen} und ${3:ein Alter}."),
    "Erschaffe": snippet("erschaffe", "Ein Ding erschaffen", "Erschaffe ${1:Hund} mit ${2:Name} ${3:\"Rocco\"} und ${4:Alter} ${5:5} als ${0:Waldi}."),
    "Liste": snippet("liste", "Eine Liste anlegen", "Erstelle eine Liste namens ${1:Einkauf} mit ${0:\"Milch\" und \"Brot\"}."),
    "Tabelle": snippet("tabelle", "Eine Tabelle anlegen", "Erstelle eine Tabelle namens ${1:Preise} mit ${0:\"Apfel\" als 3}."),
    "Programmgerüst": snippet("programm", "Kleines Programm mit Frage und Ausgabe", "Anmerkung: ${1:Was macht das Programm?}",
                              "Frage \"${2:Wie heißt du?} \" und merke die Antwort als ${3:Name}.", "Zeige \"Hallo, \" und ${3:Name} und \"!\".$0"),
}


def main():
    schreibe(EXT / "package.json", PAKET)
    schreibe(EXT / "language-configuration.json", SPRACHKONFIGURATION)
    schreibe(EXT / "syntaxes" / "klarsatz.tmLanguage.json", textmate_grammatik())
    schreibe(EXT / "snippets" / "klarsatz.json", SNIPPETS)
    schreibe(WURZEL / "editor" / "hervorhebung.json",
             {"hinweis": "Regeln für die Hervorhebung in JavaScript: new RegExp(regex, 'imuy'). 'bereiche' ist ein Name "
                         "für den ganzen Treffer oder eine Liste (ein Name pro Klammergruppe, null = ohne Farbe).",
              "namen": TEXTMATE, "regeln": js_regeln()})


if __name__ == "__main__":
    main()
