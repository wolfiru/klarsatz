"""Übungsaufgaben, die sich selbst prüfen.

Eine Aufgabe besteht aus einer Angabe, einer oder mehreren **Proben** und einer
Musterlösung. Eine Probe sind Eingaben plus Regeln: Was muss herauskommen, wenn
jemand *diese* Antworten tippt?

Geprüft wird bewusst **nicht auf wortgleiche Ausgabe** — das wäre spröde und würde
jede Lösung ablehnen, die dasselbe tut und es anders sagt. Stattdessen gibt es eine
Handvoll Regeln, die auf das Wesentliche zeigen:

    enthält: Hallo            in der Ausgabe kommt dieser Text vor
    enthält nicht: Fehler     … und dieser nicht
    letzte Zeile: 42          die letzte Ausgabezeile, genau (Leerraum egal)
    zeilen: 3                 so viele Ausgabezeilen
    fragt: 2                  so oft wird gefragt
    striche: 4                so viele Striche entstehen in der Zeichnung
    benutzt: Wiederhole       das Wort steht im Quelltext (für „nimm eine Schleife")
    benutzt nicht: 42         … und dieses nicht (gegen das Hinschreiben der Antwort)

Jede Regel sagt bei Misserfolg selbst, was sie erwartet hat — daraus wird die
Rückmeldung an den Lernenden. Das Modul kommt ohne Fremdteile aus und läuft
deshalb auch im Browser.
"""
import re
from dataclasses import dataclass, field

REGELN = ("enthält", "enthält nicht", "letzte zeile", "zeilen", "fragt", "striche",
          "benutzt", "benutzt nicht")


@dataclass
class Regel:
    art: str
    wert: str

    @property
    def text(self):
        """Wie die Regel dem Lernenden angekündigt wird."""
        eins = self.wert.strip() == "1"
        return {
            "enthält": f'Die Ausgabe enthält „{self.wert}".',
            "enthält nicht": f'Die Ausgabe enthält „{self.wert}" nicht.',
            "letzte zeile": f'Die letzte Zeile ist „{self.wert}".',
            "zeilen": f"Die Ausgabe hat {self.wert} Zeile" + ("." if eins else "n."),
            "fragt": "Das Programm fragt einmal." if eins else f"Das Programm fragt {self.wert} Mal.",
            "striche": f"Die Zeichnung hat {self.wert} Strich" + ("." if eins else "e."),
            "benutzt": f'Im Programm kommt „{self.wert}" vor.',
            "benutzt nicht": f'Im Programm kommt „{self.wert}" nicht vor.',
        }[self.art]

    def pruefe(self, lauf, quelltext):
        """Wahr, wenn diese Regel erfüllt ist. `lauf` ist ein web.Ergebnis."""
        ausgabe = "\n".join(lauf.ausgabe)
        if self.art == "enthält":
            return self.wert.lower() in ausgabe.lower()
        if self.art == "enthält nicht":
            return self.wert.lower() not in ausgabe.lower()
        if self.art == "letzte zeile":
            letzte = lauf.ausgabe[-1].strip() if lauf.ausgabe else ""
            return letzte.lower() == self.wert.strip().lower()
        if self.art == "zeilen":
            return len(lauf.ausgabe) == int(self.wert)
        if self.art == "fragt":
            return sum(1 for e in lauf.verlauf if e[0] == "frage") == int(self.wert)
        if self.art == "striche":
            return sum(1 for e in lauf.verlauf if e[0] == "linie") == int(self.wert)
        if self.art == "benutzt":
            return self.wert.lower() in quelltext.lower()
        if self.art == "benutzt nicht":
            return self.wert.lower() not in quelltext.lower()
        raise ValueError(f"Unbekannte Regel: {self.art}")


@dataclass
class Probe:
    """Ein Durchlauf mit festen Eingaben und den Regeln dafür."""
    eingaben: list = field(default_factory=list)
    regeln: list = field(default_factory=list)
    zeile: int = 0


@dataclass
class Aufgabe:
    nummer: str
    titel: str
    stufe: int
    lektion: str
    angabe: str
    proben: list = field(default_factory=list)
    loesung: str = ""
    gegenprobe: str = ""          # absichtlich unzureichend: muss durchfallen
    zeile: int = 0

    @property
    def kennung(self):
        return f"A{self.nummer}"


