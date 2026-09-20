#!/usr/bin/env python3
"""Erzeugt Signet und Wortmarke von Klarsatz.

    python3 tools/baue_logo.py

Das **Signet** sind drei Textzeilen, deren letzte im goldenen Punkt endet — der Punkt
am Satzende ist die eine Regel, über die bei Klarsatz jeder stolpert, und das, was
einen Satz erst zum Satz macht. Es ist reine Geometrie und steht hier im Quelltext.

Die **Wortmarke** ist „Klarsatz" in Fraunces, „satz" kursiv in Gold. Ihre Buchstaben
werden zu Pfaden umgerechnet: Eine SVG-Datei mit `font-family` sähe überall anders aus,
wo die Schrift fehlt — auf GitHub etwa, oder in einer Vorschau. Dafür wird Fraunces
einmalig von Google Fonts geholt (OFL); gespeichert wird nur das Ergebnis.

Gebraucht wird fontTools. Fehlt es, bleiben die vorhandenen Dateien liegen.
"""
import re
import sys
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "webseite" / "assets"

INK, INK2, PAPER, GOLD = "#0c0e0b", "#151812", "#f3efe6", "#d9b45a"
GOLD_DUNKEL = "#b38b28"          # auf hellem Grund hat das helle Gold zu wenig Kontrast

CSS = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;1,9..144,600")


# ── Signet ─────────────────────────────────────────────────────────────────

def signet(kachel=True, auf_hell=False, klein=False, einfarbig=False, groesse=64):
    """Drei Zeilen Text, die letzte endet im Punkt.

    `kachel`: mit abgerundetem Untergrund (für Avatare und App-Symbole) oder frei
    stehend (für die Seite, wo der Untergrund schon dunkel ist).
    `klein`: die vereinfachte Fassung für 16 bis 32 Pixel — zwei Zeilen statt drei
    und ein größerer Punkt, weil feine Linien in dieser Größe zu Matsch werden."""
    linie = INK if auf_hell else PAPER
    punkt = GOLD_DUNKEL if auf_hell else GOLD
    if einfarbig:
        # Für Stempel, Stickerei, Fax und alles, was nur eine Farbe kennt: Der Punkt
        # trägt dann allein durch seine Form, nicht durch Gold.
        linie = punkt = "currentColor"
    teile = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{groesse}" '
             f'height="{groesse}" role="img" aria-label="Klarsatz">',
             "<title>Klarsatz</title>",
             "<desc>Textzeilen; die letzte endet in einem goldenen Punkt — "
             "dem Punkt, mit dem in Klarsatz jeder Satz schließt.</desc>"]
    if kachel:
        # Nicht die Seitenfarbe: Sonst verschwindet die Kachel auf dunklem Grund.
        # Die Haarlinie in Gold hält sie auch dort zusammen.
        teile.append(f'<rect x="0.75" y="0.75" width="62.5" height="62.5" rx="14" fill="{INK2}" '
                     f'stroke="{GOLD}" stroke-opacity="0.3" stroke-width="1.5"/>')

    if klein:
        # Zwei kräftige Zeilen, ein großer Punkt: Das überlebt 16 Pixel.
        for y, breite in ((22, 34), (36, 17)):
            teile.append(f'<rect x="12" y="{y}" width="{breite}" height="6" rx="3" '
                         f'fill="{linie}" opacity="{0.75 if einfarbig else 0.62}"/>')
        teile.append(f'<circle cx="40" cy="39" r="7" fill="{punkt}"/>')
    else:
        # Unterschiedlich lange Zeilen, wie gesetzter Text. Die dritte bricht früh ab,
        # damit der Punkt Platz hat — er ist das eigentliche Zeichen.
        for y, breite in ((19, 28), (29, 37), (39, 19)):
            teile.append(f'<rect x="13" y="{y}" width="{breite}" height="3.4" rx="1.7" '
                         f'fill="{linie}" opacity="{0.7 if einfarbig else 0.55}"/>')
        teile.append(f'<circle cx="39" cy="40.7" r="4" fill="{punkt}"/>')

    teile.append("</svg>")
    return "\n".join(teile) + "\n"


