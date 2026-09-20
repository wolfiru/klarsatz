"""Schnittstelle für Webseiten (z. B. mit Pyodide im Browser).

Im Browser darf ein Programm nicht mitten in der Ausführung auf 'input()' warten. Darum arbeitet diese
Schnittstelle nach dem Abspiel-Prinzip: Das Programm läuft, bis es eine Antwort braucht, und hält dann an
(Zustand „wartet“). Kommt die Antwort, wird das Programm mit allen bisherigen Antworten und demselben
Zufalls-Startwert noch einmal von vorn abgespielt – dabei entsteht exakt derselbe Verlauf und ein Stück mehr.
Dateien liegen nur im Arbeitsspeicher (ein Dict), Zeit und Speicher sind streng begrenzt.

Einfachste Nutzung:
    s = Sitzung(quelltext)
    e = s.start()
    while e.zustand == "wartet":
        e = s.antworte(input(e.frage))        # in der Webseite: Eingabefeld statt input()
Für JavaScript gibt es die *_json-Funktionen, die nur Texte und Zahlen austauschen.
"""
import json
import random
from dataclasses import dataclass, field

from .dateisystem import SpeicherDateisystem
from .fehler import KlarsatzFehler, LimitFehler, StufenFehler, SyntaxFehler, formatiere_fehler
from .formatierer import formatiere as _formatiere
from .grenzen import Grenzen
from .interpreter import Interpreter
from .pruefer import pruefe as _pruefe


class _BrauchtEingabe(Exception):
    def __init__(self, frage):
        super().__init__(frage)
        self.frage = frage


@dataclass
class Ergebnis:
    zustand: str                                   # "fertig" | "wartet" | "fehler"
    verlauf: list = field(default_factory=list)    # [("aus", Text) | ("frage", Text) | ("antwort", Text)
                                                  #  | ("linie", x1, y1, x2, y2, Farbe, Breite)]
    frage: str | None = None                       # bei "wartet": die aktuelle Frage
    fehler: str | None = None                      # bei "fehler": die fertig formatierte Meldung
    fehlerart: str | None = None                   # "syntax" | "laufzeit" | "limit"
    fehler_zeile: int | None = None
    fehler_spalte: int | None = None
    dateien: dict = field(default_factory=dict)    # Inhalt des Arbeitsspeicher-Dateisystems
    wiederholung: float | None = None              # Sekunden: Programm möchte im Takt neu laufen

    @property
    def ausgabe(self):
        """Nur die Ausgabezeilen (ohne Fragen und Antworten)."""
        # Eintragsweise auspacken: Striche haben sieben Teile, ("loeschen",) nur einen.
        return [eintrag[1] for eintrag in self.verlauf if eintrag[0] == "aus"]

    def als_dict(self):
        return {"zustand": self.zustand, "verlauf": [list(v) for v in self.verlauf], "frage": self.frage,
                "fehler": self.fehler, "fehlerart": self.fehlerart, "fehler_zeile": self.fehler_zeile,
                "fehler_spalte": self.fehler_spalte, "dateien": self.dateien,
                "wiederholung": self.wiederholung}


