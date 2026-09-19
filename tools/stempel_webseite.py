#!/usr/bin/env python3
"""Frischt die Versionsstempel (?v=…) der Webseite auf.

Jede eigene CSS- und JS-Datei bekommt in allen HTML-Seiten einen Stempel, der sich
aus Änderungszeit und Größe der Datei ergibt. Dadurch holt jeder Browser eine
geänderte Datei sofort neu, statt die alte aus dem Zwischenspeicher zu nehmen —
und eine unveränderte Datei bleibt zwischengespeichert.

    python3 tools/stempel_webseite.py [ORDNER]      Voreinstellung: /var/www/html/klarsatz
"""
import hashlib
import re
import sys
from pathlib import Path

VORGABE = Path("/var/www/html/klarsatz")
# Nur eigene Dateien stempeln — nicht Pyodide (unveränderlich, groß, gut cachebar).
VERWEIS = re.compile(r'((?:href|src)=")((?:assets|spielwiese)/[^"?]+\.(?:css|js))(?:\?v=[^"]*)?(")')
# Auch Modul-Einbindungen in eigenen Skripten: import … from '../spielwiese/datei.js'
IMPORT = re.compile(r"""(from\s+['"])(\.\./spielwiese/[^'"?]+\.js)(?:\?v=[^'"]*)?(['"])""")


def stempel(datei: Path) -> str:
    """Stempel einer Datei. Für die Spielwiese zählt der ganze Ordner: Ändert sich dort
    irgendetwas — auch beispiele.json oder klarsatz-py.zip —, ändert sich der Stempel, mit
    dem die Spielwiese geladen wird. Ihre Dateien erben ihn (siehe klarsatz-playground.js),
    sodass kein Browser eine alte Fassung behält."""
    if datei.parent.name == "spielwiese":
        teile = [f"{d.name}-{d.stat().st_mtime_ns}-{d.stat().st_size}"
                 for d in sorted(datei.parent.iterdir()) if d.is_file()]
        return hashlib.sha1("|".join(teile).encode()).hexdigest()[:8]
    zustand = datei.stat()
    roh = f"{zustand.st_mtime_ns}-{zustand.st_size}".encode()
    return hashlib.sha1(roh).hexdigest()[:8]


def main() -> int:
    ordner = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    seiten = sorted(ordner.glob("*.html"))
    if not seiten:
        print(f"Keine HTML-Seiten in {ordner}", file=sys.stderr)
        return 2

    fehlend, geaendert = set(), 0

    # Modul-Einbindungen in den eigenen Skripten
    for skript in sorted((ordner / "assets").glob("*.js")):
        text = skript.read_text(encoding="utf-8")

        def ersetze_import(treffer: re.Match) -> str:
            ziel = (ordner / "assets" / treffer.group(2)).resolve()
            if not ziel.exists():
                fehlend.add(treffer.group(2))
                return treffer.group(0)
            return f"{treffer.group(1)}{treffer.group(2)}?v={stempel(ziel)}{treffer.group(3)}"

        neu = IMPORT.sub(ersetze_import, text)
        if neu != text:
            skript.write_text(neu, encoding="utf-8")
            geaendert += 1


    for seite in seiten:
        text = seite.read_text(encoding="utf-8")

        def ersetze(treffer: re.Match) -> str:
            ziel = ordner / treffer.group(2)
            if not ziel.exists():
                fehlend.add(treffer.group(2))
                return treffer.group(0)
            return f"{treffer.group(1)}{treffer.group(2)}?v={stempel(ziel)}{treffer.group(3)}"

        neu = VERWEIS.sub(ersetze, text)
        if neu != text:
            seite.write_text(neu, encoding="utf-8")
            geaendert += 1

    print(f"{geaendert} von {len(seiten)} Seiten neu gestempelt.")
    for f in sorted(fehlend):
        print(f"  ! verwiesen, aber nicht vorhanden: {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