# ── Wortmarke ──────────────────────────────────────────────────────────────

def _schriftdateien():
    kopf = {"User-Agent": "Mozilla/4.0"}          # so liefert Google TTF statt WOFF2
    css = urllib.request.urlopen(urllib.request.Request(CSS, headers=kopf)).read().decode()
    adressen = re.findall(r"url\((https://[^)]+\.ttf)\)", css)
    stile = re.findall(r"font-style: (\w+);", css)
    nach_stil = dict(zip(stile, adressen))
    return {stil: urllib.request.urlopen(nach_stil[stil]).read() for stil in ("normal", "italic")}


def _wort_als_pfad(schrift, wort, x, groesse):
    """Gibt (Pfaddaten, neue x-Position) zurück — Buchstabe für Buchstabe gesetzt."""
    from fontTools.pens.svgPathPen import SVGPathPen

    glyphen = schrift.getGlyphSet()
    cmap = schrift.getBestCmap()
    einheiten = schrift["head"].unitsPerEm
    faktor = groesse / einheiten
    stuecke = []
    for zeichen in wort:
        name = cmap[ord(zeichen)]
        stift = SVGPathPen(glyphen)
        glyphen[name].draw(stift)
        daten = stift.getCommands()
        if daten:
            stuecke.append(f'<path transform="translate({x:.2f} 0) scale({faktor:.6f} {-faktor:.6f})" '
                           f'd="{daten}"/>')
        x += glyphen[name].width * faktor
    return stuecke, x


def wortmarke(schriften, auf_hell=False, groesse=100):
    from fontTools.ttLib import TTFont
    import io

    normal = TTFont(io.BytesIO(schriften["normal"]))
    kursiv = TTFont(io.BytesIO(schriften["italic"]))

    klar, x = _wort_als_pfad(normal, "Klar", 0, groesse)
    satz, breite = _wort_als_pfad(kursiv, "satz", x, groesse)

    # Kasten aus den Schriftmaßen, nicht aus den Umrissen: So sitzt die Marke immer gleich.
    oben = normal["hhea"].ascent * groesse / normal["head"].unitsPerEm
    unten = -normal["hhea"].descent * groesse / normal["head"].unitsPerEm
    rand = groesse * 0.06
    hoehe = oben + unten
    farbe_klar = INK if auf_hell else PAPER
    farbe_satz = GOLD_DUNKEL if auf_hell else GOLD

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-rand:.1f} {-oben:.1f} '
            f'{breite + 2 * rand:.1f} {hoehe:.1f}" width="{breite + 2 * rand:.0f}" '
            f'height="{hoehe:.0f}" role="img" aria-label="Klarsatz">\n'
            f"<title>Klarsatz</title>\n"
            f'<g fill="{farbe_klar}">' + "".join(klar) + "</g>\n"
            f'<g fill="{farbe_satz}">' + "".join(satz) + "</g>\n"
            "</svg>\n")


