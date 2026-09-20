"""Satzmuster-Parser: Tokens -> Syntaxbaum (Tupel)."""
import difflib

from .fehler import SyntaxFehler
from .lexer import Token, norm

# ════════════════════════════════════════════════════════════════════
#  Parser  (Satzmuster -> AST aus Tupeln)
# ════════════════════════════════════════════════════════════════════
# Wörter, die nie als Name für Variablen/Aufgaben taugen:
RESERVIERT = {
    "ist", "sind", "und", "oder", "nicht", "plus", "minus", "mal", "geteilt", "durch", "hoch",
    "als", "auf", "um", "von", "mit", "zu", "aus", "in", "bis", "hinzu", "wenn", "sonst",
    "ende", "solange", "dass", "hat", "bei", "gleich", "groesser", "kleiner", "mindestens",
    "hoechstens", "teilbar", "wahr", "falsch", "jedes", "jede", "jeden", "zurueck",
    "enthaelt", "keine",
}

STARTER = {
    "zeige": ("s_zeige", "Zeige"), "frage": ("s_frage", "Frage"),
    "merke": ("s_merke", "Merke"), "setze": ("s_setze", "Setze"),
    "erhoehe": ("s_aendere", "Erhöhe"), "verringere": ("s_aendere", "Verringere"),
    "verdopple": ("s_aendere", "Verdopple"), "halbiere": ("s_aendere", "Halbiere"),
    "wenn": ("s_wenn", "Wenn"), "wiederhole": ("s_wiederhole", "Wiederhole"),
    "zaehle": ("s_zaehle", "Zähle"), "fuer": ("s_fuer", "Für"),
    "hoere": ("s_hoere", "Höre"), "mach": ("s_mach", "Mach"),
    "erstelle": ("s_erstelle", "Erstelle"), "fuege": ("s_fuege", "Füge"),
    "entferne": ("s_entferne", "Entferne"), "sortiere": ("s_sortiere", "Sortiere"),
    "definiere": ("s_aufgabe", "Definiere"), "gib": ("s_gib", "Gib"),
    "fuehre": ("s_fuehre", "Führe"), "erschaffe": ("s_erschaffe", "Erschaffe"),
    "versuche": ("s_versuche", "Versuche"), "lies": ("s_lies", "Lies"),
    "schreibe": ("s_schreibe", "Schreibe"), "verbinde": ("s_verbinde", "Verbinde"),
    "stelle": ("s_stelle", "Stelle"), "teile": ("s_teile", "Teile"),
    "kopiere": ("s_kopiere", "Kopiere"), "ersetze": ("s_ersetze", "Ersetze"), "trage": ("s_trage", "Trage"),
    "gehe": ("s_gehe", "Gehe"), "drehe": ("s_drehe", "Drehe"),
    "warte": ("s_warte", "Warte"), "loesche": ("s_loesche", "Lösche"),
    "hebe": ("s_stift", "Hebe"), "senke": ("s_stift", "Senke"), "nimm": ("s_nimm", "Nimm"),
}

# Wörter, die nach einer geschlossenen Klammer zeigen: "(a plus b) größer als 3" ist eine Rechenklammer
FORTSETZUNG = {"plus", "minus", "mal", "geteilt", "hoch", "groesser", "kleiner", "gleich", "mindestens",
               "hoechstens", "durch", "teilbar", "enthaelt", "zahl", "text", "liste", "tabelle", "keine", "nicht"}


