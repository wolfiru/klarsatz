#!/usr/bin/env python3
"""Kopiert die handgepflegten Seiten und Bausteine in den Webordner.

    python3 tools/veroeffentliche_webseite.py [ZIELORDNER]

Voreinstellung: /var/www/html/klarsatz

Im Repository liegt die Webseite in webseite/ — dort wird sie bearbeitet, nicht
im Webordner. Kopiert werden nur die von Hand gepflegten Teile:

    webseite/seiten/*.html   -> ZIELORDNER/
    webseite/assets/*        -> ZIELORDNER/assets/

Nicht kopiert, weil anderswo erzeugt:
    doku-*.html   aus webseite/kapitel/ über webseite/baue_doku.sh
    spielwiese/   aus playground/ über tools/veroeffentliche_spielwiese.py
    downloads/    über tools/baue_archiv.py
    pyodide/      Fremdcode, liegt nur im Webordner

Zum Schluss laufen die Cache-Stempel (?v=…) frisch über alle Seiten. Deshalb
stehen sie in webseite/ gar nicht erst drin.
"""
import shutil
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "webseite"
VORGABE = Path("/var/www/html/klarsatz")


def main() -> int:
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    if not ziel.is_dir():
        print(f"Zielordner {ziel} gibt es nicht.", file=sys.stderr)
        return 2

    kopiert = 0
    for datei in sorted((QUELLE / "seiten").glob("*.html")):
        shutil.copy2(datei, ziel / datei.name)
        kopiert += 1

    (ziel / "assets").mkdir(exist_ok=True)
    for datei in sorted((QUELLE / "assets").rglob("*")):
        if datei.is_file():
            # Auch Unterordner (assets/fonts/) — die Schriften liegen seit 0.10.1
            # im Projekt, statt bei jedem Seitenaufruf von Google geholt zu werden.
            unterhalb = datei.relative_to(QUELLE / "assets")
            (ziel / "assets" / unterhalb).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(datei, ziel / "assets" / unterhalb)
            kopiert += 1

    print(f"{kopiert} Dateien nach {ziel} kopiert")

    # Einzelne Dateien, die direkt im Seitenordner liegen (llms.txt für Antwortmaschinen).
    for name in ("llms.txt",):
        quelle_datei = QUELLE / name
        if quelle_datei.exists():
            shutil.copy2(quelle_datei, ziel / name)
            kopiert += 1

    # Die Kapitel der Dokumentation entstehen aus webseite/kapitel/ und werden
    # dabei ebenfalls neu geschrieben — sonst passten Seiten und Kapitel nach
    # einer Änderung am gemeinsamen Kopf oder Fuß nicht mehr zusammen.
    bauskript = QUELLE / "baue_doku.sh"
    if bauskript.exists():
        ergebnis = subprocess.run(["bash", str(bauskript), str(ziel)], cwd=QUELLE,
                                  capture_output=True, text=True)
        if ergebnis.returncode != 0:
            print(ergebnis.stdout + ergebnis.stderr, file=sys.stderr)
            return ergebnis.returncode
        print("  " + ergebnis.stdout.strip().splitlines()[-1])

    # Das Tutorial entsteht aus docs/TUTORIAL.md — dort wird es auch geprüft.
    tutorial = WURZEL / "tools" / "baue_tutorial.py"
    if tutorial.exists():
        ergebnis = subprocess.run([sys.executable, str(tutorial), str(ziel)],
                                  capture_output=True, text=True)
        if ergebnis.returncode != 0:
            print(ergebnis.stdout + ergebnis.stderr, file=sys.stderr)
            return ergebnis.returncode
        print("  " + ergebnis.stdout.strip().splitlines()[0])

    subprocess.run([sys.executable, str(WURZEL / "tools" / "stempel_webseite.py"), str(ziel)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
