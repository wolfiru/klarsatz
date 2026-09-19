#!/usr/bin/env python3
"""Schnürt das Archiv zum Herunterladen für die Webseite.

Nimmt alles auf, was jemand braucht, um Klarsatz auf dem eigenen Rechner
auszuprobieren — und lässt weg, was nur den Betrieb dieser Webseite betrifft
(Arbeitsnotizen, Generatoren mit Serverpfaden).

    python3 tools/baue_archiv.py [ZIELORDNER]

Voreinstellung: /var/www/html/klarsatz/downloads
Ergebnis: klarsatz-<version>.zip und die zugehörige SHA256-Prüfsumme.
"""
import hashlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
VORGABE = Path("/var/www/html/klarsatz/downloads")

# Ordner, die vollständig mitkommen.
ORDNER = ["klarsatz", "programme", "beispiele", "docs", "tests", "editor", "playground"]
# Einzelne Dateien im Wurzelverzeichnis.
DATEIEN = ["README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml"]
# Werkzeuge, die auch außerhalb dieser Webseite Sinn ergeben.
WERKZEUGE = ["baue_editor.py", "baue_playground.py", "baue_archiv.py",
             "tokenisiere_js.mjs", "tokenisiere_textmate.js", "package.json"]
# Was nie ins Archiv gehört.
AUS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache"}


def version() -> str:
    text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
    treffer = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    return treffer.group(1) if treffer else "0"


def sammle() -> list[Path]:
    dateien = []
    for name in ORDNER:
        for pfad in sorted((WURZEL / name).rglob("*")):
            if pfad.is_file() and not (set(pfad.parts) & AUS) and pfad.suffix != ".pyc":
                dateien.append(pfad)
    dateien += [WURZEL / n for n in DATEIEN if (WURZEL / n).exists()]
    dateien += [WURZEL / "tools" / n for n in WERKZEUGE if (WURZEL / "tools" / n).exists()]
    return dateien


def main() -> int:
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    ziel.mkdir(parents=True, exist_ok=True)

    v = version()

    # Erzeugte Dateien zuerst auffrischen — sie tragen unter anderem die Versionsnummer.
    # (Sonst wandert eine veraltete VS-Code-Erweiterung ins Archiv.)
    for werkzeug in ("baue_editor.py", "baue_playground.py"):
        ergebnis = subprocess.run([sys.executable, str(WURZEL / "tools" / werkzeug)],
                                  cwd=WURZEL, capture_output=True, text=True)
        if ergebnis.returncode != 0:
            print(ergebnis.stdout + ergebnis.stderr, file=sys.stderr)
            return ergebnis.returncode

    archiv = ziel / f"klarsatz-{v}.zip"
    dateien = sammle()

    # Ältere Fassungen desselben Archivs weichen der neuen.
    for alt in ziel.glob("klarsatz-*.zip*"):
        if alt.name not in (archiv.name, archiv.name + ".sha256"):
            alt.unlink()
            print(f"  entfernt: {alt.name}")

    with zipfile.ZipFile(archiv, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for datei in dateien:
            z.write(datei, Path(f"klarsatz-{v}") / datei.relative_to(WURZEL))

    pruefsumme = hashlib.sha256(archiv.read_bytes()).hexdigest()
    (ziel / f"{archiv.name}.sha256").write_text(f"{pruefsumme}  {archiv.name}\n", encoding="utf-8")

    groesse = round(archiv.stat().st_size / 1024)
    print(f"{archiv}")
    print(f"  {len(dateien)} Dateien, {groesse} kB")
    print(f"  SHA256 {pruefsumme}")

    aktualisiere_seiten(ziel.parent, archiv.name, v, groesse, pruefsumme)
    return 0


def aktualisiere_seiten(webordner: Path, dateiname: str, v: str, groesse: int, pruefsumme: str) -> None:
    """Trägt Dateiname, Version, Größe und Prüfsumme in die Webseiten ein.

    Die Stellen sind dort mit data-download="…" ausgezeichnet, damit sie beim
    nächsten Archivbau nicht von Hand nachgezogen werden müssen."""
    muster = [
        (re.compile(r'(data-download="datei"[^>]*href=")[^"]*(")'), rf'\1downloads/{dateiname}\2'),
        (re.compile(r'(<span data-download="version">)[^<]*(</span>)'), rf'\g<1>{v}\2'),
        (re.compile(r'(<span data-download="groesse">)[^<]*(</span>)'), rf'\g<1>{groesse}\2'),
        (re.compile(r'(<code data-download="sha256">)[^<]*(</code>)'), rf'\g<1>{pruefsumme[:8]}\2'),
        (re.compile(r'(data-download="sha256datei"[^>]*href=")[^"]*(")'),
         rf'\1downloads/{dateiname}.sha256\2'),
        (re.compile(r'(href="downloads/klarsatz-)[0-9.]+(\.zip\.sha256")'), rf'\g<1>{v}\2'),
    ]
    geaendert = 0
    for seite in sorted(webordner.glob("*.html")):
        text = neu = seite.read_text(encoding="utf-8")
        for regex, ersatz in muster:
            neu = regex.sub(ersatz, neu)
        if neu != text:
            seite.write_text(neu, encoding="utf-8")
            geaendert += 1
    print(f"  {geaendert} Webseiten mit den neuen Angaben versehen")

    werkzeug = WURZEL / "tools" / "stempel_webseite.py"
    if werkzeug.exists():
        subprocess.run([sys.executable, str(werkzeug), str(webordner)])


if __name__ == "__main__":
    raise SystemExit(main())
