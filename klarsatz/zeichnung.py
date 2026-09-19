"""Striche in ein SVG-Bild verwandeln.

Der Interpreter zeichnet nicht selbst, er meldet nur Striche
("linie", x1, y1, x2, y2, farbe, breite) in einem Koordinatensystem, dessen
Ursprung in der Mitte liegt und dessen y-Achse nach **oben** zeigt — so wie im
Matheunterricht. Hier wird daraus ein Bild: y wird gespiegelt, der Ausschnitt
richtet sich nach dem, was tatsächlich gezeichnet wurde.
"""

RAND = 24


def _ausschnitt(striche):
    xs = [x for _, x1, _, x2, _, _, _ in striche for x in (x1, x2)]
    ys = [y for _, _, y1, _, y2, _, _ in striche for y in (y1, y2)]
    breiteste = max((b for *_, b in striche), default=1)
    rand = RAND + breiteste
    return (min(xs) - rand, min(ys) - rand, max(xs) + rand, max(ys) + rand)


def als_svg(striche, hintergrund="#0c0e0b"):
    """Gibt die Striche als vollständiges SVG-Dokument zurück."""
    if not striche:
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
                f'<rect width="100" height="100" fill="{hintergrund}"/></svg>')

    links, unten, rechts, oben = _ausschnitt(striche)
    breite, hoehe = rechts - links, oben - unten

    teile = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {breite:.1f} {hoehe:.1f}" '
             f'width="{breite:.0f}" height="{hoehe:.0f}">',
             f'<rect width="100%" height="100%" fill="{hintergrund}"/>',
             '<g stroke-linecap="round" stroke-linejoin="round" fill="none">']

    for _, x1, y1, x2, y2, farbe, dicke in striche:
        # y spiegeln: im Bild wächst y nach unten, in der Sprache nach oben.
        teile.append(f'<path d="M{x1 - links:.1f} {oben - y1:.1f}L{x2 - links:.1f} {oben - y2:.1f}" '
                     f'stroke="{farbe}" stroke-width="{dicke}"/>')

    teile.append("</g></svg>")
    return "".join(teile)
