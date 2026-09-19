#!/usr/bin/env python3
"""Prüft alle Klarsatz-Codeblöcke der Webseite gegen den echten Interpreter.

Liest jede HTML-Datei im angegebenen Ordner, zieht den Inhalt aller
<pre class="klar">-Blöcke heraus und schickt ihn durch den Prüfmodus.
Blöcke ohne Frage/Lies/Schreibe werden zusätzlich ausgeführt.

    python3 tools/pruefe_webseite.py /var/www/html/klarsatz
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from klarsatz import web
from klarsatz.grenzen import Grenzen
from klarsatz.pruefer import pruefe

BLOCK = re.compile(r'<pre class="klar"([^>]*)>(.*?)</pre>', re.S)
BRAUCHT_EINGABE = re.compile(r'\b(Frage|Lies|Schreibe)\b', re.I)


def bloecke(pfad: Path):
    text = pfad.read_text(encoding="utf-8")
    for treffer in BLOCK.finditer(text):
        # Blöcke mit data-pruefung="nein" sind bewusst unvollständige Ausschnitte.
        if 'data-pruefung="nein"' in treffer.group(1):
            continue
        roh = re.sub(r"<[^>]+>", "", treffer.group(2))
        quelle = html.unescape(roh).strip("\n")
        zeile = text[: treffer.start()].count("\n") + 1
        yield zeile, quelle


def fuehre_aus(quelltext: str, antworten=()):
    """Führt ein Programm ohne Dateizugriff aus — wie die Spielwiese es tut."""
    return web.laufe(
        quelltext,
        antworten=antworten,
        seed=42,
        grenzen=Grenzen(schritte=200_000, sekunden=5),
    )


def main() -> int:
    ordner = Path(sys.argv[1] if len(sys.argv) > 1 else "/var/www/html/klarsatz")
    dateien = sorted(ordner.glob("*.html"))
    if not dateien:
        print(f"Keine HTML-Dateien in {ordner}", file=sys.stderr)
        return 2

    gesamt = fehlerhaft = ausgefuehrt = hinweise = 0
    for datei in dateien:
        for zeile, quelle in bloecke(datei):
            if not quelle.strip():
                continue
            gesamt += 1
            ort = f"{datei.name}:{zeile}"

            befunde = pruefe(quelle)
            echte = [b for b in befunde if b.schwere == "Fehler"]
            hinweise += len(befunde) - len(echte)
            if echte:
                fehlerhaft += 1
                print(f"\n✗ {ort} — Prüfmodus:")
                for b in echte:
                    print(f"    Zeile {b.zeile}: {b.meldung}")
                print("    " + "\n    ".join(quelle.splitlines()[:4]))
                continue

            if BRAUCHT_EINGABE.search(quelle):
                continue

            try:
                ergebnis = fuehre_aus(quelle)
            except Exception as fehler:  # darf nicht vorkommen
                fehlerhaft += 1
                print(f"\n✗ {ort} — PYTHON-AUSNAHME: {fehler!r}")
                continue

            if ergebnis.fehler:
                fehlerhaft += 1
                zeile_txt = f" (Zeile {ergebnis.fehler_zeile})" if ergebnis.fehler_zeile else ""
                print(f"\n✗ {ort} — {ergebnis.fehlerart}{zeile_txt}: {ergebnis.fehler}")
                print("    " + "\n    ".join(quelle.splitlines()[:4]))
            else:
                ausgefuehrt += 1

    print(f"\n{gesamt} Blöcke geprüft, davon {ausgefuehrt} ausgeführt, "
          f"{fehlerhaft} beanstandet ({hinweise} Hinweise/Warnungen übergangen).")
    return 1 if fehlerhaft else 0


if __name__ == "__main__":
    raise SystemExit(main())
