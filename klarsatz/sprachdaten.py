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