class Parser:
    def __init__(self, tokens, vorwissen=None, max_tiefe=50):
        self.t = tokens
        self.i = 0
        self.aufgaben = dict(vorwissen or {})   # Name -> Anzahl Parameter (Vorab-Scan, damit Aufrufe eindeutig sind)
        self.max_tiefe = max_tiefe
        self.tiefe = 0
        self.hinweise = []       # [(Zeile, Text)] – weiche Hinweise für den Prüfmodus
        self._vorscan()

    # ── Hilfen ──────────────────────────────────────────────────────
    def _vorscan(self):
        t = self.t
        for i, tok in enumerate(t):
            if tok.art == "WORT" and tok.norm == "definiere" and t[i + 1].norm == "aufgabe" \
                    and t[i + 2].art == "WORT":
                name, j, stelligkeit = t[i + 2].norm, i + 3, 0
                if t[j].art == "WORT" and t[j].norm in ("mit", "von"):
                    j += 1
                    stelligkeit = 1
                    while t[j + 1].art == "WORT" and t[j + 1].norm == "und":
                        stelligkeit += 1
                        j += 2
                self.aufgaben[name] = stelligkeit

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else self.t[-1]

    def nimm(self):
        tok = self.t[self.i]
        if tok.art != "EOF":
            self.i += 1
        return tok

    def ist_wort(self, *normen, k=0):
        tok = self.peek(k)
        return tok.art == "WORT" and tok.norm in normen

    def ist_sym(self, s, k=0):
        return self.peek(k).art == s

    def fehler(self, meldung, tok=None, zeile=None, spalte=None, laenge=None):
        tok = tok or self.peek()
        if zeile is None:
            zeile, spalte, laenge = tok.zeile, tok.spalte, tok.laenge
        raise SyntaxFehler(meldung, zeile, spalte, laenge)

    def _nach_letztem(self, meldung):
        """Fehler direkt hinter dem zuletzt gelesenen Wort (z. B. fehlender Punkt)."""
        vor = self.t[self.i - 1] if self.i > 0 else self.peek()
        self.fehler(meldung, zeile=vor.zeile, spalte=vor.spalte + vor.laenge, laenge=1)

    def _tiefer(self):
        self.tiefe += 1
        if self.tiefe > self.max_tiefe:
            self.fehler(f"Das ist zu tief verschachtelt (mehr als {self.max_tiefe} Ebenen ineinander).")

    @staticmethod
    def beschreibe(tok):
        if tok.art == "EOF":
            return "das Ende des Programms"
        if tok.art in (".", ",", ":", "(", ")"):
            return f"'{tok.art}'"
        if tok.art == "TEXT":
            return f'den Text "{tok.wert}"'
        if tok.art == "ZAHL":
            return f"die Zahl {tok.wert}"
        return f"'{tok.wert}'"

    def erwarte_wort(self, n, anzeige=None):
        if not self.ist_wort(n):
            self.fehler(f"Hier erwarte ich '{anzeige or n}', gefunden habe ich aber "
                        f"{self.beschreibe(self.peek())}.")
        return self.nimm()

    def erwarte_sym(self, s):
        if not self.ist_sym(s):
            wo = {":": "Nach der Kopfzeile erwarte ich einen Doppelpunkt ':'",
                  ")": "Hier fehlt die schließende Klammer ')'"}.get(s, f"Hier erwarte ich '{s}'")
            self.fehler(f"{wo}, gefunden habe ich aber {self.beschreibe(self.peek())}.")
        return self.nimm()

    def punkt(self):
        if not self.ist_sym("."):
            if self.ist_sym("-"):
                self.fehler("Ein Minuszeichen gibt es nur vor Zahlen (-5). Zum Rechnen schreibe 'minus': "
                            "Zeige 3 minus 2.")
            self._nach_letztem(f"Am Ende des Satzes fehlt ein Punkt (stattdessen kommt "
                               f"{self.beschreibe(self.peek())}).")
        self.nimm()

    def ende(self):
        self.erwarte_wort("ende", "Ende")
        if not self.ist_sym("."):
            self._nach_letztem("Nach 'Ende' fehlt der Punkt.")
        self.nimm()

    def name(self, variable=False):
        tok = self.peek()
        if tok.art != "WORT" or tok.norm in RESERVIERT:
            self.fehler(f"Hier erwarte ich einen Namen, gefunden habe ich aber {self.beschreibe(tok)}.")
        if variable and tok.norm in self.aufgaben:
            self.fehler(f"'{tok.wert}' ist schon der Name einer Aufgabe – eine Variable darf nicht genauso "
                        "heißen. Nimm bitte einen anderen Namen.")
        return self.nimm()

    def block(self, start_zeile, enders=("ende",)):
        stmts = []
        while True:
            tok = self.peek()
            if tok.art == "EOF":
                self.fehler(f"Der Block aus Zeile {start_zeile} wurde nie mit 'Ende.' geschlossen.",
                            zeile=start_zeile)
            if tok.art == "WORT" and tok.norm in enders:
                return stmts
            stmts.append(self.anweisung())

    # ── Programm & Anweisungen ─────────────────────────────────────
    def programm(self):
        stmts = []
        try:
            while self.peek().art != "EOF":
                stmts.append(self.anweisung())
        except RecursionError:
            raise SyntaxFehler("Das Programm ist zu tief verschachtelt.")
        return stmts

    def anweisung(self):
        self._tiefer()
        try:
            return self._anweisung_roh()
        finally:
            self.tiefe -= 1

    def _anweisung_roh(self):
        tok = self.peek()
        if tok.art == "WORT":
            eintrag = STARTER.get(tok.norm)
            if eintrag:
                return getattr(self, eintrag[0])()
            if self.ist_wort("hat", k=1):
                return self.s_struktur()
        self.unbekannt(tok)

    def unbekannt(self, tok):
        if tok.art != "WORT":
            self.fehler("Ein Satz muss mit einem Verb beginnen (z. B. Zeige, Merke, Wenn). "
                        f"Gefunden: {self.beschreibe(tok)}.")
        n = tok.norm
        if n in ("sonst", "ende", "bei"):
            self.fehler(f"'{tok.wert}' steht hier ohne passendes 'Wenn', 'Wiederhole', 'Versuche' "
                        "oder 'Definiere' davor.")
        if n in self.aufgaben:
            self.fehler(f"Ich verstehe den Satz nicht. Meintest du: 'Führe {tok.wert} ... aus.'? "
                        f"(Eine Aufgabe ruft man mit 'Führe ... aus' auf oder nutzt sie in einem Ausdruck.)")
        nahe = difflib.get_close_matches(n, list(STARTER), n=1, cutoff=0.6)
        hinweis = f" Meintest du '{STARTER[nahe[0]][1]}'?" if nahe else ""
        self.fehler(f"Ich verstehe den Satz nicht: er beginnt mit '{tok.wert}'.{hinweis}")

    # Ausgabe / Eingabe ---------------------------------------------
    def s_zeige(self):
        z = self.nimm().zeile
        items = [self.summe()]
        while self.ist_wort("und"):
            self.nimm()
            items.append(self.summe())
        self.punkt()
        return ("zeige", z, items)

    def s_frage(self):
        z = self.nimm().zeile
        frage = self.summe()
        # Optional: "Frage ... als Zahl und merke ...". Die Typangabe steht *vor* dem
        # "und merke" — dadurch ist sie eindeutig von einem Variablennamen "Zahl"
        # zu unterscheiden, der hinter dem zweiten "als" stünde. Darum müssen "Zahl"
        # und "Text" auch nicht reserviert werden.
        typ = None
        if self.ist_wort("als") and self.peek(1).art == "WORT" and self.peek(1).norm in ("zahl", "text"):
            self.nimm()
            typ = self.nimm().norm
        self.erwarte_wort("und")
        self.erwarte_wort("merke", "merke")
        if self.ist_wort("antwort"):
            self.nimm()
        self.erwarte_wort("als")
        t = self.name(True)
        self.punkt()
        return ("frage", z, frage, t.norm, t.wert, typ)

    # Variablen -----------------------------------------------------
    def s_merke(self):
        z = self.nimm().zeile
        konstant = False
        if self.ist_wort("fuer") and self.ist_wort("immer", k=1):
            self.nimm(); self.nimm()
            konstant = True
        wert = self.summe()
        self.erwarte_wort("als")
        t = self.name(True)
        self.punkt()
        return ("merke", z, wert, t.norm, t.wert, konstant)

    def ziel(self):
        t = self.name()
        if self.ist_wort("von"):
            self.nimm()
            o = self.name(True)
            return ("feld", t.norm, t.wert, ("var", o.norm, o.wert, o.zeile), t.zeile)
        if t.norm in self.aufgaben:
            self.fehler(f"'{t.wert}' ist der Name einer Aufgabe, keiner Variablen.", tok=t)
        return ("var", t.norm, t.wert, t.zeile)

    def s_setze(self):
        z = self.nimm().zeile
        ziel = self.ziel()
        self.erwarte_wort("auf")
        wert = self.summe()
        self.punkt()
        return ("setze", z, ziel, wert)

    def s_aendere(self):
        t = self.nimm()
        n = t.norm
        ziel = self.ziel()
        if n in ("erhoehe", "verringere"):
            op = "plus" if n == "erhoehe" else "minus"
            if self.ist_wort("um"):
                self.nimm()
                wert = self.summe()
            else:
                wert = ("wert", 1)
        else:
            op = "mal" if n == "verdopple" else "geteilt"
            wert = ("wert", 2)
        self.punkt()
        return ("aendere", t.zeile, ziel, op, wert)

    # Bedingungen ---------------------------------------------------
    def s_wenn(self):
        z = self.nimm().zeile
        bed = self.bedingung()
        zweige, sonst = [], None
        if self.ist_sym(":"):                              # Blockform
            self.nimm()
            zweige.append((bed, self.block(z, ("ende", "sonst"))))
            while self.ist_wort("sonst"):
                sz = self.nimm().zeile
                if self.ist_wort("wenn"):
                    self.nimm()
                    b2 = self.bedingung()
                    self.erwarte_sym(":")
                    zweige.append((b2, self.block(sz, ("ende", "sonst"))))
                else:
                    self.erwarte_sym(":")
                    sonst = self.block(sz, ("ende",))
            self.ende()
        elif self.ist_sym(","):                            # Kurzform: ein Satz
            self.nimm()
            zweige.append((bed, [self.anweisung()]))
            while self.ist_wort("sonst"):
                merke = self.i
                self.nimm()
                if self.ist_wort("wenn"):
                    self.nimm()
                    b2 = self.bedingung()
                    if not self.ist_sym(","):              # gehört zu einem äußeren Block-Wenn
                        self.i = merke
                        break
                    self.nimm()
                    zweige.append((b2, [self.anweisung()]))
                else:
                    if self.ist_sym(":"):
                        self.i = merke
                        break
                    if self.ist_sym(","):
                        self.nimm()
                    sonst = [self.anweisung()]
                    break
        else:
            self.fehler("Nach der Bedingung erwarte ich ':' (Block bis 'Ende.') oder ',' (ein einzelner "
                        f"Satz), gefunden habe ich aber {self.beschreibe(self.peek())}.")
        return ("wenn", z, zweige, sonst)

    def bedingung(self):
        l = self._und_bed()
        while self.ist_wort("oder"):
            self.nimm()
            l = ("oder", l, self._und_bed())
        return l

    def _und_bed(self):
        l = self._nicht_bed()
        while self.ist_wort("und"):
            self.nimm()
            l = ("und", l, self._nicht_bed())
        return l

    def _nicht_bed(self):
        self._tiefer()
        try:
            return self._nichtbed_roh()
        finally:
            self.tiefe -= 1

    def _nichtbed_roh(self):
        if self.ist_wort("nicht"):
            self.nimm()
            return ("nicht", self._nicht_bed())
        if self.ist_sym("("):
            gruppe = self._klammer_bedingung()
            if gruppe is not None:
                return gruppe
        return self.vergleich()

    def _klammer_bedingung(self):
        """'(a kleiner als 3 oder b …) und …' – aber '(a plus b) größer als 3' bleibt eine Rechenklammer."""
        merke = self.i
        try:
            self.nimm()
            inhalt = self.bedingung()
            if not self.ist_sym(")"):
                raise SyntaxFehler("Klammer nicht geschlossen")
            self.nimm()
        except SyntaxFehler:
            self.i = merke
            return None
        k = 1 if self.ist_wort("ist", "sind") else 0     # "(…) ist größer als 3": Rechenklammer
        if self.peek(k).art == "WORT" and self.peek(k).norm in FORTSETZUNG:
            self.i = merke
            return None
        self._ist()
        return inhalt

    def _ist(self):
        if self.ist_wort("ist", "sind"):
            self.nimm()

    def vergleich(self):
        z = self.peek().zeile
        links = self.summe()
        self._ist()
        neg, neg_wort = False, None
        if self.ist_wort("nicht", "keine"):
            neg_wort = self.nimm().norm
            neg = True
        if self.ist_wort("zahl", "text", "liste", "tabelle"):  # 'Wenn Antwort keine Zahl ist:'
            typ = self.nimm().norm
            self._ist()
            node = ("typ", links, typ, z)
            return ("nicht", node) if neg else node
        if neg_wort == "keine":
            self.fehler("Nach 'keine' erwarte ich Zahl, Text, Liste oder Tabelle (z. B. 'Wenn Antwort keine Zahl ist:').")
        if self.ist_wort("groesser"):
            self.nimm(); self.erwarte_wort("als"); op, rechts = ">", self.summe()
        elif self.ist_wort("kleiner"):
            self.nimm(); self.erwarte_wort("als"); op, rechts = "<", self.summe()
        elif self.ist_wort("gleich"):
            self.nimm(); op, rechts = "==", self.summe()
        elif self.ist_wort("mindestens"):
            self.nimm(); op, rechts = ">=", self.summe()
        elif self.ist_wort("hoechstens"):
            self.nimm(); op, rechts = "<=", self.summe()
        elif self.ist_wort("durch"):
            self.nimm(); rechts = self.summe(); self.erwarte_wort("teilbar"); op = "teilbar"
        elif self.ist_wort("enthaelt"):
            self.nimm(); op, rechts = "enthaelt", self.summe()
        else:
            if neg:
                self.fehler("Nach 'nicht' erwarte ich einen Vergleich (gleich, größer als, ... teilbar).")
            return ("wahrheit", links, z)
        self._ist()
        node = ("vgl", op, links, rechts, z)
        return ("nicht", node) if neg else node

    # Schleifen -----------------------------------------------------
    def s_wiederhole(self):
        z = self.nimm().zeile
        if self.ist_wort("dieses"):
            # "Wiederhole dieses Programm jede Sekunde." / "… alle 5 Sekunden."
            self.nimm()
            self.erwarte_wort("programm", "Programm")
            if self.ist_wort("jede", "jeden", "jedes"):
                self.nimm()
                takt = ("wert", 1)
            else:
                self.erwarte_wort("alle", "alle")
                takt = self.summe()
            if not self.ist_wort("sekunde", "sekunden"):
                self.fehler("Hier erwarte ich 'Sekunde' oder 'Sekunden' "
                            "(Wiederhole dieses Programm jede Sekunde).")
            self.nimm()
            self.punkt()
            return ("wiederholung", z, takt)
        if self.ist_wort("solange"):
            self.nimm()
            b = self.bedingung()
            self.erwarte_sym(":")
            body = self.block(z)
            self.ende()
            return ("solange", z, b, body)
        n = self.summe()
        self.erwarte_wort("mal", "Mal")
        self.erwarte_sym(":")
        body = self.block(z)
        self.ende()
        return ("wiederhole_n", z, n, body)

    def s_zaehle(self):
        z = self.nimm().zeile
        self.erwarte_wort("von")
        a = self.summe()
        self.erwarte_wort("bis")
        b = self.summe()
        rueck = False
        if self.ist_wort("rueckwaerts", "abwaerts"):
            self.nimm()
            rueck = True
        schritt = None
        if self.ist_wort("in"):
            self.nimm()
            self.erwarte_wort("schritten", "Schritten")
            self.erwarte_wort("von")
            schritt = self.summe()
        var = None
        if self.ist_wort("mit"):
            self.nimm()
            t = self.name(True)
            var = (t.norm, t.wert)
        self.erwarte_sym(":")
        body = self.block(z)
        self.ende()
        return ("zaehle", z, a, b, schritt, var, body, rueck)

    def s_fuer(self):
        z = self.nimm().zeile
        if not self.ist_wort("jedes", "jede", "jeden"):
            self.fehler("Nach 'Für' erwarte ich 'jedes' (Für jedes Element in Liste:).")
        self.nimm()
        t = self.name(True)
        self.erwarte_wort("in")
        liste = self.summe()
        self.erwarte_sym(":")
        body = self.block(z)
        self.ende()
        return ("fuer", z, t.norm, t.wert, liste, body)

    def s_hoere(self):
        z = self.nimm().zeile
        self.erwarte_wort("auf", "auf")
        self.punkt()
        return ("abbruch", z)

    def s_mach(self):
        z = self.nimm().zeile
        self.erwarte_wort("weiter")
        self.punkt()
        return ("weiter", z)

    # Listen --------------------------------------------------------
    def s_erstelle(self):
        z = self.nimm().zeile
        if self.ist_wort("tabelle"):
            self.nimm()
            self.erwarte_wort("namens")
            t = self.name(True)
            paare = []
            if self.ist_wort("mit"):
                self.nimm()
                while True:
                    schluessel = self.summe()
                    self.erwarte_wort("als")
                    paare.append((schluessel, self.summe()))
                    if self.ist_wort("und"):
                        self.nimm()
                    else:
                        break
            self.punkt()
            return ("tabelle_neu", z, t.norm, t.wert, paare)
        if not self.ist_wort("liste"):
            self.fehler("Nach 'Erstelle' erwarte ich 'Liste namens …' oder 'Tabelle namens …', gefunden "
                        f"habe ich aber {self.beschreibe(self.peek())}.")
        self.nimm()
        self.erwarte_wort("namens")
        t = self.name(True)
        werte = []
        if self.ist_wort("mit"):
            self.nimm()
            werte.append(self.summe())
            while self.ist_wort("und"):
                self.nimm()
                werte.append(self.summe())
        self.punkt()
        return ("liste_neu", z, t.norm, t.wert, werte)

    def s_fuege(self):
        z = self.nimm().zeile
        wert = self.summe()
        self.erwarte_wort("zu")
        t = self.name(True)
        self.erwarte_wort("hinzu")
        self.punkt()
        return ("liste_add", z, wert, t.norm, t.wert)

    def s_entferne(self):
        z = self.nimm().zeile
        if self.ist_wort("erste", "letzte") and self.ist_wort("element", k=1) and self.ist_wort("aus", k=2):
            pos = self.nimm().norm                       # Entferne das erste/letzte Element aus Liste.
            self.nimm()
            self.nimm()
            t = self.name(True)
            self.punkt()
            return ("liste_weg_pos", z, pos, t.norm, t.wert)
        nxt = self.peek(1)
        if self.ist_wort("element") and (nxt.art in ("ZAHL", "(") or (
                nxt.art == "WORT" and nxt.norm not in RESERVIERT and self.ist_wort("aus", k=2))):
            self.nimm()                                  # Entferne Element 2 aus Liste.
            idx = self._index("aus")
            self.erwarte_wort("aus")
            t = self.name(True)
            self.punkt()
            return ("liste_weg_pos", z, idx, t.norm, t.wert)
        wert = self.summe()
        self.erwarte_wort("aus")
        t = self.name(True)
        self.punkt()
        return ("liste_weg", z, wert, t.norm, t.wert)

    def s_kopiere(self):
        z = self.nimm().zeile
        quelle = self.summe()
        self.erwarte_wort("als")
        t = self.name(True)
        self.punkt()
        return ("kopiere", z, quelle, t.norm, t.wert)

    def s_ersetze(self):
        z = self.nimm().zeile
        alt = self.summe()
        self.erwarte_wort("durch")
        neu = self.summe()
        self.erwarte_wort("in")
        t = self.name(True)
        self.punkt()
        return ("ersetze", z, alt, neu, t.norm, t.wert)

    def s_trage(self):
        z = self.nimm().zeile
        schluessel = self.summe()
        self.erwarte_wort("mit")
        wert = self.summe()
        self.erwarte_wort("in")
        t = self.name(True)
        self.punkt()                                     # ('ein' am Satzende überliest der Lexer wie einen Artikel)
        return ("trage", z, schluessel, wert, t.norm, t.wert)

    def s_sortiere(self):
        z = self.nimm().zeile
        t = self.name(True)
        absteigend = False
        if self.ist_wort("absteigend"):
            self.nimm()
            absteigend = True
        self.punkt()
        return ("sortiere", z, t.norm, t.wert, absteigend)

    def s_warte(self):
        """Warte 1 Sekunde. · Warte 0.5 Sekunden."""
        z = self.nimm().zeile
        n = self.summe()
        if not self.ist_wort("sekunde", "sekunden"):
            self.fehler("Hier erwarte ich 'Sekunde' oder 'Sekunden' (Warte 1 Sekunde).")
        self.nimm()
        self.punkt()
        return ("warte", z, n)

    def s_loesche(self):
        """Lösche die Zeichnung."""
        z = self.nimm().zeile
        self.erwarte_wort("zeichnung", "Zeichnung")
        self.punkt()
        return ("loesche_zeichnung", z)

    # Zeichnen ------------------------------------------------------
    def s_gehe(self):
        """Gehe 50 Schritte vor. · Gehe 50 Schritte zurück. · Gehe zur Mitte."""
        z = self.nimm().zeile
        if self.ist_wort("zu"):            # "zur"/"zum" liest der Lexer als "zu"
            self.nimm()
            self.erwarte_wort("mitte", "Mitte")
            self.punkt()
            return ("mitte", z)
        weite = self.summe()
        # 'Gehe 1 Schritt vor.' soll gehen, ohne dass "Schritt" ein reserviertes Wort wird:
        # In 14_wellen.klar heißt eine Variable so. Hier wird das Wort nur an dieser einen
        # Stelle erkannt, überall sonst ist es ein gewöhnlicher Name.
        if self.ist_wort("schritt"):
            self.nimm()
        else:
            self.erwarte_wort("schritte", "Schritte")
        if self.ist_wort("zurueck"):
            self.nimm()
            rueck = True
        else:
            self.erwarte_wort("vor", "vor")
            rueck = False
        self.punkt()
        return ("gehe", z, weite, rueck)

    def s_drehe(self):
        """Drehe dich um 90 Grad nach links. · Drehe um 90 Grad nach rechts."""
        z = self.nimm().zeile
        if self.ist_wort("um"):                       # "dich" überliest schon der Lexer
            self.nimm()
        winkel = self.summe()
        self.erwarte_wort("grad", "Grad")
        if self.ist_wort("nach"):
            self.nimm()
        if self.ist_wort("links"):
            self.nimm()
            links = True
        elif self.ist_wort("rechts"):
            self.nimm()
            links = False
        else:
            self.fehler("Hier erwarte ich 'nach links' oder 'nach rechts' "
                        "(Drehe dich um 90 Grad nach links).")
        self.punkt()
        return ("drehe", z, winkel, links)

    def s_stift(self):
        """Hebe den Stift. · Senke den Stift."""
        tok = self.nimm()
        self.erwarte_wort("stift", "Stift")
        self.punkt()
        return ("stift", tok.zeile, tok.norm == "senke")

    def s_nimm(self):
        """Nimm die Farbe "rot". · Nimm die Strichstärke 3. · Nimm die Leinwand 600 mal 400."""
        z = self.nimm().zeile
        if self.ist_wort("strichstaerke"):
            self.nimm()
            breite = self.summe()
            self.punkt()
            return ("strichstaerke", z, breite)
        if self.ist_wort("leinwand"):
            self.nimm()
            # Beide Maße werden eine Ebene unterhalb des Produkts gelesen: Sonst verschluckt
            # 'mal' als Rechenzeichen die Angabe, und aus 600 mal 400 würde 240000.
            breite = self.potenz()
            self.erwarte_wort("mal", "mal (Nimm die Leinwand 600 mal 400.)")
            hoehe = self.potenz()
            self.punkt()
            return ("leinwand", z, breite, hoehe)
        self.erwarte_wort("farbe", "Farbe")
        farbe = self.summe()
        self.punkt()
        return ("farbe", z, farbe)

    # Aufgaben ------------------------------------------------------
    def s_aufgabe(self):
        z = self.nimm().zeile
        self.erwarte_wort("aufgabe", "Aufgabe")
        t = self.name()
        params = []
        if self.ist_wort("mit", "von"):
            self.nimm()
            p = self.name(True)
            params.append((p.norm, p.wert))
            while self.ist_wort("und"):
                self.nimm()
                p = self.name(True)
                params.append((p.norm, p.wert))
        self.erwarte_sym(":")
        body = self.block(z)
        self.ende()
        return ("aufgabe", z, t.norm, t.wert, params, body)

    def s_gib(self):
        z = self.nimm().zeile
        wert = self.summe()
        self.erwarte_wort("zurueck", "zurück")
        self.punkt()
        return ("gib", z, wert)

    def s_fuehre(self):
        z = self.nimm().zeile
        tok = self.peek()
        if tok.art != "WORT" or tok.norm not in self.aufgaben:
            nahe = difflib.get_close_matches(tok.norm or "", list(self.aufgaben), n=1, cutoff=0.6)
            hinweis = f" Meintest du '{nahe[0]}'?" if nahe else ""
            self.fehler(f"Diese Aufgabe kenne ich nicht: {self.beschreibe(tok)}.{hinweis} "
                        "(Sie muss mit 'Definiere Aufgabe ...' beschrieben sein.)")
        aufruf = self.aufruf()
        self.erwarte_wort("aus")
        self.punkt()
        return ("fuehre", z, aufruf)

    def aufruf(self):
        t = self.nimm()
        stelligkeit = self.aufgaben[t.norm]
        args = []
        if stelligkeit:
            if not self.ist_wort("von", "mit"):
                self.fehler(f"'{t.wert}' ist der Name einer Aufgabe und braucht {stelligkeit} Wert(e): "
                            f"{t.wert} von ... (mehrere mit 'und' trennen). Ist eine Variable gemeint? "
                            "Dann darf sie nicht genauso heißen wie die Aufgabe.", tok=t)
            self.nimm()
            for j in range(stelligkeit):
                if j:
                    self.erwarte_wort("und")
                args.append(self.argument())
            if self.ist_wort("plus", "minus", "mal", "hoch") or (self.ist_wort("geteilt") and self.ist_wort("durch", k=1)):
                nxt = self.peek()
                self.hinweise.append((nxt.zeile, nxt.spalte,
                    f"'{t.wert} von …' nimmt nur den Wert direkt dahinter; '{nxt.wert}' rechnet danach mit dem Ergebnis. "
                    f"Soll die Aufgabe mit der ganzen Rechnung arbeiten, setze Klammern: {t.wert} von (… {nxt.wert} …)."))
        return ("aufruf", t.norm, t.wert, args, t.zeile)

    # Dinge (Strukturen) -------------------------------------------
    def s_struktur(self):
        t = self.nimm()
        self.erwarte_wort("hat")
        felder = []
        f = self.name()
        felder.append((f.norm, f.wert))
        while self.ist_wort("und"):
            self.nimm()
            f = self.name()
            felder.append((f.norm, f.wert))
        self.punkt()
        return ("struktur", t.zeile, t.norm, t.wert, felder)

    def s_erschaffe(self):
        z = self.nimm().zeile
        typ = self.name()
        paare = []
        if self.ist_wort("mit"):
            self.nimm()
            while True:
                f = self.name()
                paare.append((f.norm, f.wert, self.summe()))
                if self.ist_wort("und"):
                    self.nimm()
                else:
                    break
        self.erwarte_wort("als")
        t = self.name(True)
        self.punkt()
        return ("erschaffe", z, typ.norm, typ.wert, paare, t.norm, t.wert)

    # Fehler, Dateien, Texte, Zusicherungen -------------------------
    def s_versuche(self):
        z = self.nimm().zeile
        self.erwarte_sym(":")
        body = self.block(z, ("bei", "ende"))
        if not self.ist_wort("bei"):
            self.fehler("Nach 'Versuche:' erwarte ich 'Bei Fehler:' (die Fehlerbehandlung).")
        self.nimm()
        self.erwarte_wort("fehler", "Fehler")
        self.erwarte_sym(":")
        handler = self.block(z)
        self.ende()
        return ("versuche", z, body, handler)

    def s_lies(self):
        z = self.nimm().zeile
        self.erwarte_wort("datei", "Datei")
        pfad = self.summe()
        self.erwarte_wort("als")
        t = self.name(True)
        self.punkt()
        return ("lies", z, pfad, t.norm, t.wert)

    def s_schreibe(self):
        z = self.nimm().zeile
        inhalt = self.summe()
        self.erwarte_wort("in")
        self.erwarte_wort("datei", "Datei")
        pfad = self.summe()
        self.punkt()
        return ("schreibe", z, inhalt, pfad)

    def s_verbinde(self):
        z = self.nimm().zeile
        teile = [self.summe()]
        while self.ist_wort("und"):
            self.nimm()
            teile.append(self.summe())
        self.erwarte_wort("zu")
        t = self.name(True)
        self.punkt()
        return ("verbinde", z, teile, t.norm, t.wert)

    def s_teile(self):
        z = self.nimm().zeile
        text = self.summe()
        self.erwarte_wort("bei")
        trenner = self.summe()
        self.erwarte_wort("zu")
        t = self.name(True)
        self.punkt()
        return ("teile", z, text, trenner, t.norm, t.wert)

    def s_stelle(self):
        z = self.nimm().zeile
        self.erwarte_wort("sicher", "sicher")
        if self.ist_sym(","):
            self.nimm()
        self.erwarte_wort("dass", "dass")
        bed = self.bedingung()
        self.punkt()
        return ("sicher", z, bed)

    # ── Ausdrücke ───────────────────────────────────────────────────
    def summe(self):
        l = self.produkt()
        while self.ist_wort("plus", "minus"):
            t = self.nimm()
            l = ("bin", t.norm, l, self.produkt(), t.zeile)
        return l

    def produkt(self):
        l = self.potenz()
        while True:
            if self.ist_wort("mal") and not self.ist_sym(":", k=1):   # 'Wiederhole 5 Mal:' nicht verwechseln
                t = self.nimm()
            elif self.ist_wort("geteilt") and self.ist_wort("durch", k=1):
                t = self.nimm()
                self.nimm()
            else:
                return l
            l = ("bin", t.norm, l, self.potenz(), t.zeile)

    def potenz(self):
        b = self.unaer()
        if self.ist_wort("hoch"):
            t = self.nimm()
            self._tiefer()
            try:
                return ("bin", "hoch", b, self.potenz(), t.zeile)
            finally:
                self.tiefe -= 1
        return b

    def unaer(self):
        if self.ist_wort("minus") or self.ist_sym("-"):
            t = self.nimm()
            self._tiefer()
            try:
                if t.art == "-":                       # negative Zahl: -5
                    if self.peek().art != "ZAHL":
                        self.fehler("Nach dem Minuszeichen erwarte ich eine Zahl (z. B. -5).")
                    return ("wert", -self.nimm().wert)
                return ("bin", "minus", ("wert", 0), self.unaer(), t.zeile)
            finally:
                self.tiefe -= 1
        return self.primaer()

    def _index(self, folge):
        """Nummer in 'Element Nr von Liste' bzw. 'Zeichen 2 bis Nr': ein bloßer Name ist hier nur eine Variable."""
        tok = self.peek()
        if tok.art == "WORT" and tok.norm not in RESERVIERT and self.ist_wort(folge, k=1):
            self.nimm()
            return ("var", tok.norm, tok.wert, tok.zeile)
        return self.argument()

    def argument(self):
        """Argument einer Funktion: ein einfacher Wert (sonst Klammern setzen)."""
        return self.unaer()

    def primaer(self):
        self._tiefer()
        try:
            return self._primaer_roh()
        finally:
            self.tiefe -= 1

    def _primaer_roh(self):
        tok = self.peek()
        if tok.art in ("ZAHL", "TEXT"):
            self.nimm()
            return ("wert", tok.wert)
        if tok.art == "(":
            self.nimm()
            e = self.summe()
            self.erwarte_sym(")")
            return e
        if tok.art != "WORT":
            self.fehler(f"Hier erwarte ich einen Wert (Zahl, Text oder Name), gefunden habe ich aber "
                        f"{self.beschreibe(tok)}.")
        n, z = tok.norm, tok.zeile
        if n in ("aktuelle", "aktueller", "aktuelles", "aktuellen"):
            # "die aktuelle Stunde", "die aktuelle Minute" … – der Wert kommt von der Uhr des Rechners.
            teile = {"stunde": "stunde", "minute": "minute", "sekunde": "sekunde",
                     "tag": "tag", "monat": "monat", "jahr": "jahr"}
            naechstes = self.peek(1)
            if naechstes.art != "WORT" or naechstes.norm not in teile:
                self.fehler("Nach 'aktuelle' erwarte ich Stunde, Minute, Sekunde, Tag, Monat oder Jahr "
                            "(Merke die aktuelle Stunde als h).")
            self.nimm(); self.nimm()
            return ("jetzt", teile[naechstes.norm], z)
        if n == "wahr":
            self.nimm(); return ("wert", True)
        if n == "falsch":
            self.nimm(); return ("wert", False)
        if self.ist_wort("von", k=1):
            if n == "zufallszahl":
                self.nimm(); self.nimm()
                a = self.argument()
                self.erwarte_wort("bis")
                return ("zufall", a, self.argument(), z)
            if n in ("abgerundet", "aufgerundet", "gerundet"):
                self.nimm(); self.nimm()
                a = self.argument()
                stellen = None
                if n == "gerundet" and self.ist_wort("auf") and self.ist_wort("stellen", k=2):
                    self.nimm()                          # Gerundet von x auf 2 Stellen
                    stellen = self.argument()
                    self.nimm()
                return (n, a, z, stellen)
            if n == "verkettet":
                self.nimm(); self.nimm()
                a = self.argument()
                self.erwarte_wort("mit")
                return ("verkettet", a, self.argument(), z)
            if n == "zahlenwert":
                self.nimm(); self.nimm()
                return ("zahlenwert", self.argument(), z)
            if n in ("rechtsbuendig", "linksbuendig"):
                # "Rechtsbündig von Wert auf 8 Zeichen" – für Tabellen, die untereinander stehen.
                self.nimm(); self.nimm()
                a = self.argument()
                self.erwarte_wort("auf")
                breite = self.argument()
                self.erwarte_wort("zeichen", "Zeichen")
                return (n, a, breite, z)
            if n == "formatiert":
                self.nimm(); self.nimm()
                a = self.argument()
                self.erwarte_wort("auf")
                stellen = self.argument()
                self.erwarte_wort("stellen", "Stellen")
                return ("formatiert", a, stellen, z)
            if n in ("laenge", "wurzel", "betrag", "kleinbuchstaben", "grossbuchstaben",
                     "sinus", "kosinus", "cosinus", "tangens",
                     "arkussinus", "arkuskosinus", "arkuscosinus", "arkustangens"):
                self.nimm(); self.nimm()
                return (n, self.argument(), z)
            if n == "rest":
                self.nimm(); self.nimm()
                a = self.potenz()
                self.erwarte_wort("geteilt", "geteilt durch")
                self.erwarte_wort("durch")
                return ("rest", a, self.potenz(), z)
        if n in ("zufaelliges", "zufaellige") and self.ist_wort("element", k=1) and self.ist_wort("von", k=2):
            self.nimm(); self.nimm(); self.nimm()
            return ("zufallselement", self.argument(), z)
        if n == "wert" and self.ist_wort("fuer", k=1):        # Wert für "Apfel" in Preise
            self.nimm(); self.nimm()
            schluessel = self._index("in")
            self.erwarte_wort("in")
            return ("tabellenwert", schluessel, self.argument(), z)
        if n in ("zeichen", "elemente"):                      # Zeichen 2 bis 4 von Wort
            nxt = self.peek(1)
            if nxt.art in ("ZAHL", "(") or (nxt.art == "WORT" and nxt.norm not in RESERVIERT
                                             and self.ist_wort("bis", k=2)):
                self.nimm()
                von = self._index("bis")
                self.erwarte_wort("bis")
                bis = self._index("von")
                self.erwarte_wort("von")
                return ("ausschnitt", n, von, bis, self.argument(), z)
        if n in ("erste", "letzte") and self.ist_wort("element", k=1):
            self.nimm(); self.nimm()
            self.erwarte_wort("von")
            return ("pos", n, self.argument(), z)
        if n == "element":
            nxt = self.peek(1)
            if nxt.art in ("ZAHL", "(") or (nxt.art == "WORT" and nxt.norm not in RESERVIERT
                                             and self.ist_wort("von", k=2)):
                self.nimm()                              # Element 2 von Liste  /  Element Nr von Liste
                idx = self._index("von")
                self.erwarte_wort("von")
                return ("element", idx, self.argument(), z)
        if n in self.aufgaben:
            return self.aufruf()
        if n in RESERVIERT:
            self.fehler(f"Hier erwarte ich einen Wert, gefunden habe ich aber das Schlüsselwort '{tok.wert}'.")
        self.nimm()
        if self.ist_wort("von"):                       # Feld von Objekt
            self.nimm()
            return ("feld", n, tok.wert, self.argument(), z)
        return ("var", n, tok.wert, z)
