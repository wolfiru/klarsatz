"""Fehlerarten, interne Steuerausnahmen und die Darstellung von Fehlern für Menschen."""


class KlarsatzFehler(Exception):
    """Basis aller Fehler, die ein Klarsatz-Programm betreffen können."""

    def __init__(self, meldung, zeile=None, spalte=None, laenge=None):
        super().__init__(meldung)
        self.meldung = meldung
        self.zeile = zeile            # 1-basiert
        self.spalte = spalte          # 0-basiert, nur bei Syntaxfehlern bekannt
        self.laenge = laenge          # Länge der markierten Stelle
        self.aufrufe = []             # [(Aufgabenname, Zeile des Aufrufs)], innerste zuerst


class SyntaxFehler(KlarsatzFehler):
    """Der Satz passt auf kein bekanntes Satzmuster."""


class StufenFehler(SyntaxFehler):
    """Das Wort gibt es, aber es gehört zu einer höheren Lernstufe (siehe stufen.py)."""


class LaufzeitFehler(KlarsatzFehler):
    """Fehler beim Ausführen (kann mit 'Versuche ... Bei Fehler' abgefangen werden)."""


class LimitFehler(KlarsatzFehler):
    """Ein Gesamtlimit (Schritte, Zeit, Ausgabe) wurde erreicht – lässt sich NICHT abfangen."""


class _Abbruch(Exception):
    pass


class _Weiter(Exception):
    pass


class _Rueckgabe(Exception):
    def __init__(self, wert):
        self.wert = wert


def _quellzeile(zeilen, nr, spalte=None, laenge=None):
    """Eine Quelltextzeile mit Zeilennummer; bei bekannter Spalte mit ^^^-Markierung darunter."""
    if not (nr and 1 <= nr <= len(zeilen)):
        return []
    text = zeilen[nr - 1].rstrip()
    ausgabe = [f"  {nr:>4} | {text}"]
    if spalte is not None:
        # Tabulatoren so darstellen, dass die Markierung darunter passt
        anzeige = text.expandtabs(4)
        versatz = len(text[:spalte].expandtabs(4))
        ausgabe[0] = f"  {nr:>4} | {anzeige}"
        ausgabe.append("       | " + " " * versatz + "^" * max(1, min(laenge or 1, max(1, len(anzeige) - versatz))))
    return ausgabe


def formatiere_fehler(e, quelltext):
    """Fehlermeldung als Text: Überschrift, betroffene Zeile mit Markierung, Aufrufkette."""
    if isinstance(e, StufenFehler):
        art = "Das kommt später"
    elif isinstance(e, SyntaxFehler):
        art = "Ich verstehe das Programm nicht"
    elif isinstance(e, LimitFehler):
        art = "Abgebrochen"
    else:
        art = "Fehler beim Ausführen"
    if e.zeile:
        wo = f" (Zeile {e.zeile}" + (f", Spalte {e.spalte + 1}" if e.spalte is not None else "") + ")"
    else:
        wo = ""
    zeilen = quelltext.splitlines()
    ausgabe = [f"{art}{wo}: {e.meldung}"]
    ausgabe += _quellzeile(zeilen, e.zeile, e.spalte, e.laenge)
    for aufgabe, aufruf_zeile in e.aufrufe:
        ausgabe.append(f"  … in der Aufgabe „{aufgabe}“, aufgerufen in Zeile {aufruf_zeile}:")
        ausgabe += _quellzeile(zeilen, aufruf_zeile)
    return "\n".join(ausgabe)
