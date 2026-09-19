"""Übersetzt ein Klarsatz-Programm in lesbares Python.

Gedacht als Brücke: Wer Klarsatz versteht, sieht hier, wie dieselbe Idee in einer
verbreiteten Sprache aussieht. Das Ziel ist **Lesbarkeit**, nicht buchstabengetreue
Gleichheit — an den wenigen Stellen, an denen Klarsatz anders rechnet als Python,
steht ein Hinweis im erzeugten Quelltext statt einer Hilfsbibliothek:

* `geteilt durch` liefert in Klarsatz eine ganze Zahl, wenn es aufgeht; Python liefert
  immer eine Kommazahl.
* Klarsatz zählt Listen ab 1, Python ab 0 — das rechnet die Übersetzung um.
* Kommazahlen zeigt Klarsatz mit Komma, Python mit Punkt.
* `Sortiere` ordnet in Klarsatz nach deutscher Reihenfolge (ä wie a).

Aufruf:  python3 -m klarsatz --nach-python programm.klar
"""
import keyword
import re

from .fehler import KlarsatzFehler
from .werte import passt
from .lexer import lexer
from .parser import Parser

EINZUG = "    "

# Klarsatz-Rechenwörter → Python-Operatoren
RECHNEN = {"plus": "+", "minus": "-", "mal": "*", "geteilt": "/", "hoch": "**"}
AENDERN = {"plus": "+=", "minus": "-=", "mal": "*=", "geteilt": "/="}
ZEIT = {"stunde": "hour", "minute": "minute", "sekunde": "second",
        "tag": "day", "monat": "month", "jahr": "year"}
TYPEN = {"zahl": "(int, float)", "text": "str", "liste": "list", "tabelle": "dict"}
# Deutsche Farbnamen → was turtle versteht
FARBEN_PY = {"#d94f4f": "red", "#5a8fd9": "blue", "#7fb069": "green", "#e8cd86": "yellow",
             "#d9b45a": "goldenrod", "#e8a87c": "orange", "#a87cd9": "purple",
             "#e07ca8": "pink", "#7cd9c8": "turquoise", "#a87c5a": "brown",
             "#9aa08f": "gray", "#1a1d18": "black", "#f3efe6": "white"}


class NichtUebersetzbar(KlarsatzFehler):
    """Für Sätze, die (noch) keine sinnvolle Entsprechung in Python haben."""


def _name(anzeige):
    """Macht aus einem Klarsatz-Namen einen gültigen Python-Bezeichner."""
    sauber = re.sub(r"\W", "_", anzeige, flags=re.UNICODE)
    if not sauber or sauber[0].isdigit():
        sauber = "x_" + sauber
    if keyword.iskeyword(sauber) or sauber in ("print", "input", "len", "list", "dict", "str"):
        sauber += "_"
    return sauber


