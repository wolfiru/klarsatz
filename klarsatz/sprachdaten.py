"""Die Wörter der Sprache, gruppiert – Grundlage für Syntax-Hervorhebung (VS Code, Pygments, Webseite).

Alles ist aus dem Parser abgeleitet, damit Hervorhebung und Sprache nie auseinanderlaufen."""
from .lexer import FUELLWOERTER
from .parser import RESERVIERT, STARTER

# Wörter, die Programmfluss oder Blöcke steuern
KONTROLLE = {"wenn", "sonst", "ende", "wiederhole", "solange", "zaehle", "fuer", "jedes", "jede", "jeden",
             "hoere", "mach", "weiter", "gib", "zurueck", "versuche", "bei", "fehler", "definiere", "aufgabe",
             "stelle", "sicher", "dass"}

# Weitere Verben am Satzanfang
ANWEISUNGEN = set(STARTER) - KONTROLLE

# Eingebaute Wörter in Ausdrücken. Viele davon sind auch beliebte Variablennamen (Element, Rest, Wert, Zeichen …),
# darum werden sie nur im passenden Zusammenhang hervorgehoben (siehe hervorhebung.py).
FUNKTIONEN_MIT_VON = {"laenge", "wurzel", "betrag", "rest", "kleinbuchstaben", "grossbuchstaben", "zufallszahl",
                      "abgerundet", "aufgerundet", "gerundet", "formatiert", "verkettet", "zahlenwert",
                      "sinus", "kosinus", "cosinus", "tangens",
                      "arkussinus", "arkuskosinus", "arkuscosinus", "arkustangens",
                      "rechtsbuendig", "linksbuendig"}
FUNKTIONEN = FUNKTIONEN_MIT_VON | {"zufaelliges", "zufaellige", "zeichen", "elemente", "element", "erste", "letzte", "wert"}

KONSTANTEN = {"wahr", "falsch"}

# Bindewörter und Vergleiche – alles Reservierte, was nicht schon Steuerwort oder Konstante ist. Wörter, die oft als
# Variablennamen dienen (Zahl, Text, Liste, Antwort, Datei), gehören bewusst nicht dazu.
_EXTRA = {"immer", "namens", "schritten", "stellen", "rueckwaerts", "abwaerts", "absteigend", "keine", "enthaelt",
          # Zeichnen: eindeutige Musterwörter. "Farbe", "Stift" und "Mitte" fehlen bewusst –
          # das sind beliebte Variablennamen.
          "schritte", "grad", "strichstaerke",
          # Zeit: nur "aktuelle" – Stunde, Minute, Tag … sind beliebte Variablennamen.
          "aktuelle", "aktueller", "aktuelles", "aktuellen",
          "sekunde", "sekunden"}
BINDEWOERTER = (set(RESERVIERT) | _EXTRA) - KONTROLLE - KONSTANTEN

ARTIKEL = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem", "einer", "eines"} | FUELLWOERTER


def wort_regex(norm):
    """Regex-Text für ein Wort in normierter Schreibweise: 'zaehle' passt auf Zähle und Zaehle, 'fuer' auf für und fuer."""
    teile, i = [], 0
    ersatz = {"ae": "(?:ä|ae)", "oe": "(?:ö|oe)", "ue": "(?:ü|ue)", "ss": "(?:ß|ss)"}
    while i < len(norm):
        if norm[i:i + 2] in ersatz:
            teile.append(ersatz[norm[i:i + 2]])
            i += 2
        else:
            teile.append(norm[i])
            i += 1
    return "".join(teile)


def alternative(woerter):
    """Ein Regex-Text 'a|b|c', längste Wörter zuerst."""
    return "|".join(wort_regex(w) for w in sorted(woerter, key=lambda w: (-len(w), w)))


GRUPPEN = {"steuerung": KONTROLLE, "anweisungen": ANWEISUNGEN, "funktionen": FUNKTIONEN,
           "konstanten": KONSTANTEN, "bindewoerter": BINDEWOERTER}

# ── Lernstufen ──────────────────────────────────────────────────────────────────
#
# Wer anfängt, soll nicht die ganze Sprache auf einmal vor sich haben. Jede Stufe
# schaltet ein paar Wörter frei; die Reihenfolge folgt den Lektionen des Tutorials.
# Ein Wort steht bei der *frühesten* Stufe, auf der es gebraucht wird — "bis" etwa
# gehört zu den Schleifen, kommt aber schon bei "Zufallszahl von 1 bis 10" vor.
#
# Geprüft wird in stufen.py. Ein Test erzwingt, dass jedes Wort der Sprache hier
# eingeordnet ist, damit die Sperre beim Ausbau der Sprache nicht löchrig wird.

STUFEN_NAMEN = {
    1: "Zeigen, fragen, merken",
    2: "Rechnen",
    3: "Entscheiden",
    4: "Wiederholen",
    5: "Eigene Bausteine",
    6: "Listen und Tabellen",
    7: "Alles",
}

STUFEN = {
    1: {"zeige", "frage", "merke", "als", "und"},

    2: {"setze", "erhoehe", "verringere", "verdopple", "halbiere", "verbinde",
        "plus", "minus", "mal", "geteilt", "durch", "hoch",
        "um", "auf", "von", "mit", "zu", "bis", "immer", "stellen", "fuer",
        "wurzel", "betrag", "rest", "laenge", "zahlenwert", "zufallszahl",
        "abgerundet", "aufgerundet", "gerundet", "formatiert",
        "grossbuchstaben", "kleinbuchstaben"},

    3: {"wenn", "sonst", "ende",
        "ist", "sind", "gleich", "groesser", "kleiner", "mindestens", "hoechstens",
        "teilbar", "nicht", "oder", "keine", "enthaelt", "wahr", "falsch"},

    4: {"wiederhole", "zaehle", "hoere", "mach", "weiter",
        "solange", "jedes", "jede", "jeden", "in",
        "rueckwaerts", "abwaerts", "schritten"},

    5: {"definiere", "aufgabe", "gib", "zurueck", "fuehre", "aus"},

    6: {"erstelle", "fuege", "entferne", "sortiere", "teile", "kopiere", "trage", "ersetze",
        "namens", "hinzu", "absteigend", "bei",
        "element", "elemente", "erste", "letzte", "wert", "verkettet", "zeichen",
        "zufaelliges", "zufaellige", "rechtsbuendig", "linksbuendig"},

    7: {"versuche", "fehler", "stelle", "sicher", "dass",
        "hat", "erschaffe",
        "lies", "schreibe",
        "gehe", "drehe", "hebe", "senke", "nimm", "loesche", "warte",
        "schritte", "grad", "strichstaerke",
        "aktuelle", "aktueller", "aktuelles", "aktuellen", "sekunde", "sekunden",
        "sinus", "kosinus", "cosinus", "tangens",
        "arkussinus", "arkuskosinus", "arkuscosinus", "arkustangens"},
}

HOECHSTE_STUFE = max(STUFEN)

# Wort -> Stufe, auf der es dazukommt.
STUFE_VON_WORT = {wort: nr for nr, woerter in STUFEN.items() for wort in woerter}
