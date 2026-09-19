#!/usr/bin/env python3
"""Baut aus docs/TUTORIAL.md die Tutorial-Seite der Webseite.

    python3 tools/baue_tutorial.py [ZIELORDNER]      Voreinstellung: /var/www/html/klarsatz

Eine Quelle, zwei Ausgaben: Das Tutorial wird als Markdown geschrieben (dort prüft es
`tests/test_tutorial.py` Block für Block nach) und hier zur Webseite gemacht. Damit kann die
Seite nicht von der geprüften Fassung abweichen.

Der Markdown-Umfang ist bewusst klein — genau das, was das Tutorial benutzt: Überschriften,
Absätze, Aufzählungen, Tabellen, Zitate, Trennlinien, Codeblöcke (`klar`, `eingabe`, `ausgabe`)
sowie **fett**, *kursiv*, `Code` und Verweise. Keine Fremdbibliothek, wie im ganzen Projekt.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "docs" / "TUTORIAL.md"
VORGABE = Path("/var/www/html/klarsatz")

# Verweise, die im Markdown auf Dateien zeigen, führen auf der Webseite woandershin.
UMLEITUNG = {
    "SPRACHE.md": "doku-referenz.html",
    "PROGRAMME.md": "https://github.com/wolfiru/klarsatz/blob/main/docs/PROGRAMME.md",
    "https://www.ruthner.at/klarsatz/spielplatz.html": "spielplatz.html",
    "https://www.ruthner.at/klarsatz/doku-zeichnen.html": "doku-zeichnen.html",
}


def anker(text):
    """Aus einer Überschrift eine Sprungmarke machen — wie GitHub es tut."""
    # Dieselbe Regel wie auf GitHub, damit die Verweise im Markdown auch hier stimmen:
    # kleinschreiben, Satzzeichen weg, jedes einzelne Leerzeichen wird ein Bindestrich.
    # Aus "Lektion 1 — Der erste Satz" wird darum "lektion-1--der-erste-satz" (zwei
    # Bindestriche, weil der Gedankenstrich verschwindet, seine Leerzeichen aber bleiben).
    wert = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"\s", "-", wert.strip()).strip("-")


def inline(text):
    """**fett**, *kursiv*, `Code`, [Text](Ziel) — in dieser Reihenfolge, damit sich nichts beißt."""
    teile = []
    for i, stueck in enumerate(re.split(r"(`[^`]+`)", text)):
        if i % 2:                                  # unveränderter Code-Schnipsel
            teile.append(f"<code>{html.escape(stueck[1:-1])}</code>")
            continue
        s = html.escape(stueck)

        def verweis(m):
            ziel = UMLEITUNG.get(m.group(2), m.group(2))
            extern = ' rel="noopener"' if ziel.startswith("http") else ""
            return f'<a href="{ziel}"{extern}>{m.group(1)}</a>'

        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", verweis, s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
        teile.append(s)
    return "".join(teile)


def tabelle(zeilen):
    """Eine Markdown-Tabelle. Die zweite Zeile (---) gibt nur die Ausrichtung an."""
    def zellen(z):
        return [c.strip() for c in z.strip().strip("|").split("|")]

    kopf = zellen(zeilen[0])
    aus = ['<div class="tabelle-rahmen">', "<table>", "<thead><tr>"]
    aus += [f"<th>{inline(c)}</th>" for c in kopf]
    aus += ["</tr></thead>", "<tbody>"]
    for z in zeilen[2:]:
        aus.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in zellen(z)) + "</tr>")
    aus += ["</tbody>", "</table>", "</div>"]
    return aus


def codeblock(art, inhalt):
    roh = html.escape("\n".join(inhalt))
    if art == "klar":
        return [f'<pre class="klar"><code>{roh}</code></pre>']
    beschriftung = "Deine Eingaben" if art == "eingabe" else "Das kommt heraus"
    return [f'<div class="tut-{art}"><span class="tut-marke">{beschriftung}</span>',
            f"<pre><code>{roh}</code></pre></div>"]


def nach_html(markdown):
    zeilen = markdown.split("\n")
    aus, lektionen = [], []
    i = 0
    while i < len(zeilen):
        z = zeilen[i]

        if z.startswith("```"):
            art = z[3:].strip() or "text"
            inhalt, i = [], i + 1
            while i < len(zeilen) and not zeilen[i].startswith("```"):
                inhalt.append(zeilen[i])
                i += 1
            i += 1
            aus += codeblock(art, inhalt)
            continue

        if z.startswith("# "):                       # Titel steht schon im Seitenkopf
            i += 1
            continue

        if z.startswith("## "):
            titel = z[3:].strip()
            marke = anker(titel)
            if titel.startswith("Lektion"):
                lektionen.append((marke, titel))
            aus.append(f'<h2 id="{marke}">{inline(titel)}</h2>')
            i += 1
            continue

        if z.startswith("### "):
            aus.append(f"<h3>{inline(z[4:].strip())}</h3>")
            i += 1
            continue

        if z.strip() == "---":
            aus.append("<hr>")
            i += 1
            continue

        if z.startswith("|"):
            block = []
            while i < len(zeilen) and zeilen[i].startswith("|"):
                block.append(zeilen[i])
                i += 1
            aus += tabelle(block)
            continue

        if z.startswith("> "):
            block = []
            while i < len(zeilen) and zeilen[i].startswith("> "):
                block.append(zeilen[i][2:])
                i += 1
            aus.append(f"<blockquote><p>{inline(' '.join(block))}</p></blockquote>")
            continue

        if z.startswith("* "):
            aus.append("<ul>")
            while i < len(zeilen) and (zeilen[i].startswith("* ") or zeilen[i].startswith("  ")):
                if zeilen[i].startswith("* "):
                    aus.append(f"<li>{inline(zeilen[i][2:].strip())}")
                    i += 1
                    while i < len(zeilen) and zeilen[i].startswith("  ") and zeilen[i].strip():
                        aus.append(" " + inline(zeilen[i].strip()))
                        i += 1
                    aus.append("</li>")
                else:
                    i += 1
            aus.append("</ul>")
            continue

        if not z.strip():
            i += 1
            continue

        absatz = []
        while i < len(zeilen) and zeilen[i].strip() and not zeilen[i].startswith(("#", "|", ">", "* ", "```", "---")):
            absatz.append(zeilen[i].strip())
            i += 1
        aus.append(f"<p>{inline(' '.join(absatz))}</p>")

    return "\n".join(aus), lektionen


GERUEST = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Klarsatz in elf Lektionen lernen — vom ersten Satz bis zum eigenen Spiel. Jedes Beispiel läuft, alle Ausgaben werden nachgerechnet.">
<meta name="theme-color" content="#0c0e0b">
<title>Klarsatz lernen — Tutorial</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230c0e0b'/%3E%3Crect x='14' y='20' width='28' height='3' rx='1.5' fill='%23d9b45a'/%3E%3Crect x='14' y='30' width='36' height='3' rx='1.5' fill='%23f3efe6' opacity='.6'/%3E%3Crect x='14' y='40' width='20' height='3' rx='1.5' fill='%23f3efe6' opacity='.6'/%3E%3Crect x='38' y='40' width='4' height='3' rx='1.5' fill='%23d9b45a'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<canvas id="manuskript"></canvas>
<div class="bg-overlay"></div>
<div class="grain"></div>

<nav class="nav">
    <div class="nav-start">
        <a class="heim" href="/" aria-label="Zur Startseite von ruthner.at">
            <img src="/monogram.png" alt="" width="414" height="516" decoding="async">
            <span>ruthner<em>.at</em></span>
        </a>
        <span class="nav-teiler" aria-hidden="true"></span>
        <a class="brand" href="index.html"><span class="brand-mark"></span><span>Klar<em>satz</em></span></a>
    </div>
    <div class="nav-links">
        <a href="index.html">Sprache</a>
        <a href="tutorial.html">Tutorial</a>
        <a href="doku.html">Dokumentation</a>
        <a href="spielplatz.html" class="nav-cta">Spielplatz</a>
    </div>
</nav>

<header class="seitenkopf">
    <p class="kicker">Tutorial · elf Lektionen</p>
    <h1>Klarsatz lernen</h1>
</header>

<main>
<div class="doku-layout">

    <aside class="doku-seitenleiste">
        <span class="sl-titel">Lektionen</span>
        <ol>
__LEKTIONEN__
        </ol>
    </aside>

    <article class="doku-inhalt tut-inhalt">
__INHALT__

<nav class="blaettern">
    <a href="doku.html"><span class="bl-label">Danach</span>Die Dokumentation</a>
    <a href="spielplatz.html"><span class="bl-label">Sofort</span>Im Spielplatz üben</a>
</nav>

    </article>

</div>
</main>

<footer>
    <div class="foot-inner">
        <span>© <span id="jahr"></span> ruthner.at · Klarsatz <span data-download="version">0.7.1</span></span>
        <span><a href="/">ruthner.at</a> &nbsp;·&nbsp; <a href="index.html">Sprache</a> &nbsp;·&nbsp; <a href="doku.html">Dokumentation</a> &nbsp;·&nbsp; <a href="spielplatz.html">Spielplatz</a> &nbsp;·&nbsp; <a href="https://github.com/wolfiru/klarsatz" rel="noopener">GitHub</a></span>
    </div>
</footer>

<script src="assets/manuskript-bg.js"></script>
<script src="assets/app.js"></script>
<script type="module" src="assets/code-hervorhebung.js"></script>
</body>
</html>
"""


def main() -> int:
    ziel = Path(sys.argv[1]) if len(sys.argv) > 1 else VORGABE
    if not ziel.is_dir():
        print(f"Zielordner {ziel} gibt es nicht.", file=sys.stderr)
        return 2

    inhalt, lektionen = nach_html(QUELLE.read_text(encoding="utf-8"))
    liste = "\n".join(f'            <li><a href="#{marke}">{html.escape(titel.split("—", 1)[-1].strip())}</a></li>'
                      for marke, titel in lektionen)
    seite = GERUEST.replace("__LEKTIONEN__", liste).replace("__INHALT__", inhalt)
    (ziel / "tutorial.html").write_text(seite, encoding="utf-8")
    print(f"gebaut: tutorial.html ({len(seite)} Bytes, {len(lektionen)} Lektionen)")

    werkzeug = WURZEL / "tools" / "stempel_webseite.py"
    if werkzeug.exists():
        subprocess.run([sys.executable, str(werkzeug), str(ziel)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