class NachPython:
    def __init__(self):
        self.importe = set()
        self.hinweise = []
        self.strukturen = {}          # norm -> [Feldnamen] (für @dataclass)
        # Klarsatz unterscheidet Groß- und Kleinschreibung nicht ("ZAHL" = "zahl"),
        # Python schon. Darum bekommt jeder Name genau eine Schreibweise — die erste,
        # in der er auftaucht.
        self.namen = {}
        self.klassennamen = {}        # norm -> Anzeigename der Struktur
        self.zeichnet = False

    def _n(self, norm, anzeige):
        """Einheitlicher Python-Bezeichner für einen Klarsatz-Namen."""
        if norm not in self.namen:
            self.namen[norm] = _name(anzeige)
        return self.namen[norm]

    # ── Einstieg ────────────────────────────────────────────────────
    def uebersetze(self, quelltext):
        programm = Parser(lexer(quelltext)).programm()
        koerper = self._bloecke(programm)

        kopf = []
        if self.strukturen:
            self.importe.add("from dataclasses import dataclass")
        for zeile in sorted(self.importe):
            kopf.append(zeile)
        if kopf:
            kopf.append("")

        for norm, felder in self.strukturen.items():
            kopf.append("@dataclass")
            kopf.append(f"class {_name(self.klassennamen[norm])}:")
            for _norm, feld in felder:
                kopf.append(f"{EINZUG}{feld}: object")
            kopf.append("")

        if self.zeichnet:
            kopf += ["stift = turtle.Turtle()", "stift.speed(0)", "stift.pencolor('goldenrod')",
                     "stift.pensize(2)", ""]

        fuss = []
        if self.zeichnet:
            fuss = ["", "turtle.done()"]

        if self.hinweise:
            kopf = ["# Hinweise zur Übersetzung:"] + [f"#   {h}" for h in dict.fromkeys(self.hinweise)] + [""] + kopf

        return "\n".join(kopf + koerper + fuss).rstrip() + "\n"

    # ── Sätze ───────────────────────────────────────────────────────
    def _bloecke(self, saetze):
        """Zeilen eines Blocks — ohne führende Einrückung; die setzt der Aufrufer."""
        zeilen = []
        for satz in saetze:
            zeilen += self._satz(satz)
        return zeilen or ["pass"]

    def _tiefer(self, saetze):
        """Derselbe Block, eine Stufe eingerückt."""
        return [EINZUG + z if z else "" for z in self._bloecke(saetze)]

    def _satz(self, k):
        name = "s_" + k[0]
        if not hasattr(self, name):
            raise NichtUebersetzbar(f"Diesen Satz kann ich noch nicht nach Python übersetzen: '{k[0]}'.",
                                    k[1] if len(k) > 1 and isinstance(k[1], int) else None)
        return getattr(self, name)(k)

    def s_zeige(self, k):
        teile = [self._a(e) for e in k[2]]
        if len(teile) == 1:
            return [f"print({teile[0]})"]
        return ["print(" + ", ".join(teile) + ", sep='')"]

    def s_merke(self, k):
        if k[5]:
            self.hinweise.append("'Merke für immer' kennt Python nicht – dort ist eine Konstante nur eine "
                                 "Absprache unter Menschen.")
        return [f"{self._n(k[3], k[4])} = {self._a(k[2])}"]

    def s_setze(self, k):
        return [f"{self._ziel(k[2])} = {self._a(k[3])}"]

    def s_aendere(self, k):
        ziel, art, wert = self._ziel(k[2]), k[3], self._a(k[4])
        if art not in AENDERN:
            raise NichtUebersetzbar(f"Unbekannte Änderung: {art}", k[1])
        return [f"{ziel} {AENDERN[art]} {wert}"]

    def s_wenn(self, k):
        zeilen = []
        for i, (bed, koerper) in enumerate(k[2]):
            zeilen.append(("if " if i == 0 else "elif ") + self._a(bed) + ":")
            zeilen += self._tiefer(koerper)
        if k[3] is not None:
            zeilen.append("else:")
            zeilen += self._tiefer(k[3])
        return zeilen

    def s_wiederhole_n(self, k):
        return [f"for _ in range({self._a(k[2])}):"] + self._tiefer(k[3])

    def s_solange(self, k):
        return [f"while {self._a(k[2])}:"] + self._tiefer(k[3])

    def s_zaehle(self, k):
        _, z, von, bis, schritt, var, koerper, rueckwaerts = k
        name = self._n(var[0], var[1]) if var else "_"
        a, b = self._a(von), self._a(bis)
        if rueckwaerts:
            bereich = f"range({a}, {b} - 1, -{self._a(schritt) if schritt else 1})"
        else:
            bereich = f"range({a}, {b} + 1{', ' + self._a(schritt) if schritt else ''})"
        return [f"for {name} in {bereich}:"] + self._tiefer(koerper)

    def s_fuer(self, k):
        return [f"for {self._n(k[2], k[3])} in {self._a(k[4])}:"] + self._tiefer(k[5])

    def s_abbruch(self, k):
        return ["break"]

    def s_weiter(self, k):
        return ["continue"]

    def s_aufgabe(self, k):
        _, z, norm, anzeige, parameter, koerper = k
        namen = ", ".join(self._n(p[0], p[1]) for p in parameter)
        return [f"def {self._n(norm, anzeige)}({namen}):"] + self._tiefer(koerper) + [""]

    def s_gib(self, k):
        return [f"return {self._a(k[2])}"]

    def s_fuehre(self, k):
        return [self._a(k[2])]

    def s_frage(self, k):
        self.hinweise.append("'Frage' macht aus einer Eingabe, die wie eine Zahl aussieht, automatisch eine "
                             "Zahl – in Python steht hier immer ein Text.")
        return [f"{self._n(k[3], k[4])} = input({self._a(k[2])})"]

    def s_liste_neu(self, k):
        werte = ", ".join(self._a(e) for e in k[4])
        return [f"{self._n(k[2], k[3])} = [{werte}]"]

    def s_liste_add(self, k):
        return [f"{self._n(k[3], k[4])}.append({self._a(k[2])})"]

    def s_liste_weg(self, k):
        return [f"{self._n(k[3], k[4])}.remove({self._a(k[2])})"]

    def s_liste_weg_pos(self, k):
        art, ziel = k[2], self._n(k[3], k[4])
        if art == "erste":
            return [f"{ziel}.pop(0)"]
        if art == "letzte":
            return [f"{ziel}.pop()"]
        return [f"{ziel}.pop({self._a(art)} - 1)"]

    def s_sortiere(self, k):
        self.hinweise.append("'Sortiere' ordnet in Klarsatz nach deutscher Reihenfolge (ä wie a); "
                             "Python sortiert nach Zeichencode.")
        return [f"{self._n(k[2], k[3])}.sort({'reverse=True' if k[4] else ''})"]

    def s_kopiere(self, k):
        return [f"{self._n(k[3], k[4])} = list({self._a(k[2])})"]

    def s_tabelle_neu(self, k):
        paare = ", ".join(f"{self._a(sch)}: {self._a(w)}" for sch, w in k[4])
        return [f"{self._n(k[2], k[3])} = {{{paare}}}"]

    def s_trage(self, k):
        return [f"{self._n(k[4], k[5]) if len(k) > 5 else self._n(k[4], k[4])}[{self._a(k[2])}] = {self._a(k[3])}"]

    def s_verbinde(self, k):
        teile = " + ".join(f"str({self._a(e)})" for e in k[2])
        return [f"{self._n(k[3], k[4])} = {teile}"]

    def s_teile(self, k):
        return [f"{self._n(k[4], k[5])} = {self._a(k[2])}.split({self._a(k[3])})"]

    def s_ersetze(self, k):
        ziel = self._n(k[4], k[5]) if len(k) > 5 else self._n(k[3], k[4])
        return [f"{ziel} = {ziel}.replace({self._a(k[2])}, {self._a(k[3])})"]

    def s_struktur(self, k):
        # Feldnamen samt ihrer Klarsatz-Form merken — beim Erschaffen dürfen sie
        # gebeugt sein ("Name" statt "Namen"), in Python muss es derselbe sein.
        self.strukturen[k[2]] = [(f[0], self._n(f[0], f[1])) for f in k[4]]
        self.klassennamen[k[2]] = k[3]
        return []

    def s_erschaffe(self, k):
        werte = ", ".join(f"{self._feldname(k[2], fnorm, fanzeige)}={self._a(wert)}"
                          for fnorm, fanzeige, wert in k[4])
        return [f"{self._n(k[5], k[6])} = {_name(k[3])}({werte})"]

    def _feldname(self, struktur_norm, fnorm, fanzeige):
        """Das Feld der Struktur finden — auch wenn es hier gebeugt geschrieben steht."""
        for gespeichert, py_name in self.strukturen.get(struktur_norm, []):
            if passt(gespeichert, fnorm):
                return py_name
        return self._n(fnorm, fanzeige)

    def s_versuche(self, k):
        zeilen = ["try:"] + self._tiefer(k[2])
        zeilen += ["except Exception as fehler:"]
        zeilen += self._tiefer(k[3])
        self.hinweise.append("'Fehlermeldung' heißt in Python 'fehler' (die abgefangene Ausnahme).")
        return zeilen

    def s_sicher(self, k):
        return [f"assert {self._a(k[2])}"]

    def s_lies(self, k):
        return [f"{_name(k[4])} = open({self._a(k[2])}, encoding='utf-8').read()"]

    def s_schreibe(self, k):
        return [f"open({self._a(k[3])}, 'w', encoding='utf-8').write({self._a(k[2])})"]

    def s_warte(self, k):
        self.importe.add("import time")
        return [f"time.sleep({self._a(k[2])})"]

    # ── Zeichnen (wird zu turtle) ───────────────────────────────────
    def _turtle(self):
        self.importe.add("import turtle")
        self.zeichnet = True

    def s_gehe(self, k):
        self._turtle()
        weite = self._a(k[2])
        return [f"stift.{'backward' if k[3] else 'forward'}({weite})"]

    def s_drehe(self, k):
        self._turtle()
        return [f"stift.{'left' if k[3] else 'right'}({self._a(k[2])})"]

    def s_stift(self, k):
        self._turtle()
        return [f"stift.{'pendown' if k[2] else 'penup'}()"]

    def s_mitte(self, k):
        self._turtle()
        return ["stift.penup(); stift.home(); stift.pendown()"]

    def s_farbe(self, k):
        self._turtle()
        wert = k[2]
        if wert[0] == "wert" and isinstance(wert[1], str):
            from .interpreter import FARBEN
            from .lexer import norm as _norm
            farbe = FARBEN_PY.get(FARBEN.get(_norm(wert[1]), ""), "goldenrod")
            return [f"stift.pencolor('{farbe}')"]
        return [f"stift.pencolor({self._a(wert)})"]

    def s_strichstaerke(self, k):
        self._turtle()
        return [f"stift.pensize({self._a(k[2])})"]

    def s_loesche_zeichnung(self, k):
        self._turtle()
        return ["stift.clear()"]

    def s_wiederholung(self, k):
        self.hinweise.append("'Wiederhole dieses Programm …' hat keine Entsprechung – in Python schreibt man "
                             "dafür eine Schleife mit time.sleep.")
        return [f"# Klarsatz würde das ganze Programm alle {self._a(k[2])} Sekunden neu starten."]

    # ── Hilfen ──────────────────────────────────────────────────────
    def _ziel(self, ziel):
        if ziel[0] == "var":
            return self._n(ziel[1], ziel[2])
        if ziel[0] == "feld":
            return self.a_feld(ziel)
        if ziel[0] == "element":
            return f"{self._a(ziel[2])}[{self._a(ziel[1])} - 1]"
        if ziel[0] == "tabellenwert":
            return f"{self._a(ziel[2])}[{self._a(ziel[1])}]"
        return self._a(ziel)

    # ── Ausdrücke ───────────────────────────────────────────────────
    def _a(self, k):
        name = "a_" + k[0]
        if not hasattr(self, name):
            raise NichtUebersetzbar(f"Diesen Ausdruck kann ich noch nicht nach Python übersetzen: '{k[0]}'.")
        return getattr(self, name)(k)

    def a_wert(self, k):
        return repr(k[1])

    def a_var(self, k):
        return self._n(k[1], k[2])

    def a_bin(self, k):
        op = RECHNEN[k[1]]
        if k[1] == "geteilt":
            self.hinweise.append("'geteilt durch' liefert in Klarsatz eine ganze Zahl, wenn es aufgeht – "
                                 "Python liefert immer eine Kommazahl.")
        return f"({self._a(k[2])} {op} {self._a(k[3])})"

    def a_vgl(self, k):
        links, rechts = self._a(k[2]), self._a(k[3])
        if k[1] == "teilbar":
            return f"({links} % {rechts} == 0)"
        if k[1] == "enthaelt":
            return f"({rechts} in {links})"
        return f"({links} {k[1]} {rechts})"

    def a_und(self, k):
        return f"({self._a(k[1])} and {self._a(k[2])})"

    def a_oder(self, k):
        return f"({self._a(k[1])} or {self._a(k[2])})"

    def a_nicht(self, k):
        return f"(not {self._a(k[1])})"

    def a_wahrheit(self, k):
        return self._a(k[1])

    def a_aufruf(self, k):
        return f"{self._n(k[1], k[2])}({', '.join(self._a(a) for a in k[3])})"

    def a_feld(self, k):
        for felder in self.strukturen.values():
            for gespeichert, py_name in felder:
                if passt(gespeichert, k[1]):
                    return f"{self._a(k[3])}.{py_name}"
        return f"{self._a(k[3])}.{self._n(k[1], k[2])}"

    def a_laenge(self, k):
        return f"len({self._a(k[1])})"

    def a_element(self, k):
        return f"{self._a(k[2])}[{self._a(k[1])} - 1]"

    def a_pos(self, k):
        return f"{self._a(k[2])}[{'0' if k[1] == 'erste' else '-1'}]"

    def a_ausschnitt(self, k):
        return f"{self._a(k[3])}[{self._a(k[1])} - 1:{self._a(k[2])}]"

    def a_tabellenwert(self, k):
        return f"{self._a(k[2])}[{self._a(k[1])}]"

    def a_rest(self, k):
        return f"({self._a(k[1])} % {self._a(k[2])})"

    def a_wurzel(self, k):
        self.importe.add("import math")
        return f"math.sqrt({self._a(k[1])})"

    def a_rechtsbuendig(self, k):
        return f"str({self._a(k[1])}).rjust({self._a(k[2])})"

    def a_linksbuendig(self, k):
        return f"str({self._a(k[1])}).ljust({self._a(k[2])})"

    def a_sinus(self, k):
        self.importe.add("import math")
        return f"math.sin(math.radians({self._a(k[1])}))"

    def a_kosinus(self, k):
        self.importe.add("import math")
        return f"math.cos(math.radians({self._a(k[1])}))"

    a_cosinus = a_kosinus

    def a_tangens(self, k):
        self.importe.add("import math")
        return f"math.tan(math.radians({self._a(k[1])}))"

    def a_arkussinus(self, k):
        self.importe.add("import math")
        return f"math.degrees(math.asin({self._a(k[1])}))"

    def a_arkuskosinus(self, k):
        self.importe.add("import math")
        return f"math.degrees(math.acos({self._a(k[1])}))"

    a_arkuscosinus = a_arkuskosinus

    def a_arkustangens(self, k):
        self.importe.add("import math")
        return f"math.degrees(math.atan({self._a(k[1])}))"

    def a_betrag(self, k):
        return f"abs({self._a(k[1])})"

    def a_zufall(self, k):
        self.importe.add("import random")
        return f"random.randint({self._a(k[1])}, {self._a(k[2])})"

    def a_zufallselement(self, k):
        self.importe.add("import random")
        return f"random.choice({self._a(k[1])})"

    def a_jetzt(self, k):
        self.importe.add("from datetime import datetime")
        return f"datetime.now().{ZEIT[k[1]]}"

    def a_typ(self, k):
        return f"isinstance({self._a(k[1])}, {TYPEN.get(k[2], 'object')})"

    def a_kleinbuchstaben(self, k):
        return f"{self._a(k[1])}.lower()"

    def a_grossbuchstaben(self, k):
        return f"{self._a(k[1])}.upper()"

    def a_verkettet(self, k):
        return f"{self._a(k[2])}.join(str(x) for x in {self._a(k[1])})"

    def a_zahlenwert(self, k):
        return f"float(str({self._a(k[1])}).replace(',', '.'))"

    def a_formatiert(self, k):
        self.hinweise.append("Kommazahlen zeigt Klarsatz mit Komma, Python mit Punkt.")
        return f"f'{{{self._a(k[1])}:.{{{self._a(k[2])}}}f}}'.replace('.', ',')"

    def a_abgerundet(self, k):
        self.importe.add("import math")
        return f"math.floor({self._a(k[1])})"

    def a_aufgerundet(self, k):
        self.importe.add("import math")
        return f"math.ceil({self._a(k[1])})"

    def a_gerundet(self, k):
        stellen = f", {self._a(k[3])}" if len(k) > 3 and k[3] is not None else ""
        return f"round({self._a(k[1])}{stellen})"

    def a_enthaelt(self, k):
        return f"({self._a(k[2])} in {self._a(k[1])})"


def nach_python(quelltext):
    """Übersetzt Klarsatz-Quelltext in Python-Quelltext."""
    return NachPython().uebersetze(quelltext)