def _rastere(html, breite, hoehe, ziel):
    """Macht aus HTML ein PNG — für Avatar, Touch-Symbol und Vorschaubild."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        seite = browser.new_page(viewport={"width": breite, "height": hoehe}, device_scale_factor=1)
        seite.set_content(html)
        seite.wait_for_timeout(400)
        seite.screenshot(path=str(ziel))
        browser.close()


def _bilder():
    """Avatar (512), Touch-Symbol (180) und das Vorschaubild geteilter Links (1200×630)."""
    # Die Grafiken werden direkt eingehängt statt verlinkt: Eine per set_content gesetzte
    # Seite darf keine file://-Bilder nachladen, sie blieben leer.
    def eingehaengt(datei, stil):
        svg = (ZIEL / datei).read_text(encoding="utf-8")
        svg = svg.replace("<svg ", f'<svg style="{stil}" ', 1)
        return svg

    quadrat = '<body style="margin:0;line-height:0">SVG</body>'

    karte = (
        '<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Fraunces:ital,opsz,wght@0,9..144,600;1,9..144,600&family=Manrope:wght@500&display=swap">'
        '</head><body style="margin:0;width:1200px;height:630px;background:' + INK + ';'
        'display:flex;flex-direction:column;justify-content:center;gap:34px;padding:0 96px;'
        'font-family:Manrope,system-ui,sans-serif;box-sizing:border-box">'
        '<div style="display:flex;align-items:center;gap:28px">SIGNET WORTMARKE</div>'
        '<p style="margin:0;color:' + PAPER + ';font-family:Fraunces,Georgia,serif;font-size:54px;'
        'line-height:1.18;max-width:940px">Programmieren lernen,<br>ohne vorher eine '
        '<em style="color:' + GOLD + '">Fremdsprache</em> zu übersetzen.</p>'
        '<p style="margin:0;color:#b9b4a5;font-size:25px">Eine Programmiersprache, deren Befehle '
        'deutsche Sätze sind · ruthner.at/klarsatz</p></body></html>')

    for datei, groesse, quelle in (("klarsatz-avatar-512.png", 512, "klarsatz-signet.svg"),
                                   ("apple-touch-icon.png", 180, "klarsatz-signet-klein.svg"),
                                   ("editor-icon-128.png", 128, "klarsatz-signet-klein.svg")):
        _rastere(quadrat.replace("SVG", eingehaengt(quelle, f"width:{groesse}px;height:{groesse}px")),
                 groesse, groesse, ZIEL / datei)
        yield datei

    html = (karte.replace("SIGNET", eingehaengt("klarsatz-signet.svg", "width:92px;height:92px"))
                 .replace("WORTMARKE", eingehaengt("klarsatz-wortmarke.svg", "height:76px;width:auto")))
    _rastere(html, 1200, 630, ZIEL / "klarsatz-vorschau.png")
    yield "klarsatz-vorschau.png"

    # Die VS-Code-Erweiterung braucht ihr Symbol im eigenen Ordner.
    ext = WURZEL / "editor" / "vscode-klarsatz"
    if ext.exists():
        (ext / "icon.png").write_bytes((ZIEL / "editor-icon-128.png").read_bytes())


def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    geschrieben = []

    for name, inhalt in (("klarsatz-signet.svg", signet()),
                         ("klarsatz-signet-klein.svg", signet(klein=True)),
                         ("klarsatz-signet-blank.svg", signet(kachel=False)),
                         ("klarsatz-signet-auf-hell.svg", signet(kachel=False, auf_hell=True)),
                         ("klarsatz-signet-einfarbig.svg", signet(kachel=False, einfarbig=True))):
        (ZIEL / name).write_text(inhalt, encoding="utf-8")
        geschrieben.append(name)

    try:
        from fontTools.ttLib import TTFont            # noqa: F401  (nur zum Prüfen)
    except ImportError:
        print("fontTools fehlt — die Wortmarke bleibt, wie sie ist.", file=sys.stderr)
    else:
        try:
            schriften = _schriftdateien()
        except OSError as fehler:
            print(f"Fraunces nicht erreichbar ({fehler}) — die Wortmarke bleibt, wie sie ist.",
                  file=sys.stderr)
        else:
            for name, inhalt in (("klarsatz-wortmarke.svg", wortmarke(schriften)),
                                 ("klarsatz-wortmarke-auf-hell.svg", wortmarke(schriften, auf_hell=True))):
                (ZIEL / name).write_text(inhalt, encoding="utf-8")
                geschrieben.append(name)

    try:
        geschrieben += list(_bilder())
    except ImportError:
        print("playwright fehlt — die PNG-Fassungen bleiben, wie sie sind.", file=sys.stderr)

    for name in geschrieben:
        print(f"  {(ZIEL / name).relative_to(WURZEL)}  ({(ZIEL / name).stat().st_size} Bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
