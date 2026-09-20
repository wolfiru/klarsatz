"""Interpreter: führt den Syntaxbaum aus."""
import difflib
import math
import os
import random
import re
import sys
import time
from dataclasses import replace

from .dateisystem import KeinDateisystem, OrdnerDateisystem
from .fehler import (KlarsatzFehler, LaufzeitFehler, LimitFehler, SyntaxFehler, _Abbruch, _Rueckgabe, _Weiter)
from .grenzen import Grenzen
from .lexer import lexer, norm
from .parser import Parser
from .stufen import pruefe as pruefe_stufe
from .werte import *  # noqa
from .werte import _ist_zahl, _gleich, _sortierschluessel, _auto_zahl


# Winkelfunktionen rechnen in **Grad** — passend zu "Drehe dich um 90 Grad".
WINKEL = {"sinus": math.sin, "kosinus": math.cos, "cosinus": math.cos, "tangens": math.tan}
ARKUS = {"arkussinus": math.asin, "arkuskosinus": math.acos,
         "arkuscosinus": math.acos, "arkustangens": math.atan}

# Farben zum Zeichnen. Bewusst eine feste Liste deutscher Namen: So gibt es für Tippfehler
# eine hilfreiche Meldung, und in die Zeichnung gerät nichts Unerwartetes.
FARBEN = {
    "rot": "#d94f4f", "blau": "#5a8fd9", "gruen": "#7fb069", "gelb": "#e8cd86",
    "gold": "#d9b45a", "orange": "#e8a87c", "lila": "#a87cd9", "rosa": "#e07ca8",
    "tuerkis": "#7cd9c8", "braun": "#a87c5a", "grau": "#9aa08f",
    "schwarz": "#1a1d18", "weiss": "#f3efe6",
}


# ════════════════════════════════════════════════════════════════════
#  Interpreter
# ════════════════════════════════════════════════════════════════════
def _ohne_rauschen(wert):
    """Rundet das Rechenrauschen weg: Der Sinus von 30 Grad soll 0,5 sein —
    nicht 0,49999999999999994. Ganze Ergebnisse werden auch als ganze Zahl gezeigt."""
    gerundet = round(wert, 12)
    return int(gerundet) if gerundet == int(gerundet) else gerundet


