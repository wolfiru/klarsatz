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
# Auch alles, was die eigenen Skripte selbst nachladen. Nicht nur statische Einbindungen
# (import … from '../spielwiese/datei.js'), sondern ebenso nachgeladene Module
# (await import('./../spielwiese/datei.js')) und schlichte Pfade in Zeichenketten
# ('spielwiese/beispiele.json'). Genau daran hat es gefehlt: Die Startseite lud die
# Spielwiese ohne Stempel nach und bekam so einen alten Interpreter aus dem
# Zwischenspeicher, der die neuen Sätze der Sprache noch nicht kannte.
IN_JS = re.compile(r"""(['"])((?:\.{1,2}/)*(?:spielwiese|assets)/[^'"?]+\.(?:js|css|json))(?:\?v=[^'"]*)?\1""")


def stempel(datei: Path) -> str:
    """Stempel einer Datei, gebildet aus ihrem Inhalt. Für die Spielwiese zählt der ganze
    Ordner: Ändert sich dort irgendetwas — auch beispiele.json oder klarsatz-py.zip —,
    ändert sich der Stempel, mit dem die Spielwiese geladen wird. Ihre Dateien erben ihn
    (siehe klarsatz-playground.js), sodass kein Browser eine alte Fassung behält.

    Bewusst der Inhalt und nicht Änderungszeit und Größe: Beim Veröffentlichen wird
    kopiert, und Kopieren setzt neue Änderungszeiten. Sonst bekäme jede Veröffentlichung
    neue Stempel, und jeder Besucher lüde CSS und JavaScript erneut, obwohl sich nichts
    geändert hat."""
    if datei.parent.name == "spielwiese":
        teile = [f"{d.name}-{hashlib.sha1(d.read_bytes()).hexdigest()}"
                 for d in sorted(datei.parent.iterdir()) if d.is_file()]
        return hashlib.sha1("|".join(teile).encode()).hexdigest()[:8]
    return hashlib.sha1(datei.read_bytes()).hexdigest()[:8]


def main() -> int:
    ordner = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    seiten = sorted(ordner.glob("*.html"))
    if not seiten:
        print(f"Keine HTML-Seiten in {ordner}", file=sys.stderr)
        return 2

    fehlend, geaendert = set(), 0

    # Was die eigenen Skripte nachladen
    for skript in sorted((ordner / "assets").glob("*.js")):
        text = skript.read_text(encoding="utf-8")

        def ersetze_import(treffer: re.Match) -> str:
            # Ein Skript löst seine Pfade entweder gegen den eigenen Ordner auf
            # (import '../spielwiese/…') oder gegen die Seite (new URL('spielwiese/…',
            # document.baseURI)). Beides kommt vor, also werden beide Wege probiert.
            pfad = treffer.group(2)
            for ziel in ((ordner / "assets" / pfad).resolve(), (ordner / pfad).resolve()):
                if ziel.exists():
                    return f"{treffer.group(1)}{pfad}?v={stempel(ziel)}{treffer.group(1)}"
            fehlend.add(pfad)
            return treffer.group(0)

        neu = IN_JS.sub(ersetze_import, text)
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
