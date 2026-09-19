#!/usr/bin/env python3
"""Erzeugt die von der Spielwiese benötigten Dateien in playground/:
  klarsatz-py.zip     das Python-Paket (für Pyodide im Browser)
  beispiele.json      die Beispielprogramme aus beispiele/ und programme/
  hervorhebung.json   die Hervorhebungsregeln (aus editor/)

Aufruf:  python3 tools/baue_playground.py     (danach:  python3 -m http.server -d playground 8000)"""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

TITEL = {
    ("beispiele", "hallo"): ("Erste Schritte", "Hallo Welt"),
    ("beispiele", "schreibweise"): ("Erste Schritte", "So darf man schreiben"),
    ("beispiele", "rechnen"): ("Erste Schritte", "Rechnen und Bedingungen"),
    ("beispiele", "fizzbuzz"): ("Erste Schritte", "FizzBuzz"),
    ("beispiele", "listen"): ("Erste Schritte", "Listen und Schleifen"),
    ("beispiele", "aufgaben"): ("Erste Schritte", "Aufgaben (Funktionen)"),
    ("beispiele", "dinge"): ("Erste Schritte", "Dinge (Strukturen)"),
    ("beispiele", "fehler"): ("Erste Schritte", "Fehler und Prüfmodus (mit Absicht fehlerhaft)"),
    ("beispiele", "zeichnen"): ("Erste Schritte", "Zeichnen (Quadrat und Dreieck)"),
}
PROGRAMM_TITEL = {
    "01": "Zahlenraten – du rätst",
    "02": "Kopfrechnen",
    "03": "Taschenrechner",
    "04": "Umrechner",
    "05": "Primzahlen",
    "06": "Notenrechner",
    "07": "Schere, Stein, Papier",
    "08": "Zahlenraten – der Computer rät",
    "09": "Palindrome und Textanalyse",
    "10": "Vokabeltrainer",
    "11": "Galgenmännchen",
    "12": "Vielecke zeichnen",
    "13": "Bunte Spirale",
    "14": "Sinus und Kosinus",
    "15": "Rekursiver Baum",
    "16": "Analoguhr",
    "17": "Warenkorb",
    "18": "To-do-Liste",
    "19": "Textadventure",
    "20": "Grafikadventure",
}


def beschreibung(code):
    m = re.match(r"\s*Anmerkung:\s*(.+)", code)
    return m.group(1).strip() if m else ""


def main():
    ziel = WURZEL / "playground"
    ziel.mkdir(exist_ok=True)

    with zipfile.ZipFile(ziel / "klarsatz-py.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for datei in sorted((WURZEL / "klarsatz").glob("*.py")):
            z.write(datei, f"klarsatz/{datei.name}")

    beispiele = []
    for (ordner, name), (gruppe, titel) in TITEL.items():
        code = (WURZEL / ordner / f"{name}.klar").read_text(encoding="utf-8")
        beispiele.append({"id": name, "gruppe": gruppe, "titel": titel, "beschreibung": beschreibung(code), "code": code,
                          "fragt": "Frage " in code})
    for datei in sorted((WURZEL / "programme").glob("*.klar")):
        nr = datei.name[:2]
        code = datei.read_text(encoding="utf-8")
        beispiele.append({"id": datei.stem, "gruppe": "Programme zum Ausprobieren", "titel": f"{nr} {PROGRAMM_TITEL[nr]}",
                          "beschreibung": beschreibung(code), "code": code, "fragt": "Frage " in code})
    (ziel / "beispiele.json").write_text(json.dumps(beispiele, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    shutil.copy(WURZEL / "editor" / "hervorhebung.json", ziel / "hervorhebung.json")
    print(f"playground/: klarsatz-py.zip, beispiele.json ({len(beispiele)} Programme), hervorhebung.json")


if __name__ == "__main__":
    main()