class Interpreter:
    def __init__(self, ausgabe=None, eingabe=None, dateien=True, max_schritte=None, zufall=None,
                 grenzen=None, dateisystem=None, zeichne=None, uhr=None, stufe=None):
        """dateien=False sperrt jeden Dateizugriff; ohne weitere Angabe sind Dateien im aktuellen Ordner
        (und darunter) erlaubt. Ein eigenes `dateisystem` hat Vorrang. `grenzen` begrenzt Zeit und Speicher.

        `zeichne` bekommt jeden Strich als ("linie", x1, y1, x2, y2, farbe, breite). Ohne Angabe sammelt
        der Interpreter die Striche in `self.zeichnung` — er malt selbst nichts, das überlässt er der
        Oberfläche (Browser: Leinwand, Kommandozeile: SVG-Datei)."""
        self.stufe = stufe                       # Lernstufe (None = ganze Sprache)
        self.zufall = zufall or random.Random()
        self.aus = ausgabe or print
        self.eingabe = eingabe or input
        self.grenzen = grenzen or Grenzen()
        if max_schritte is not None:
            self.grenzen = replace(self.grenzen, schritte=max_schritte)
        if dateisystem is not None:
            self.fs = dateisystem
        elif not dateien:
            self.fs = KeinDateisystem()
        else:
            self.fs = OrdnerDateisystem(os.getcwd())
        self.schritte = 0
        self.ausgabe_zeichen = 0
        self.start = time.monotonic()
        self.tiefe = 0
        self.zeichnung = []
        self.leinwand = None                  # feste Zeichenfläche, siehe _a_leinwand
        self._eigener_kanal = zeichne is not None
        self.zeichne = zeichne or self.zeichnung.append
        self.uhr = uhr or time.localtime
        self._jetzt = None
        self.wiederholung = None   # Sekunden; gesetzt durch "Wiederhole dieses Programm …"
        self._stift_zuruecksetzen()
        self.global_bereich = Bereich()
        self.aufgaben = {}       # norm -> (anzeige, [(norm, anz)], body)
        self.strukturen = {}     # norm -> (anzeige, [(norm, anz)])
        self.stelligkeit = {}    # norm -> Anzahl Parameter (auch für spätere Programmteile, z. B. in der Konsole)
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))

    # ── Einstieg ────────────────────────────────────────────────────
    def parse(self, quelltext: str):
        """Quelltext -> Syntaxbaum (Aufgaben aus früheren Programmteilen sind bekannt)."""
        if len(quelltext) > self.grenzen.quelltext:
            raise LimitFehler(f"Das Programm ist zu lang (mehr als {self.grenzen.quelltext} Zeichen).")
        tokens = lexer(quelltext)
        pruefe_stufe(tokens, self.stufe)
        parser = Parser(tokens, vorwissen=self.stelligkeit, max_tiefe=self.grenzen.verschachtelung)
        programm = parser.programm()
        self.stelligkeit.update(parser.aufgaben)
        return programm

    def lauf(self, quelltext: str):
        self.fuehre_aus(self.parse(quelltext))

    def zuruecksetzen(self):
        """Alle Variablen, Aufgaben und Dinge vergessen (für die Konsole)."""
        self.global_bereich = Bereich()
        self.aufgaben, self.strukturen, self.stelligkeit = {}, {}, {}

    def _neuer_lauf(self):
        self.schritte = 0
        self.ausgabe_zeichen = 0
        self.start = time.monotonic()
        self._jetzt = None
        self.wiederholung = None
        self._stift_zuruecksetzen()

    def _zeitpunkt(self):
        """Die Zeit wird je Lauf einmal abgelesen — sonst könnte zwischen 'aktuelle Minute'
        und 'aktuelle Sekunde' ein Sprung liegen und eine Uhr falsch gehen."""
        if self._jetzt is None:
            self._jetzt = self.uhr()
        return self._jetzt

    def _w_jetzt(self, k, b):
        jetzt = self._zeitpunkt()
        return {"stunde": jetzt.tm_hour, "minute": jetzt.tm_min, "sekunde": jetzt.tm_sec,
                "tag": jetzt.tm_mday, "monat": jetzt.tm_mon, "jahr": jetzt.tm_year}[k[1]]

    def _stift_zuruecksetzen(self):
        """Der Stift steht in der Mitte, zeigt nach oben und malt in Gold."""
        self.stift = {"x": 0.0, "y": 0.0, "winkel": 90.0, "unten": True,
                      "farbe": FARBEN["gold"], "breite": 2}
        self.striche = 0

    def werte_aus(self, quelltext: str):
        """Einen einzelnen Ausdruck oder eine Bedingung auswerten und das Ergebnis zurückgeben."""
        parser = Parser(lexer(quelltext), vorwissen=self.stelligkeit, max_tiefe=self.grenzen.verschachtelung)
        try:
            knoten = parser.bedingung()
            if parser.ist_sym("."):
                parser.nimm()
            if parser.peek().art != "EOF":
                parser.fehler(f"Nach dem Ausdruck kommt noch etwas: {parser.beschreibe(parser.peek())}.")
        except RecursionError:
            raise SyntaxFehler("Das ist zu tief verschachtelt.")
        self._neuer_lauf()
        try:
            if knoten[0] == "wahrheit":
                return self.auswerten(knoten[1], self.global_bereich)
            return self.bed(knoten, self.global_bereich)
        except RecursionError:
            raise LaufzeitFehler("Der Ausdruck ist zu tief verschachtelt.")

    def fuehre_aus(self, programm):
        self._neuer_lauf()
        for node in programm:                          # Aufgaben auf oberster Ebene vorab bekannt machen
            if node[0] == "aufgabe":
                self._a_aufgabe(node, self.global_bereich)
        try:
            self.ausfuehren(programm, self.global_bereich)
        except _Rueckgabe:
            raise LaufzeitFehler("'Gib ... zurück' gibt es nur innerhalb einer Aufgabe.")
        except (_Abbruch, _Weiter):
            raise LaufzeitFehler("'Höre auf' / 'Mach weiter' gibt es nur innerhalb einer Schleife.")
        except RecursionError:
            raise LaufzeitFehler("Das Programm oder ein Wert ist zu tief verschachtelt.")

    def _tick(self, zeile):
        self.schritte += 1
        g = self.grenzen
        if g.schritte and self.schritte > g.schritte:
            raise LimitFehler("Schrittlimit erreicht – läuft das Programm in einer Endlosschleife?", zeile)
        if g.sekunden and not self.schritte & 255 and time.monotonic() - self.start > g.sekunden:
            raise LimitFehler(f"Zeitlimit erreicht ({g.sekunden:g} Sekunden) – läuft das Programm in "
                              "einer Endlosschleife?", zeile)

    def ausfuehren(self, stmts, bereich):
        for node in stmts:
            self._tick(node[1])
            try:
                getattr(self, "_a_" + node[0])(node, bereich)
            except KlarsatzFehler as e:
                if e.zeile is None:
                    e.zeile = node[1]
                raise
            except MemoryError:
                raise LaufzeitFehler("Dafür reicht der Speicher nicht.", node[1])
            except OverflowError:
                raise LaufzeitFehler("Die Zahl ist zu groß für diese Rechnung.", node[1])
            except ValueError as e:
                if "digits" in str(e):
                    raise LaufzeitFehler("Die Zahl hat zu viele Stellen, um sie anzuzeigen (mehr als 4300).",
                                         node[1])
                raise LaufzeitFehler("Das kann ich nicht berechnen.", node[1])
            except RecursionError:
                raise LaufzeitFehler("Die Werte sind zu tief verschachtelt (oder enthalten sich gegenseitig).",
                                     node[1])

    def _koerper(self, body, bereich):
        """Schleifenkörper ausführen. True = Schleife abbrechen."""
        try:
            self.ausfuehren(body, bereich)
        except _Weiter:
            pass
        except _Abbruch:
            return True
        return False

    # ── Anweisungen ─────────────────────────────────────────────────
    def _a_zeige(self, k, b):
        text = "".join(als_text(self.auswerten(x, b)) for x in k[2])
        self.ausgabe_zeichen += len(text) + 1
        if self.ausgabe_zeichen > self.grenzen.ausgabe:
            raise LimitFehler(f"Zu viel Ausgabe (mehr als {self.grenzen.ausgabe} Zeichen).", k[1])
        self.aus(text)

    def _a_frage(self, k, b):
        _, z, frage, n, anz = k[:5]
        typ = k[5] if len(k) > 5 else None
        try:
            antwort = self.eingabe(als_text(self.auswerten(frage, b)) + " ")
        except EOFError:
            raise LaufzeitFehler("Es kam keine Eingabe.", z)
        roh = antwort.strip()[:self.grenzen.eingabe]

        if typ == "text":
            wert = roh                       # ausdrücklich Text: "5" bleibt "5"
        elif typ == "zahl":
            wert = _auto_zahl(roh)
            if not _ist_zahl(wert):
                raise LaufzeitFehler(
                    f"Hier war eine Zahl gefragt, '{roh}' ist aber keine. "
                    "Wenn du so lange fragen willst, bis eine Zahl kommt, lass 'als Zahl' weg "
                    f"und prüfe mit 'Wenn {anz} eine Zahl ist'.", z)
        else:
            wert = _auto_zahl(roh)           # wie bisher: sieht es aus wie eine Zahl, ist es eine
        b.lege_an(n, anz, wert)

    def _a_merke(self, k, b):
        _, z, ausdruck, n, anz, konstant = k
        b.lege_an(n, anz, self.auswerten(ausdruck, b), konstant)

    def _schreibe_ziel(self, ziel, wert, b):
        if ziel[0] == "var":
            _, n, anz, z = ziel
            bb = b.finde(n)
            if bb is None:
                raise LaufzeitFehler(f"Ich kenne '{anz}' noch nicht. Lege es zuerst mit "
                                     f"'Merke ... als {anz}.' an.", z)
            bb.lege_an(n, anz, wert)
        elif ziel[0] in ("element", "pos", "tabellenwert"):
            self._stelle_setzen(ziel, wert, b)
        else:
            _, fn, fa, objk, z = ziel
            obj = self.auswerten(objk, b)
            self._feld_setzen(obj, fn, fa, wert, z)

    def _stelle_setzen(self, ziel, wert, b):
        """Schreibt an eine Stelle in einer Liste oder Tabelle.

        Gelesen wird so eine Stelle schon lange (`Zeige Element 2 von Liste.`); hier ist
        der Gegenweg. Geprüft wird dasselbe wie beim Lesen — wer daneben greift, bekommt
        dieselbe Meldung, statt dass still etwas Falsches passiert."""
        art, z = ziel[0], ziel[-1]

        if art == "tabellenwert":
            schluessel = self._schluessel(self.auswerten(ziel[1], b), z)
            tabelle = self._tabelle(self.auswerten(ziel[2], b), z)
            if len(tabelle) >= self.grenzen.liste and schluessel not in tabelle:
                raise LimitFehler(f"Die Tabelle hat mehr als {self.grenzen.liste} Einträge.", z)
            tabelle[schluessel] = wert
            return

        liste = self.auswerten(ziel[2], b)
        if isinstance(liste, str):
            raise LaufzeitFehler("Ein Text lässt sich nicht an einer Stelle ändern. "
                                 "Mit 'Ersetze \"alt\" durch \"neu\" in Text.' geht es.", z)
        if not isinstance(liste, list):
            raise LaufzeitFehler(f"Elemente hat nur eine Liste, hier ist es {typname(liste)}.", z)

        if art == "pos":
            if not liste:
                raise LaufzeitFehler(f"Die Liste ist leer – ein {ziel[1]}s Element gibt es nicht.", z)
            liste[0 if ziel[1] == "erste" else -1] = wert
            return

        nummer = self.auswerten(ziel[1], b)
        if not isinstance(nummer, int) or isinstance(nummer, bool):
            raise LaufzeitFehler(f"Die Nummer eines Elements muss eine ganze Zahl sein "
                                 f"(hier: {als_text(nummer)}).", z)
        if not 1 <= nummer <= len(liste):
            raise LaufzeitFehler(f"Element {nummer} gibt es nicht – gezählt wird ab 1, und es sind nur "
                                 f"{len(liste)} Elemente.", z)
        liste[nummer - 1] = wert

    def _a_setze(self, k, b):
        self._schreibe_ziel(k[2], self.auswerten(k[3], b), b)

    def _a_aendere(self, k, b):
        _, z, ziel, op, wert = k
        alt = self.auswerten(ziel, b)
        self._schreibe_ziel(ziel, self._rechne(op, alt, self.auswerten(wert, b), z), b)

    def _a_wenn(self, k, b):
        _, z, zweige, sonst = k
        for bed, body in zweige:
            if self.bed(bed, b):
                self.ausfuehren(body, b)
                return
        if sonst is not None:
            self.ausfuehren(sonst, b)

    def _a_solange(self, k, b):
        _, z, bed, body = k
        while self.bed(bed, b):
            self._tick(z)
            if self._koerper(body, b):
                break

    def _a_wiederhole_n(self, k, b):
        _, z, n, body = k
        anzahl = self.auswerten(n, b)
        if not isinstance(anzahl, int) or isinstance(anzahl, bool) or anzahl < 0:
            raise LaufzeitFehler(f"Wie oft wiederholt werden soll, muss eine ganze Zahl ab 0 sein "
                                 f"(hier: {als_text(anzahl)}).", z)
        for _ in range(anzahl):
            self._tick(z)
            if self._koerper(body, b):
                break

    def _a_zaehle(self, k, b):
        _, z, ka, kb, ks, var, body, rueck = k
        a, e = self.auswerten(ka, b), self.auswerten(kb, b)
        s = self.auswerten(ks, b) if ks is not None else (-1 if rueck else 1)
        if not (_ist_zahl(a) and _ist_zahl(e) and _ist_zahl(s)):
            raise LaufzeitFehler("'Zähle von ... bis ...' braucht Zahlen.", z)
        if s == 0:
            raise LaufzeitFehler("Die Schrittweite darf nicht 0 sein.", z)
        i = a
        while (i <= e) if s > 0 else (i >= e):
            self._tick(z)
            if var:
                b.lege_an(var[0], var[1], i)
            if self._koerper(body, b):
                break
            i += s

    def _a_fuer(self, k, b):
        _, z, n, anz, kliste, body = k
        quelle = self.auswerten(kliste, b)
        if not isinstance(quelle, (list, str, dict)):
            raise LaufzeitFehler(f"Durchgehen kann ich Listen, Tabellen (die Schlüssel) und Texte, hier ist es "
                                 f"{typname(quelle)}.", z)
        for element in list(quelle):
            self._tick(z)
            b.lege_an(n, anz, element)
            if self._koerper(body, b):
                break

    def _a_abbruch(self, k, b):
        raise _Abbruch()

    def _a_weiter(self, k, b):
        raise _Weiter()

    # Listen
    def _liste(self, n, anz, b, z):
        bb = b.finde(n)
        if bb is None:
            raise LaufzeitFehler(f"Ich kenne '{anz}' nicht. Erstelle sie mit 'Erstelle Liste namens {anz}.'", z)
        w = bb.werte[n]
        if isinstance(w, dict):
            raise LaufzeitFehler(f"'{anz}' ist eine Tabelle, keine Liste. Einträge setzt man mit "
                                 f"'Trage … mit … in {anz} ein.'", z)
        if not isinstance(w, list):
            raise LaufzeitFehler(f"'{anz}' ist keine Liste, sondern {typname(w)}.", z)
        return w

    def _behaelter(self, n, anz, b, z):
        """Liste oder Tabelle unter diesem Namen."""
        bb = b.finde(n)
        if bb is None:
            raise LaufzeitFehler(f"Ich kenne '{anz}' nicht.", z)
        w = bb.werte[n]
        if not isinstance(w, (list, dict)):
            raise LaufzeitFehler(f"'{anz}' ist weder Liste noch Tabelle, sondern {typname(w)}.", z)
        return w

    def _tabelle(self, w, z):
        if not isinstance(w, dict):
            raise LaufzeitFehler(f"Hier brauche ich eine Tabelle, aber es ist {typname(w)}.", z)
        return w

    @staticmethod
    def _schluessel(w, z):
        if isinstance(w, bool) or not isinstance(w, (str, int, float)):
            raise LaufzeitFehler(f"Als Schlüssel in einer Tabelle gehen nur Texte und Zahlen, hier ist es {typname(w)}.", z)
        return w

    def _pruefe_liste(self, laenge, z):
        if laenge > self.grenzen.liste:
            raise LaufzeitFehler(f"Die Liste würde zu groß (mehr als {self.grenzen.liste} Einträge).", z)

    def _pruefe_text(self, text, z):
        if len(text) > self.grenzen.text:
            raise LaufzeitFehler(f"Der Text würde zu lang (mehr als {self.grenzen.text} Zeichen).", z)
        return text

    def _a_liste_neu(self, k, b):
        _, z, n, anz, werte = k
        b.lege_an(n, anz, [self.auswerten(w, b) for w in werte])

    def _a_liste_add(self, k, b):
        _, z, wert, n, anz = k
        liste, w = self._liste(n, anz, b, z), self.auswerten(wert, b)
        if w is liste:
            raise LaufzeitFehler("Eine Liste kann sich nicht selbst enthalten.", z)
        self._pruefe_liste(len(liste) + 1, z)
        liste.append(w)

    def _a_liste_weg(self, k, b):
        _, z, wert, n, anz = k
        beh, w = self._behaelter(n, anz, b, z), self.auswerten(wert, b)
        if isinstance(beh, dict):
            schluessel = self._schluessel(w, z)
            if schluessel not in beh:
                raise LaufzeitFehler(f"In {anz} gibt es keinen Eintrag für {als_text(w)}.", z)
            del beh[schluessel]
            return
        for i, x in enumerate(beh):                    # ersten gleichen Wert entfernen (ohne 1 mit wahr zu verwechseln)
            if _gleich(x, w):
                del beh[i]
                return
        raise LaufzeitFehler(f"{als_text(w)} steht nicht in {anz}.", z)

    def _a_liste_weg_pos(self, k, b):
        _, z, pos, n, anz = k
        liste = self._liste(n, anz, b, z)
        if pos in ("erste", "letzte"):
            if not liste:
                raise LaufzeitFehler(f"{anz} ist leer, da gibt es kein {pos}s Element zu entfernen.", z)
            del liste[0 if pos == "erste" else -1]
            return
        idx = self.auswerten(pos, b)
        if isinstance(idx, bool) or not isinstance(idx, int):
            raise LaufzeitFehler(f"Die Nummer eines Elements muss eine ganze Zahl sein (hier: {als_text(idx)}).", z)
        if not 1 <= idx <= len(liste):
            raise LaufzeitFehler(f"Element {idx} gibt es nicht – gezählt wird ab 1, und {anz} hat nur "
                                 f"{len(liste)} Elemente.", z)
        del liste[idx - 1]

    def _a_kopiere(self, k, b):
        _, z, quelle, n, anz = k
        w = self.auswerten(quelle, b)
        if not isinstance(w, (list, dict)):
            raise LaufzeitFehler(f"Kopieren kann ich Listen und Tabellen, hier ist es {typname(w)}.", z)
        b.lege_an(n, anz, list(w) if isinstance(w, list) else dict(w))

    def _a_ersetze(self, k, b):
        _, z, kalt, kneu, n, anz = k
        alt, neu = self.auswerten(kalt, b), self.auswerten(kneu, b)
        ziel = ("var", n, anz, z)
        text = self.auswerten(ziel, b)
        if not (isinstance(text, str) and isinstance(alt, str) and isinstance(neu, str)):
            raise LaufzeitFehler("'Ersetze … durch … in …' braucht drei Texte.", z)
        if alt == "":
            raise LaufzeitFehler("Das zu ersetzende Textstück darf nicht leer sein.", z)
        self._schreibe_ziel(ziel, self._pruefe_text(text.replace(alt, neu), z), b)

    def _a_tabelle_neu(self, k, b):
        _, z, n, anz, paare = k
        t = {}
        for kschluessel, kwert in paare:
            t[self._schluessel(self.auswerten(kschluessel, b), z)] = self.auswerten(kwert, b)
        b.lege_an(n, anz, t)

    def _a_trage(self, k, b):
        _, z, kschluessel, kwert, n, anz = k
        bb = b.finde(n)
        if bb is None:
            raise LaufzeitFehler(f"Ich kenne '{anz}' nicht. Erstelle sie mit 'Erstelle Tabelle namens {anz}.'", z)
        t = self._tabelle(bb.werte[n], z)
        schluessel = self._schluessel(self.auswerten(kschluessel, b), z)
        wert = self.auswerten(kwert, b)
        if schluessel not in t:
            self._pruefe_liste(len(t) + 1, z)
        t[schluessel] = wert

    def _a_sortiere(self, k, b):
        _, z, n, anz, absteigend = k
        try:
            self._liste(n, anz, b, z).sort(key=_sortierschluessel, reverse=absteigend)
        except TypeError:
            raise LaufzeitFehler("Zahlen und Texte kann ich nicht gemeinsam sortieren.", z)

    # Aufgaben
    def _a_aufgabe(self, k, b):
        _, z, n, anz, params, body = k
        self.aufgaben[n] = (anz, params, body)

    def _a_gib(self, k, b):
        raise _Rueckgabe(self.auswerten(k[2], b))

    def _a_fuehre(self, k, b):
        self.auswerten(k[2], b)

    def _rufe(self, n, anz, werte, z):
        if n not in self.aufgaben:
            raise LaufzeitFehler(f"Die Aufgabe '{anz}' ist an dieser Stelle noch nicht bekannt.", z)
        _, params, body = self.aufgaben[n]
        if self.tiefe >= self.grenzen.tiefe:
            raise LaufzeitFehler(f"Zu viele ineinander verschachtelte Aufgaben (mehr als {self.grenzen.tiefe}). "
                                 f"Fehlt in '{anz}' eine Abbruchbedingung?", z)
        neu = Bereich(self.global_bereich)
        for (pn, pa), w in zip(params, werte):
            neu.lege_an(pn, pa, w)
        self.tiefe += 1
        try:
            self.ausfuehren(body, neu)
        except _Rueckgabe as r:
            return r.wert
        except RecursionError:
            raise LaufzeitFehler("Die Verschachtelung ist zu tief geworden.", z)
        except KlarsatzFehler as e:
            e.aufrufe.append((anz, z))                 # so entsteht die Aufrufkette für die Fehlermeldung
            raise
        finally:
            self.tiefe -= 1
        return None

    # Dinge
    def _a_struktur(self, k, b):
        _, z, n, anz, felder = k
        self.strukturen[n] = (anz, felder)

    def _a_erschaffe(self, k, b):
        _, z, tn, tanz, paare, n, anz = k
        if tn not in self.strukturen:
            raise LaufzeitFehler(f"Ich kenne kein '{tanz}'. Beschreibe es zuerst, z. B.: "
                                 f"Ein {tanz} hat einen Namen und ein Alter.", z)
        tanz2, felder = self.strukturen[tn]
        werte = {}
        for fn, fa, ausdruck in paare:
            ziel = next((f for f in felder if passt(f[0], fn)), None)
            if ziel is None:
                raise LaufzeitFehler(f"Ein {tanz2} hat kein Feld '{fa}'. Vorhanden: "
                                     f"{', '.join(f[1] for f in felder)}.", z)
            werte[ziel[0]] = self.auswerten(ausdruck, b)
        fehlend = [f[1] for f in felder if f[0] not in werte]
        if fehlend:
            raise LaufzeitFehler(f"Beim Erschaffen von {tanz2} fehlt noch: {', '.join(fehlend)}.", z)
        b.lege_an(n, anz, Objekt(tanz2, felder, werte))

    def _feld_finden(self, obj, fn, fa, z):
        if not isinstance(obj, Objekt):
            raise LaufzeitFehler(f"'{fa} von ...' geht nur bei Dingen (Strukturen), hier ist es "
                                 f"{typname(obj)}.", z)
        key = obj.schluessel(fn)
        if key is None:
            raise LaufzeitFehler(f"Ein {obj.typ} hat kein Feld '{fa}'. Vorhanden: "
                                 f"{', '.join(a for _, a in obj.felder)}.", z)
        return key

    def _feld_setzen(self, obj, fn, fa, wert, z):
        schluessel = self._feld_finden(obj, fn, fa, z)     # erst prüfen, dann schreiben
        obj.werte[schluessel] = wert

    # Fehlerbehandlung, Dateien, Texte
    def _a_versuche(self, k, b):
        _, z, body, handler = k
        try:
            self.ausfuehren(body, b)
        except LimitFehler:
            raise
        except KlarsatzFehler as e:
            b.werte["fehlermeldung"] = e.meldung
            b.anzeige["fehlermeldung"] = "Fehlermeldung"
            self.ausfuehren(handler, b)

    def _pfad(self, k, b, z):
        p = self.auswerten(k, b)
        if not isinstance(p, str):
            raise LaufzeitFehler(f"Ein Dateiname muss ein Text sein, hier ist es {typname(p)}.", z)
        return p

    # Zeichnen ------------------------------------------------------
    def _zeichenzahl(self, wert, was, z):
        if isinstance(wert, bool) or not _ist_zahl(wert):
            raise LaufzeitFehler(f"Für {was} erwarte ich eine Zahl, bekommen habe ich {als_text(wert)}.", z)
        return wert

    def _a_wiederholung(self, k, b):
        """Das Programm bittet darum, im Takt neu zu laufen — ausführen muss das die Umgebung
        (Browser: Leinwand neu malen, Kommandozeile: Bildschirm löschen und wieder loslegen)."""
        sekunden = self._zeichenzahl(self.auswerten(k[2], b), "den Takt", k[1])
        if not 0.1 <= sekunden <= 3600:
            raise LaufzeitFehler("Der Takt muss zwischen 0,1 und 3600 Sekunden liegen.", k[1])
        self.wiederholung = sekunden

    def _a_warte(self, k, b):
        """Hält das Programm an. Die Wartezeit zählt nicht als Rechenzeit — sonst würde die
        Zeitgrenze eine Uhr abbrechen, die brav jede Sekunde einmal schläft."""
        sekunden = self._zeichenzahl(self.auswerten(k[2], b), "die Wartezeit", k[1])
        if not 0 <= sekunden <= 60:
            raise LaufzeitFehler("Warten geht von 0 bis 60 Sekunden.", k[1])
        # Die Umgebung darf kürzen (Tests laufen mit grenzen.warte = 0 in voller Geschwindigkeit).
        wirklich = min(sekunden, self.grenzen.warte)
        if wirklich > 0:
            time.sleep(wirklich)
        self.start += wirklich

    def _a_loesche_zeichnung(self, k, b):
        self.zeichnung.clear()
        self.striche = 0                      # leere Fläche, also zählt auch nichts mehr
        if self._eigener_kanal:
            self.zeichne(("loeschen",))       # die Oberfläche soll die Fläche leeren
        if self.leinwand:
            # Die Größe der Fläche ist keine Zeichnung, sie überlebt das Löschen. Ohne
            # diese Zeile springt ein laufendes Bild nach dem ersten Löschen zurück in
            # den automatischen Ausschnitt.
            self.zeichne(("leinwand",) + self.leinwand)

    def _a_leinwand(self, k, b):
        """Legt Größe und Ausschnitt der Zeichenfläche fest.

        Ohne diesen Satz sucht die Oberfläche den Ausschnitt selbst und passt ihn an das
        an, was gerade gezeichnet ist. Für ein einzelnes Bild ist das bequem, für ein
        bewegtes ist es fatal: Sobald in einem Durchlauf etwas fehlt, ändert sich der
        Maßstab, und alles springt. Wer die Leinwand angibt, bekommt einen festen Rahmen
        von -Breite/2 bis +Breite/2 und -Höhe/2 bis +Höhe/2."""
        breite = self._zeichenzahl(self.auswerten(k[2], b), "die Breite der Leinwand", k[1])
        hoehe = self._zeichenzahl(self.auswerten(k[3], b), "die Höhe der Leinwand", k[1])
        for mass, was in ((breite, "Breite"), (hoehe, "Höhe")):
            if not 20 <= mass <= 4000:
                raise LaufzeitFehler(
                    f"Die {was} der Leinwand geht von 20 bis 4000, bekommen habe ich {mass:g}.", k[1])
        self.leinwand = (round(breite, 3), round(hoehe, 3))
        self.zeichne(("leinwand",) + self.leinwand)

    def _a_gehe(self, k, b):
        weite = self._zeichenzahl(self.auswerten(k[2], b), "die Schritte", k[1])
        if k[3]:
            weite = -weite
        s = self.stift
        bogen = math.radians(s["winkel"])
        x2, y2 = s["x"] + weite * math.cos(bogen), s["y"] + weite * math.sin(bogen)
        if s["unten"] and weite:
            self.striche += 1
            if self.striche > self.grenzen.striche:
                raise LimitFehler(f"Die Zeichnung hat mehr als {self.grenzen.striche} Striche.", k[1])
            self.zeichne(("linie", round(s["x"], 3), round(s["y"], 3),
                          round(x2, 3), round(y2, 3), s["farbe"], s["breite"]))
        s["x"], s["y"] = x2, y2

    def _a_drehe(self, k, b):
        winkel = self._zeichenzahl(self.auswerten(k[2], b), "den Winkel", k[1])
        self.stift["winkel"] = (self.stift["winkel"] + (winkel if k[3] else -winkel)) % 360

    def _a_beschrifte(self, k, b):
        """Schreibt Text an die Stelle, an der der Stift gerade steht.

        Eine Karte ohne Ortsnamen ist eine halbe Karte. Gemeldet wird -- wie bei den
        Linien auch -- nur, was geschrieben werden soll; wie daraus Buchstaben werden,
        entscheidet die Oberfläche."""
        from .werte import als_text
        text = "".join(als_text(self.auswerten(teil, b)) for teil in k[2])
        groesse = 14 if k[3] is None else self._zeichenzahl(self.auswerten(k[3], b), "die Schriftgröße", k[1])
        if not 4 <= groesse <= 400:
            raise LaufzeitFehler(
                f"Die Schriftgröße geht von 4 bis 400, bekommen habe ich {groesse:g}.", k[1])
        if len(text) > 200:
            raise LaufzeitFehler("Eine Beschriftung darf höchstens 200 Zeichen lang sein.", k[1])
        self.striche += 1
        if self.striche > self.grenzen.striche:
            raise LimitFehler(f"Die Zeichnung hat mehr als {self.grenzen.striche} Striche.", k[1])
        s = self.stift
        self.zeichne(("text", round(s["x"], 3), round(s["y"], 3), text, s["farbe"], groesse))

    def _a_stift(self, k, b):
        self.stift["unten"] = k[2]

    def _a_mitte(self, k, b):
        self.stift["x"] = self.stift["y"] = 0.0
        self.stift["winkel"] = 90.0

    def _a_farbe(self, k, b):
        wert = self.auswerten(k[2], b)
        if not isinstance(wert, str):
            raise LaufzeitFehler('Eine Farbe ist ein Text: Nimm die Farbe "rot".', k[1])
        n = norm(wert)
        if n not in FARBEN:
            nahe = difflib.get_close_matches(n, list(FARBEN), n=1, cutoff=0.6)
            hinweis = f" Meintest du '{nahe[0]}'?" if nahe else ""
            raise LaufzeitFehler(f"Die Farbe '{wert}' kenne ich nicht.{hinweis} "
                                 f"Ich kenne: {', '.join(sorted(FARBEN))}.", k[1])
        self.stift["farbe"] = FARBEN[n]

    def _a_strichstaerke(self, k, b):
        breite = self._zeichenzahl(self.auswerten(k[2], b), "die Strichstärke", k[1])
        if not 1 <= breite <= 50:
            raise LaufzeitFehler("Die Strichstärke muss zwischen 1 und 50 liegen.", k[1])
        self.stift["breite"] = breite

    def _a_lies(self, k, b):
        _, z, kp, n, anz = k
        p = self._pfad(kp, b, z)
        b.lege_an(n, anz, self.fs.lesen(p, min(self.grenzen.datei, self.grenzen.text)))

    def _a_schreibe(self, k, b):
        _, z, kinhalt, kp = k
        inhalt, p = als_text(self.auswerten(kinhalt, b)), self._pfad(kp, b, z)
        self.fs.schreiben(p, inhalt, self.grenzen.datei)

    def _a_teile(self, k, b):
        _, z, ktext, ktrenn, n, anz = k
        text, trenn = self.auswerten(ktext, b), self.auswerten(ktrenn, b)
        if not isinstance(text, str) or not isinstance(trenn, str):
            raise LaufzeitFehler("'Teile ... bei ...' braucht zwei Texte (Zahlen vorher mit 'Verbinde' "
                                 "in einen Text verwandeln).", z)
        if trenn == "":
            raise LaufzeitFehler("Der Trenner darf nicht leer sein.", z)
        teile = text.split(trenn)
        self._pruefe_liste(len(teile), z)
        b.lege_an(n, anz, teile)

    def _a_verbinde(self, k, b):
        _, z, teile, n, anz = k
        b.lege_an(n, anz, self._pruefe_text("".join(als_text(self.auswerten(t, b)) for t in teile), z))

    def _a_sicher(self, k, b):
        _, z, bed = k
        if not self.bed(bed, b):
            raise LaufzeitFehler(f"Die Zusicherung in Zeile {z} stimmt nicht.", z)

    # ── Bedingungen ─────────────────────────────────────────────────
    def bed(self, k, b):
        art = k[0]
        if art == "und":
            return self.bed(k[1], b) and self.bed(k[2], b)
        if art == "oder":
            return self.bed(k[1], b) or self.bed(k[2], b)
        if art == "nicht":
            return not self.bed(k[1], b)
        if art == "vgl":
            return self._vergleich(k[1], self.auswerten(k[2], b), self.auswerten(k[3], b), k[4])
        if art == "typ":
            w = self.auswerten(k[1], b)
            if k[2] == "zahl":
                return _ist_zahl(w)
            if k[2] == "text":
                return isinstance(w, str)
            return isinstance(w, dict) if k[2] == "tabelle" else isinstance(w, list)
        w = self.auswerten(k[1], b)                       # "wahrheit"
        if not isinstance(w, bool):
            raise LaufzeitFehler(f"Hier brauche ich wahr oder falsch, aber es ist {typname(w)} "
                                 f"({als_text(w)}). Vergleiche mit 'gleich', 'größer als', ...", k[2])
        return w

    def _vergleich(self, op, a, b, z):
        if op == "==":
            return _gleich(a, b)
        if op == "enthaelt":
            if isinstance(a, list):
                return any(_gleich(x, b) for x in a)
            if isinstance(a, dict):
                return not isinstance(b, (list, dict)) and any(_gleich(x, b) for x in a)
            if isinstance(a, str) and isinstance(b, str):
                return b in a
            raise LaufzeitFehler("'enthält' geht bei Listen, Tabellen (Schlüssel) und Texten "
                                 "(dann muss auch das Gesuchte ein Text sein).", z)
        if op == "teilbar":
            if not (_ist_zahl(a) and _ist_zahl(b)):
                raise LaufzeitFehler("'teilbar' geht nur mit Zahlen.", z)
            if b == 0:
                raise LaufzeitFehler("Durch null kann man nicht teilen.", z)
            return a % b == 0
        if not ((_ist_zahl(a) and _ist_zahl(b)) or (isinstance(a, str) and isinstance(b, str))):
            raise LaufzeitFehler(f"Ich kann {typname(a)} und {typname(b)} nicht der Größe nach vergleichen.", z)
        if isinstance(a, str):
            a, b = norm(a), norm(b)
        return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    # ── Ausdrücke ───────────────────────────────────────────────────
    def _lies_var(self, n, anz, b, z):
        bb = b.finde(n)
        if bb is None:
            bekannt = b.bekannte()
            nahe = difflib.get_close_matches(n, list(bekannt), n=1, cutoff=0.6)
            hinweis = f" Meintest du '{bekannt[nahe[0]]}'?" if nahe else ""
            raise LaufzeitFehler(f"Ich kenne '{anz}' nicht. Lege es zuerst mit 'Merke ... als {anz}.' an."
                                 f"{hinweis}", z)
        return bb.werte[n]

    def auswerten(self, k, b):
        art = k[0]
        if art == "wert":
            return k[1]
        if art == "var":
            return self._lies_var(k[1], k[2], b, k[3])
        if art == "bin":
            return self._rechne(k[1], self.auswerten(k[2], b), self.auswerten(k[3], b), k[4])
        if art == "aufruf":
            return self._rufe(k[1], k[2], [self.auswerten(a, b) for a in k[3]], k[4])
        if art == "feld":
            obj = self.auswerten(k[3], b)
            # Erst prüfen, dann zugreifen: Sonst stolpert Python über obj.werte,
            # bevor die freundliche Meldung aus _feld_finden greift.
            schluessel = self._feld_finden(obj, k[1], k[2], k[4])
            return obj.werte[schluessel]
        if art == "laenge":
            w = self.auswerten(k[1], b)
            if not isinstance(w, (str, list, dict)):
                raise LaufzeitFehler(f"Eine Länge haben Texte, Listen und Tabellen, hier ist es {typname(w)}.", k[2])
            return len(w)
        if art in ("kleinbuchstaben", "grossbuchstaben"):
            w = self.auswerten(k[1], b)
            if not isinstance(w, str):
                name = "Kleinbuchstaben" if art == "kleinbuchstaben" else "Großbuchstaben"
                raise LaufzeitFehler(f"'{name} von ...' braucht einen Text, hier ist es {typname(w)}.", k[2])
            return w.lower() if art == "kleinbuchstaben" else w.upper()
        if art == "jetzt":
            return self._w_jetzt(k, b)
        if art == "zufall":
            a, e = self.auswerten(k[1], b), self.auswerten(k[2], b)
            if isinstance(a, bool) or isinstance(e, bool) or not isinstance(a, int) or not isinstance(e, int):
                raise LaufzeitFehler("'Zufallszahl von ... bis ...' braucht zwei ganze Zahlen.", k[3])
            if a > e:
                raise LaufzeitFehler(f"Zufallszahl von {a} bis {e} geht nicht: die erste Zahl darf nicht "
                                     "größer sein als die zweite.", k[3])
            return self.zufall.randint(a, e)
        if art in ("abgerundet", "aufgerundet", "gerundet"):
            w = self.auswerten(k[1], b)
            if not _ist_zahl(w):
                raise LaufzeitFehler(f"'{art.capitalize()} von ...' braucht eine Zahl, hier ist es {typname(w)}.", k[2])
            if art == "abgerundet":
                return math.floor(w)
            if art == "aufgerundet":
                return math.ceil(w)
            st = 0 if k[3] is None else self.auswerten(k[3], b)
            if isinstance(st, bool) or not isinstance(st, int) or not 0 <= st <= 12:
                raise LaufzeitFehler("Die Zahl der Stellen muss eine ganze Zahl von 0 bis 12 sein.", k[2])
            d = runde_dezimal(w, st)
            return int(d) if st == 0 else float(d)
        if art == "formatiert":
            w, st = self.auswerten(k[1], b), self.auswerten(k[2], b)
            if not _ist_zahl(w):
                raise LaufzeitFehler(f"'Formatiert von ...' braucht eine Zahl, hier ist es {typname(w)}.", k[3])
            if isinstance(st, bool) or not isinstance(st, int) or not 0 <= st <= 12:
                raise LaufzeitFehler("Die Zahl der Stellen muss eine ganze Zahl von 0 bis 12 sein.", k[3])
            d = runde_dezimal(w, st)
            if d == 0:
                d = abs(d)                                # kein "-0,00"
            return format(d, "f").replace(".", ",")
        if art == "verkettet":
            liste, trenn = self.auswerten(k[1], b), self.auswerten(k[2], b)
            if not isinstance(liste, list) or not isinstance(trenn, str):
                raise LaufzeitFehler("'Verkettet von Liste mit Trenner' braucht eine Liste und einen Text als Trenner.", k[3])
            teile = [als_text(x) for x in liste]
            if sum(map(len, teile)) + len(trenn) * max(0, len(teile) - 1) > self.grenzen.text:
                raise LaufzeitFehler(f"Der Text würde zu lang (mehr als {self.grenzen.text} Zeichen).", k[3])
            return trenn.join(teile)
        if art == "zahlenwert":
            w = self.auswerten(k[1], b)
            if _ist_zahl(w):
                return w
            if isinstance(w, str):
                z2 = _auto_zahl(w.strip())
                if _ist_zahl(z2):
                    return z2
                raise LaufzeitFehler(f"Aus „{w}“ kann ich keine Zahl machen.", k[2])
            raise LaufzeitFehler(f"Aus {typname(w)} kann ich keine Zahl machen.", k[2])
        if art == "zufallselement":
            w = self.auswerten(k[1], b)
            if not isinstance(w, (list, str)):
                raise LaufzeitFehler(f"Ein zufälliges Element gibt es bei Listen und Texten, hier ist es {typname(w)}.", k[2])
            if len(w) == 0:
                raise LaufzeitFehler("Da ist nichts drin – ein zufälliges Element gibt es nicht.", k[2])
            return self.zufall.choice(w)
        if art == "tabellenwert":
            schluessel = self._schluessel(self.auswerten(k[1], b), k[3])
            t = self._tabelle(self.auswerten(k[2], b), k[3])
            if schluessel not in t:
                raise LaufzeitFehler(f"In der Tabelle gibt es keinen Eintrag für {als_text(schluessel)}. "
                                     "(Vorher prüfen: Wenn Tabelle enthält Schlüssel …)", k[3])
            return t[schluessel]
        if art == "ausschnitt":
            _, was, kvon, kbis, kquelle, z2 = k
            quelle, von, bis = self.auswerten(kquelle, b), self.auswerten(kvon, b), self.auswerten(kbis, b)
            erwartet = str if was == "zeichen" else list
            if not isinstance(quelle, erwartet):
                raise LaufzeitFehler(f"'{was.capitalize()} … bis … von …' gibt es bei "
                                     f"{'Texten' if was == 'zeichen' else 'Listen'}, hier ist es {typname(quelle)}.", z2)
            for x in (von, bis):
                if isinstance(x, bool) or not isinstance(x, int):
                    raise LaufzeitFehler(f"Die Nummern müssen ganze Zahlen sein (hier: {als_text(x)}).", z2)
            if not 1 <= von <= bis <= len(quelle):
                raise LaufzeitFehler(f"{was.capitalize()} {von} bis {bis} gibt es nicht – gezählt wird ab 1, "
                                     f"es sind {len(quelle)}, und die erste Nummer darf nicht größer sein als die zweite.", z2)
            return quelle[von - 1:bis]
        if art in ("rechtsbuendig", "linksbuendig"):
            text = als_text(self.auswerten(k[1], b))
            breite = self.auswerten(k[2], b)
            if isinstance(breite, bool) or not _ist_zahl(breite) or breite != int(breite):
                raise LaufzeitFehler(f"'{art.capitalize()} von ... auf ... Zeichen' braucht eine ganze "
                                     f"Zahl, hier ist es {typname(breite)}.", k[3])
            breite = int(breite)
            if not 0 <= breite <= self.grenzen.text:
                raise LaufzeitFehler(f"Die Breite muss zwischen 0 und {self.grenzen.text} liegen.", k[3])
            return text.rjust(breite) if art == "rechtsbuendig" else text.ljust(breite)
        if art in WINKEL:
            w = self.auswerten(k[1], b)
            if isinstance(w, bool) or not _ist_zahl(w):
                raise LaufzeitFehler(f"'{art.capitalize()} von ...' braucht eine Zahl (Grad), "
                                     f"hier ist es {typname(w)}.", k[2])
            if art == "tangens" and (w - 90) % 180 == 0:
                raise LaufzeitFehler(f"Der Tangens von {als_text(w)} Grad ist nicht bestimmt – "
                                     "dort steht der Winkel senkrecht.", k[2])
            return _ohne_rauschen(WINKEL[art](math.radians(w)))
        if art in ARKUS:
            w = self.auswerten(k[1], b)
            if isinstance(w, bool) or not _ist_zahl(w):
                raise LaufzeitFehler(f"'{art.capitalize()} von ...' braucht eine Zahl, "
                                     f"hier ist es {typname(w)}.", k[2])
            if art != "arkustangens" and not -1 <= w <= 1:
                raise LaufzeitFehler(f"'{art.capitalize()} von ...' geht nur mit Werten zwischen "
                                     f"-1 und 1, hier ist es {als_text(w)}.", k[2])
            return _ohne_rauschen(math.degrees(ARKUS[art](w)))
        if art in ("wurzel", "betrag"):
            w = self.auswerten(k[1], b)
            if not _ist_zahl(w):
                raise LaufzeitFehler(f"'{art.capitalize()} von ...' braucht eine Zahl, hier ist es {typname(w)}.", k[2])
            if art == "betrag":
                return abs(w)
            if w < 0:
                raise LaufzeitFehler("Aus einer negativen Zahl kann ich keine Wurzel ziehen.", k[2])
            if isinstance(w, int):
                r = math.isqrt(w)
                return r if r * r == w else math.sqrt(w)
            return math.sqrt(w)
        if art == "rest":
            return self._rechne("rest", self.auswerten(k[1], b), self.auswerten(k[2], b), k[3])
        if art == "pos":
            liste = self._als_sequenz(self.auswerten(k[2], b), k[3])
            if not liste:
                raise LaufzeitFehler("Die Liste ist leer, ein erstes oder letztes Element gibt es nicht.", k[3])
            return liste[0] if k[1] == "erste" else liste[-1]
        if art == "element":
            idx, liste = self.auswerten(k[1], b), self._als_sequenz(self.auswerten(k[2], b), k[3])
            if not isinstance(idx, int) or isinstance(idx, bool):
                raise LaufzeitFehler(f"Die Nummer eines Elements muss eine ganze Zahl sein (hier: {als_text(idx)}).", k[3])
            if not 1 <= idx <= len(liste):
                raise LaufzeitFehler(f"Element {idx} gibt es nicht – gezählt wird ab 1, und es sind nur "
                                     f"{len(liste)} Elemente.", k[3])
            return liste[idx - 1]
        raise LaufzeitFehler(f"Interner Fehler: unbekannter Ausdruck '{art}'.")

    def _als_sequenz(self, w, z):
        if not isinstance(w, (list, str)):
            raise LaufzeitFehler(f"Elemente hat nur eine Liste oder ein Text, hier ist es {typname(w)}.", z)
        return w

    def _zahl(self, r, z):
        if isinstance(r, int) and r.bit_length() > self.grenzen.zahl_bits:
            raise LaufzeitFehler("Die Zahl wird zu groß.", z)
        return r

    def _rechne(self, op, a, b, z):
        if not (_ist_zahl(a) and _ist_zahl(b)):
            hinweis = (" Texte verbindest du mit 'Verbinde ... zu ...' oder mit 'und' bei 'Zeige'."
                       if isinstance(a, str) or isinstance(b, str) else "")
            raise LaufzeitFehler(f"Mit '{op}' kann ich nur Zahlen verrechnen, hier stehen aber "
                                 f"{typname(a)} und {typname(b)}.{hinweis}", z)
        if op == "plus":
            return self._zahl(a + b, z)
        if op == "minus":
            return self._zahl(a - b, z)
        if op == "mal":
            return self._zahl(a * b, z)
        if op == "geteilt":
            if b == 0:
                raise LaufzeitFehler("Durch null kann man nicht teilen.", z)
            return a // b if isinstance(a, int) and isinstance(b, int) and a % b == 0 else a / b
        if op == "rest":
            if b == 0:
                raise LaufzeitFehler("Durch null kann man nicht teilen (auch nicht für den Rest).", z)
            return a % b
        if op == "hoch":
            if isinstance(a, int) and isinstance(b, int) and abs(a) > 1 and b > 0 \
                    and b * math.log2(abs(a)) > self.grenzen.zahl_bits:
                raise LaufzeitFehler("Diese Potenz wird zu groß.", z)
            try:
                r = a ** b
            except ZeroDivisionError:
                raise LaufzeitFehler("Null hoch einer negativen Zahl ist nicht definiert.", z)
            if isinstance(r, complex):
                raise LaufzeitFehler("Das Ergebnis wäre keine reelle Zahl.", z)
            return self._zahl(r, z)
        raise LaufzeitFehler(f"Interner Fehler: unbekannte Rechenart '{op}'.", z)