def laufe(quelltext, antworten=(), seed=0, grenzen=None, dateien=None, melde=None, stufe=None):
    """Führt das Programm mit den bisherigen `antworten` aus und hält an, wenn eine weitere gebraucht wird.

    `melde` bekommt jeden Verlaufseintrag sofort, sobald er entsteht — dadurch kann eine Oberfläche
    schon während des Laufs zeigen, was passiert. Ohne `melde` verhält sich alles wie bisher: Das
    Ergebnis kommt am Ende, vollständig."""
    verlauf, vorrat = [], iter(antworten)
    fs = SpeicherDateisystem(dateien)

    # Ein Programm mit "Warte" kann stundenlang laufen. Wer mitliest (melde), hat jeden
    # Eintrag schon bekommen — dann genügt hier ein Fenster der jüngsten Einträge, damit
    # der Speicher nicht mitwächst.
    OBERGRENZE = 5000

    def sammle(eintrag):
        if melde is not None:
            melde(eintrag)
            if len(verlauf) >= OBERGRENZE:
                del verlauf[:OBERGRENZE // 2]
        verlauf.append(eintrag)

    def eingabe(frage=""):
        sammle(("frage", frage))
        try:
            antwort = next(vorrat)
        except StopIteration:
            raise _BrauchtEingabe(frage)
        sammle(("antwort", str(antwort)))
        return str(antwort)

    interp = Interpreter(ausgabe=lambda z: sammle(("aus", z)),
                         zeichne=sammle,              # ("linie", …) und ("loeschen",)
                         eingabe=eingabe,
                         grenzen=grenzen or Grenzen.streng(), dateisystem=fs, zufall=random.Random(seed),
                         stufe=stufe)
    try:
        interp.lauf(quelltext)
    except _BrauchtEingabe as e:
        return Ergebnis("wartet", verlauf, frage=e.frage, dateien=dict(fs.dateien))
    except KlarsatzFehler as e:
        art = ("stufe" if isinstance(e, StufenFehler) else
               "syntax" if isinstance(e, SyntaxFehler) else
               "limit" if isinstance(e, LimitFehler) else "laufzeit")
        return Ergebnis("fehler", verlauf, fehler=formatiere_fehler(e, quelltext), fehlerart=art,
                        fehler_zeile=e.zeile, fehler_spalte=e.spalte, dateien=dict(fs.dateien))
    return Ergebnis("fertig", verlauf, dateien=dict(fs.dateien), wiederholung=interp.wiederholung)


class Sitzung:
    """Ein laufendes Programm mit seinen bisherigen Antworten."""

    def __init__(self, quelltext, seed=None, grenzen=None, dateien=None):
        self.quelltext = quelltext
        self.seed = random.randrange(2 ** 31) if seed is None else seed
        self.grenzen = grenzen
        self.dateien = dict(dateien or {})
        self.antworten = []
        self.ergebnis = None

    def _lauf(self):
        self.ergebnis = laufe(self.quelltext, self.antworten, self.seed, self.grenzen, self.dateien)
        return self.ergebnis

    def start(self):
        self.antworten = []
        return self._lauf()

    def antworte(self, text):
        if self.ergebnis is None or self.ergebnis.zustand != "wartet":
            raise ValueError("Das Programm wartet gerade auf keine Antwort.")
        self.antworten.append(str(text))
        return self._lauf()


# ── Für JavaScript: nur Texte hin und her ───────────────────────────────
def laufe_json(quelltext, antworten_json="[]", seed=0, melde=None, stufe=None):
    """Wie `laufe`, aber mit Texten statt Objekten — für JavaScript.

    `melde` wird, wenn angegeben, mit jedem Verlaufseintrag als JSON-Text aufgerufen."""
    weiter = (lambda eintrag: melde(json.dumps(list(eintrag), ensure_ascii=False))) if melde is not None else None
    ergebnis = laufe(quelltext, json.loads(antworten_json), int(seed), melde=weiter,
                     stufe=int(stufe) if stufe else None)
    return json.dumps(ergebnis.als_dict(), ensure_ascii=False)


def pruefe_aufgabe_json(quelltext, aufgabe_json, seed=0):
    """Prüft eine Lösung gegen die Regeln einer Übungsaufgabe — für die Aufgabenseite.

    `aufgabe_json` enthält nur, was zum Prüfen nötig ist:
    {"proben": [{"eingaben": ["4", "3"], "regeln": [["enthält", "12"], …]}]}
    Zurück kommt, welche Regel erfüllt ist und welche nicht — nie die Lösung."""
    from .aufgaben import Aufgabe, Probe, Regel, pruefe as _pruefe

    daten = json.loads(aufgabe_json)
    aufgabe = Aufgabe(nummer=str(daten.get("nummer", "")), titel=daten.get("titel", ""),
                      stufe=int(daten.get("stufe", 0)), lektion="", angabe="")
    for p in daten.get("proben", []):
        aufgabe.proben.append(Probe(eingaben=[str(e) for e in p.get("eingaben", [])],
                                    regeln=[Regel(art, str(wert)) for art, wert in p.get("regeln", [])]))

    befund = _pruefe(aufgabe, quelltext,
                     lambda q, a: laufe(q, antworten=a, seed=int(seed)))
    return json.dumps({
        "bestanden": befund.bestanden,
        "offen": befund.offen,
        "proben": [{"bestanden": b,
                    "regeln": [{"erfuellt": e, "text": txt} for e, txt in regeln],
                    "fehler": fehler}
                   for b, regeln, fehler in befund.proben],
    }, ensure_ascii=False)


def pruefe_json(quelltext):
    return json.dumps([{"schwere": b.schwere, "zeile": b.zeile, "spalte": b.spalte, "laenge": b.laenge,
                        "meldung": b.meldung, "code": b.code} for b in _pruefe(quelltext)], ensure_ascii=False)


def nach_python_json(quelltext):
    """Übersetzt nach Python — für den Knopf in der Spielwiese."""
    from .nach_python import nach_python
    try:
        return json.dumps({"ok": True, "text": nach_python(quelltext)}, ensure_ascii=False)
    except KlarsatzFehler as e:
        return json.dumps({"ok": False, "fehler": formatiere_fehler(e, quelltext),
                           "zeile": e.zeile}, ensure_ascii=False)


def formatiere_json(quelltext):
    try:
        return json.dumps({"ok": True, "text": _formatiere(quelltext)}, ensure_ascii=False)
    except SyntaxFehler as e:
        return json.dumps({"ok": False, "fehler": formatiere_fehler(e, quelltext), "zeile": e.zeile}, ensure_ascii=False)