@dataclass
class Befund:
    """Das Ergebnis einer Prüfung — für einen Lernenden lesbar."""
    bestanden: bool
    proben: list = field(default_factory=list)     # [(bestanden, [(bestanden, Regeltext)], Fehler)]

    @property
    def offen(self):
        """Die Regeltexte, die noch nicht erfüllt sind."""
        return [text for _b, regeln, _f in self.proben for erfuellt, text in regeln if not erfuellt]


def pruefe(aufgabe, quelltext, laufe):
    """Prüft eine Lösung. `laufe(quelltext, antworten)` liefert ein web.Ergebnis."""
    proben = []
    for probe in aufgabe.proben:
        lauf = laufe(quelltext, probe.eingaben)
        if lauf.zustand == "fehler":
            proben.append((False, [(False, r.text) for r in probe.regeln], lauf.fehler))
            continue
        if lauf.zustand == "wartet":
            fehlt = ("Das Programm fragt öfter, als diese Probe Antworten hat. "
                     f"Zuletzt: {lauf.frage}")
            proben.append((False, [(False, r.text) for r in probe.regeln], fehlt))
            continue
        einzeln = [(r.pruefe(lauf, quelltext), r.text) for r in probe.regeln]
        proben.append((all(b for b, _t in einzeln), einzeln, None))
    return Befund(bool(proben) and all(b for b, _r, _f in proben), proben)


# ── Aufgaben aus der Markdown-Datei lesen ──────────────────────────────────

_KOPF = re.compile(r"^## (\d+) — (.+)$")
_UNTERTITEL = re.compile(r"^\*Stufe (\d+) · (.+)\*$")


def lies(text):
    """Liest `docs/AUFGABEN.md` und gibt die Aufgaben in ihrer Reihenfolge zurück."""
    aufgaben, zeilen, i = [], text.split("\n"), 0
    while i < len(zeilen):
        kopf = _KOPF.match(zeilen[i])
        if kopf:
            aufgaben.append(Aufgabe(nummer=kopf.group(1), titel=kopf.group(2).strip(),
                                    stufe=0, lektion="", angabe="", zeile=i + 1))
            i += 1
            continue
        if aufgaben:
            unter = _UNTERTITEL.match(zeilen[i].strip())
            if unter:
                aufgaben[-1].stufe = int(unter.group(1))
                aufgaben[-1].lektion = unter.group(2).strip()
                i += 1
                continue
            block = re.match(r"^```(probe|loesung|gegenprobe)\s*$", zeilen[i])
            if block:
                art, start, inhalt = block.group(1), i + 1, []
                i += 1
                while i < len(zeilen) and zeilen[i].strip() != "```":
                    inhalt.append(zeilen[i])
                    i += 1
                i += 1
                _nimm_block(aufgaben[-1], art, inhalt, start)
                continue
            # Trennlinien und Überschriften gehören nicht zur Angabe.
            if zeilen[i].strip() and not zeilen[i].startswith("#") \
                    and not re.fullmatch(r"-{3,}", zeilen[i].strip()):
                aufgaben[-1].angabe += zeilen[i].strip() + " "
        i += 1
    for a in aufgaben:
        a.angabe = a.angabe.strip()
    return aufgaben


def _nimm_block(aufgabe, art, inhalt, zeile):
    if art == "loesung":
        aufgabe.loesung = "\n".join(inhalt).strip() + "\n"
        return
    if art == "gegenprobe":
        aufgabe.gegenprobe = "\n".join(inhalt).strip() + "\n"
        return

    probe = Probe(zeile=zeile)
    for z in inhalt:
        if not z.strip():
            continue
        schluessel, _, wert = z.partition(":")
        schluessel, wert = schluessel.strip().lower(), wert.strip()
        if schluessel == "eingabe":
            probe.eingaben.append(wert)
        elif schluessel in REGELN:
            probe.regeln.append(Regel(schluessel, wert))
        else:
            raise ValueError(f"Zeile {zeile}: unbekannte Regel '{schluessel}'. "
                             f"Erlaubt sind: eingabe, {', '.join(REGELN)}.")
    aufgabe.proben.append(probe)
