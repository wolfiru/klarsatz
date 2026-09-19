"""Lernstufen: nur so viel Sprache zeigen, wie gerade gelernt wurde.

Wer anfängt, hat mit `Zeige`, `Frage` und `Merke` schon ein Programm. Alles andere wartet.
Greift jemand zu früh nach einem Wort, sagt Klarsatz freundlich, wo es hingehört:

    Das lernst du in Stufe 3 (Entscheiden) — du bist gerade auf Stufe 1.

Die Einteilung steht in `sprachdaten.py` neben den Wortgruppen, damit es **eine** Regelliste
bleibt. Hier steht nur, wie geprüft wird.

**Geprüft wird nur, was eindeutig ist.** Reservierte Wörter (`wenn`, `plus`, `hinzu` …) können nie
ein Variablenname sein — die lassen sich gefahrlos sperren. Funktionswörter wie `Wurzel` oder
`Element` sind dagegen erlaubte Namen; sie gelten nur dann als Funktion, wenn auch das Muster
stimmt (bei `Wurzel` also ein `von` dahinter, genau wie der Parser es liest). Im Zweifel wird
**nicht** gesperrt: Eine Lücke in der Lernhilfe ist ärgerlich, ein fälschlich abgelehntes
Programm wäre schlimmer.
"""
from .fehler import StufenFehler
from .parser import RESERVIERT, STARTER
from .sprachdaten import (FUNKTIONEN_MIT_VON, HOECHSTE_STUFE, STUFEN_NAMEN, STUFE_VON_WORT)

# Reservierte Wörter können nie ein Name sein — die dürfen wir ohne Zusammenhang beurteilen.
EINDEUTIG = set(RESERVIERT)

# Satzanfänge (Zeige, Merke, Versuche …) sind nur **am Satzanfang** Befehle. `Versuche` ist
# mittendrin ein völlig normaler Variablenname — das Ratespiel im Tutorial benutzt ihn so.
NUR_AM_SATZANFANG = set(STARTER) - EINDEUTIG


def name(stufe):
    """'3 (Entscheiden)' — für Meldungen und Hilfetexte."""
    return f"{stufe} ({STUFEN_NAMEN[stufe]})"


def erlaubte_woerter(stufe):
    """Alles bis einschließlich dieser Stufe."""
    return {w for w, n in STUFE_VON_WORT.items() if n <= stufe}


def _gilt_als_funktion(tokens, i):
    """`Wurzel von 4` ist eine Funktion, `Merke 4 als Wurzel` ist ein Name."""
    folgt = tokens[i + 1] if i + 1 < len(tokens) else None
    return folgt is not None and folgt.art == "WORT" and folgt.norm == "von"


def _steht_am_satzanfang(tokens, i):
    """Ein Satz fängt am Programmanfang an oder nach '.' bzw. ':'."""
    return i == 0 or tokens[i - 1].art in (".", ":")


def pruefe(tokens, stufe):
    """Wirft einen SyntaxFehler, sobald ein Wort über der erlaubten Stufe auftaucht."""
    if stufe is None or stufe >= HOECHSTE_STUFE:
        return
    if stufe < 1:
        raise ValueError(f"Stufe {stufe} gibt es nicht — erlaubt ist 1 bis {HOECHSTE_STUFE}.")

    for i, t in enumerate(tokens):
        if t.art != "WORT":
            continue
        noetig = STUFE_VON_WORT.get(t.norm)
        if noetig is None or noetig <= stufe:
            continue
        if t.norm not in EINDEUTIG:
            # Mehrdeutig: nur sperren, wenn das Wort auch wirklich als Befehl oder
            # Funktion dasteht — sonst ist es ein ganz normaler Name.
            befehl = t.norm in NUR_AM_SATZANFANG and _steht_am_satzanfang(tokens, i)
            funktion = t.norm in FUNKTIONEN_MIT_VON and _gilt_als_funktion(tokens, i)
            if not (befehl or funktion):
                continue
        raise StufenFehler(
            f"'{t.wert}' lernst du in Stufe {name(noetig)} — du bist gerade auf Stufe {name(stufe)}.",
            t.zeile, t.spalte, t.laenge)


def uebersicht():
    """Eine kurze Übersicht für `--stufen` und die Hilfe."""
    zeilen = []
    for nr in sorted(STUFEN_NAMEN):
        woerter = sorted(w for w, n in STUFE_VON_WORT.items() if n == nr)
        zeilen.append(f"Stufe {nr} — {STUFEN_NAMEN[nr]}")
        zeilen.append("    " + ", ".join(woerter))
    return "\n".join(zeilen)
