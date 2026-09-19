#!/usr/bin/env python3
"""Baut die Spielwiese und kopiert sie in den Webordner der Klarsatz-Seite.

    python3 tools/veroeffentliche_spielwiese.py [ZIELORDNER]

Voreinstellung: /var/www/html/klarsatz/spielwiese
Die Datei playground/index.html wird bewusst nicht mitkopiert — die Webseite
bringt ihre eigene Seite (spielplatz.html) mit.
"""
import shutil
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
VORGABE = Path("/var/www/html/klarsatz/spielwiese")

# Alles aus playground/ außer der eigenständigen Vorführseite und Node-Beiwerk.
NICHT = {"index.html", "package.json"}


def main() -> int:
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE

    print("Spielwiese bauen …")
    ergebnis = subprocess.run(
        [sys.executable, str(WURZEL / "tools" / "baue_playground.py")],
        cwd=WURZEL, capture_output=True, text=True,
    )
    if ergebnis.returncode != 0:
        print(ergebnis.stdout + ergebnis.stderr, file=sys.stderr)
        return ergebnis.returncode
    print(ergebnis.stdout.strip())

    ziel.mkdir(parents=True, exist_ok=True)
    kopiert = 0
    for datei in sorted((WURZEL / "playground").iterdir()):
        if not datei.is_file() or datei.name in NICHT:
            continue
        shutil.copy2(datei, ziel / datei.name)
        groesse = (ziel / datei.name).stat().st_size
        print(f"  {datei.name:28} {groesse / 1024:8.1f} kB")
        kopiert += 1

    # Was im Ziel liegt, aber nicht mehr zur Spielwiese gehört, kommt weg —
    # sonst bleiben nach einer Umbenennung alte Dateien zurück.
    gehoert_dazu = {d.name for d in (WURZEL / "playground").iterdir() if d.is_file() and d.name not in NICHT}
    for datei in sorted(ziel.iterdir()):
        if datei.is_file() and datei.name not in gehoert_dazu:
            datei.unlink()
            print(f"  entfernt: {datei.name}")

    print(f"\n{kopiert} Dateien nach {ziel} kopiert.")
    print("Die Seite lädt Pyodide aus ../pyodide/ — siehe spielplatz.html.")

    # Versionsstempel der Seite auffrischen, damit Browser die neuen Dateien holen.
    subprocess.run([sys.executable, str(WURZEL / "tools" / "stempel_webseite.py"), str(ziel.parent)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
