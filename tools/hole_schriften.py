#!/usr/bin/env python3
"""Lädt die Schriften herunter und stellt sie selbst bereit.

    python3 tools/hole_schriften.py

Bisher holte `assets/style.css` die Schriften per @import von Google. Damit ging bei
jedem Seitenaufruf die IP-Adresse des Besuchers an einen fremden Server — für eine
Seite, die stolz darauf ist, dass nichts das Fenster verlässt, der falsche Zustand.
Jetzt liegen die Dateien unter `assets/fonts/`, und in `style.css` stehen zwischen
zwei Markierungen die passenden @font-face-Regeln.

Alle drei Schriften stehen unter der SIL Open Font License 1.1 und dürfen mitgeliefert
werden; die Lizenz landet als `assets/fonts/LIZENZ.txt` daneben.
"""
import re
import sys
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "webseite" / "assets" / "fonts"
CSS_DATEI = WURZEL / "webseite" / "assets" / "style.css"

ANFANG = "/* ── Schriften (selbst bereitgestellt, siehe tools/hole_schriften.py) ── */"
ENDE = "/* ── Ende der Schriften ── */"

# Alle drei sind variable Schriften. Fragt man einzelne Gewichte ab, liefert Google
# für jedes davon die *ganze* variable Datei — vier Dateien Fraunces waren 260 kB, und
# jede enthielt dasselbe. Als Bereich (400..600) ist es eine Datei je Stil.
FAMILIEN = [
    "Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..600",
    "Manrope:wght@400..700",
    "JetBrains+Mono:wght@400..700",
]

# Moderne Kennung: dann liefert Google woff2 mit unicode-range.
KOPF = {"User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36")}

LIZENZ = """Die Schriften in diesem Ordner stammen von Google Fonts und stehen unter der
SIL Open Font License 1.1:

  Fraunces        © Undercase Type          https://github.com/undercasetype/Fraunces
  Manrope         © Mikhail Sharanda        https://github.com/sharanda/manrope
  JetBrains Mono  © JetBrains               https://github.com/JetBrains/JetBrainsMono

Der vollständige Lizenztext steht in den jeweiligen Projekten. Die OFL erlaubt das
Mitliefern und Bereitstellen der Dateien; die Schriften selbst wurden nicht verändert.
"""


def hole(adresse):
    return urllib.request.urlopen(urllib.request.Request(adresse, headers=KOPF)).read()


def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    for alt_datei in ZIEL.glob("*.woff2"):      # sonst bleiben Schnitte von früher liegen
        alt_datei.unlink()
    regeln, geladen = [], 0

    for familie in FAMILIEN:
        css = hole(f"https://fonts.googleapis.com/css2?family={familie}&display=swap").decode()
        # Nur die lateinischen Schnitte: Die Seite ist deutsch, alles andere wäre Ballast.
        bloecke = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
        for name, block in bloecke:
            if name not in ("latin", "latin-ext"):
                continue
            adresse = re.search(r"url\((https://[^)]+)\)", block).group(1)
            stil = re.search(r"font-style:\s*(\w+)", block).group(1)
            gewicht = re.search(r"font-weight:\s*([\d ]+)", block).group(1).strip().replace(" ", "bis")
            kurz = familie.split(":")[0].replace("+", "")
            datei = f"{kurz}-{gewicht}-{stil}-{name}.woff2"
            (ZIEL / datei).write_bytes(hole(adresse))
            geladen += 1
            regeln.append(block.replace(adresse, f"fonts/{datei}")
                               .replace("font-display: swap;", "font-display: swap;")
                               .replace("@font-face {", "@font-face {\n  /* " + name + " */"))

    block = ANFANG + "\n" + "\n".join(regeln) + "\n" + ENDE
    text = CSS_DATEI.read_text(encoding="utf-8")
    if ANFANG in text:
        text = re.sub(re.escape(ANFANG) + ".*?" + re.escape(ENDE), block, text, flags=re.S)
    else:
        # Der @import stand ganz oben; er verschwindet mitsamt seiner Zeile.
        text = re.sub(r"^@import url\('https://fonts\.googleapis\.com[^\n]*\n", block + "\n\n",
                      text, count=1, flags=re.M)
    CSS_DATEI.write_text(text, encoding="utf-8")
    (ZIEL / "LIZENZ.txt").write_text(LIZENZ, encoding="utf-8")

    groesse = sum(d.stat().st_size for d in ZIEL.glob("*.woff2"))
    print(f"{geladen} Schriftdateien in {ZIEL.relative_to(WURZEL)} ({groesse // 1024} kB), "
          f"{len(regeln)} @font-face-Regeln in style.css")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
