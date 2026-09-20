#!/usr/bin/env python3
"""Hebt die Versionsnummer an allen Stellen zugleich.

    python3 tools/hebe_version.py 0.9.0

Die Nummer steht in sieben Dateien. Von Hand ist das einmal schiefgegangen: Der Sprung
auf 0.8.1 erreichte die Übergabe nicht, weil eine feste Dateiliste im Kopf des Autors
kürzer war als die Wirklichkeit. `tests/test_doku_konsistenz.py` merkt so etwas — dieses
Werkzeug verhindert es. Die Überschrift im Changelog wird nicht angefasst; die schreibt
man von Hand, denn dort steht, *was* sich geändert hat.
"""
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent


def stellen():
    """Alle Dateien, in denen die Nummer wörtlich vorkommt."""
    return ([WURZEL / "pyproject.toml", WURZEL / "klarsatz" / "__init__.py",
             WURZEL / "ÜBERGABE.md", WURZEL / "docs" / "SPRACHE.md",
             WURZEL / "tools" / "baue_tutorial.py", WURZEL / "webseite" / "baue_doku.sh"]
            + sorted((WURZEL / "webseite" / "seiten").glob("*.html"))
            + sorted((WURZEL / "webseite" / "kapitel").glob("*.html")))


def alte_version():
    text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)


def main(argv):
    if len(argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", argv[1]):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    alt, neu = alte_version(), argv[1]
    if alt == neu:
        print(f"Steht schon auf {neu}.")
        return 0

    geaendert = 0
    for datei in stellen():
        text = datei.read_text(encoding="utf-8")
        if alt in text:
            datei.write_text(text.replace(alt, neu), encoding="utf-8")
            print(f"  {datei.relative_to(WURZEL)}: {text.count(alt)}×")
            geaendert += 1

    print(f"{alt} → {neu} in {geaendert} Dateien.")
    print("Jetzt fehlen noch: Überschrift in CHANGELOG.md, tools/baue_editor.py,")
    print("die drei Veröffentlichungsbefehle und git tag -a v" + neu)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
