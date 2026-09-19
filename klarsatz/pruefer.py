"""Prüfmodus: findet Fehler und Auffälligkeiten, ohne das Programm auszuführen.

Was geprüft wird (Schwere in Klammern):
  * Namen, die nirgends angelegt werden – mit „Meintest du …?“ (Fehler)
  * Benutzung vor dem Anlegen, Änderung von Konstanten (Warnung / Fehler)
  * 'Gib … zurück' außerhalb einer Aufgabe, 'Höre auf' / 'Mach weiter' außerhalb einer Schleife (Fehler)
  * unbekannte Dinge, fehlende oder überflüssige Felder, unbekannte Felder (Fehler)
  * Endlosschleifen-Verdacht, Schleifen die nie laufen, unerreichbarer Code (Warnung)
  * Aufgaben ohne 'Gib … zurück', die als Wert benutzt werden; Rekursion ohne 'Wenn' (Warnung)
  * Division durch 0, Rechnen mit Text, Element 0 (Warnung)
  * lokale Variable verdeckt eine globale (Warnung)
  * unbenutzte Variablen, Parameter und Aufgaben, leere Blöcke, immer wahre Bedingungen (Hinweis)
"""
import difflib
from dataclasses import dataclass

from .fehler import SyntaxFehler, _quellzeile
from .lexer import lexer
from .parser import Parser
from .werte import passt

SCHWERE = {"Fehler": 0, "Warnung": 1, "Hinweis": 2}


@dataclass
class Befund:
    schwere: str                # "Fehler", "Warnung" oder "Hinweis"
    zeile: int
    meldung: str
    spalte: int | None = None
    laenge: int | None = None
    code: str = ""              # kurze Kennung, z. B. "unbekannter-name"


# Wo steht die Zeilennummer im Knoten?
ZEILENPOS = {"var": 3, "bin": 4, "aufruf": 4, "feld": 4, "laenge": 2, "wurzel": 2, "betrag": 2,
             "kleinbuchstaben": 2, "grossbuchstaben": 2, "rest": 3, "pos": 3, "element": 3, "zufall": 3,
             "abgerundet": 2, "aufgerundet": 2, "gerundet": 2, "formatiert": 3, "verkettet": 3,
             "zahlenwert": 2, "zufallselement": 2, "tabellenwert": 3, "ausschnitt": 5, "vgl": 4,
             "wahrheit": 2, "typ": 3}


@dataclass(frozen=True)
class Kontext:
    loops: tuple = ()           # Zeilen der umgebenden Schleifen
    func: str | None = None     # Name (norm) der umgebenden Aufgabe
    tiefe: int = 0              # Schleifentiefe innerhalb von Programm bzw. Aufgabe

    def schleife(self, zeile):
        return Kontext(self.loops + (zeile,), self.func, self.tiefe + 1)


class Bereich:
    def __init__(self, ist_aufgabe=False, anzeige=""):
        self.ist_aufgabe = ist_aufgabe
        self.anzeige = anzeige
        self.defs = {}            # norm -> [(zeile, art, loops, konstant)]
        self.namen = {}           # norm -> Anzeigename
        self.nutzungen = []       # (norm, anz, zeile, loops, art)  art: "lese" | "schreibe"
        self.zuweisungen = {}     # norm -> [zeile]  (Setze/Erhöhe …)


class _Info:
    def __init__(self):
        self.namen = set()        # in der Schleife veränderte Namen
        self.abbruch = False      # 'Höre auf' auf dieser Schleifenebene
        self.gib = False
        self.aufruf = False


def _ist_wert(node, typ=None):
    return isinstance(node, tuple) and node and node[0] == "wert" and (
        typ is None or (isinstance(node[1], typ) and not isinstance(node[1], bool)))


def _null(node):
    return _ist_wert(node) and node[1] is not True and node[1] is not False and node[1] == 0 \
        and not isinstance(node[1], str)


class Pruefer:
    def __init__(self, programm, hinweise=()):
        self.programm = programm
        self.parser_hinweise = list(hinweise)
        self.befunde = []
        self.aufgaben = {}        # norm -> dict(anz, zeile, params, hat_gib, hat_wenn)
        self.strukturen = {}      # norm -> (anz, felder, zeile)
        self.feldnamen = {}       # norm -> Anzeige
        self.aufgerufen = set()
        self.aufrufer = {}        # norm der Aufgabe -> {norm der aufgerufenen}
        self.wert_aufrufe = []
        self.glob = Bereich()
        self.aufgabenbereiche = []   # [(norm, Bereich)]

    # ── Ausgabe ─────────────────────────────────────────────────────
    def melde(self, schwere, zeile, meldung, code="", spalte=None, laenge=None):
        b = Befund(schwere, zeile or 0, meldung, spalte, laenge, code)
        if not any(x.schwere == b.schwere and x.zeile == b.zeile and x.meldung == b.meldung for x in self.befunde):
            self.befunde.append(b)

    # ── Hilfen zum Durchsuchen des Syntaxbaums ───────────────────────
    @staticmethod
    def _bloecke(node):
        """Untergeordnete Blöcke eines Satzes: [(Anweisungen, ist_schleife)]."""
        tag = node[0]
        if tag == "wenn":
            return [(body, False) for _, body in node[2]] + ([(node[3], False)] if node[3] is not None else [])
        if tag in ("wiederhole_n", "solange"):
            return [(node[3], True)]
        if tag == "zaehle":
            return [(node[6], True)]
        if tag == "fuer":
            return [(node[5], True)]
        if tag == "versuche":
            return [(node[2], False), (node[3], False)]
        if tag == "aufgabe":
            return [(node[5], False)]
        return []

    @staticmethod
    def _ausdruecke_von(node):
        """Ausdrücke und Bedingungen eines Satzes (ohne die Blöcke darin)."""
        tag = node[0]
        if tag == "zeige" or tag == "verbinde":
            return list(node[2])
        if tag in ("frage", "merke", "wiederhole_n", "solange", "liste_add", "liste_weg", "kopiere", "gib",
                   "fuehre", "lies", "sicher"):
            return [node[2]]
        if tag == "setze":
            return [node[2], node[3]]
        if tag == "aendere":
            return [node[2], node[4]]
        if tag == "wenn":
            return [bed for bed, _ in node[2]]
        if tag == "zaehle":
            return [x for x in (node[2], node[3], node[4]) if x is not None]
        if tag == "fuer":
            return [node[4]]
        if tag == "liste_neu":
            return list(node[4])
        if tag == "tabelle_neu":
            return [x for paar in node[4] for x in paar]
        if tag == "liste_weg_pos":
            return [node[2]] if isinstance(node[2], tuple) else []
        if tag == "ersetze":
            return [node[2], node[3]]
        if tag == "trage":
            return [node[2], node[3]]
        if tag == "erschaffe":
            return [e for _, _, e in node[4]]
        if tag == "schreibe":
            return [node[2], node[3]]
        if tag == "teile":
            return [node[2], node[3]]
        return []

    def _alle(self, stmts, in_aufgaben=True):
        for node in stmts:
            yield node
            if node[0] == "aufgabe" and not in_aufgaben:
                continue
            for block, _ in self._bloecke(node):
                yield from self._alle(block, in_aufgaben)

    @classmethod
    def _scan(cls, node, namen, aufrufe):
        """Sammelt die gelesenen Namen eines Ausdrucks; merkt sich, ob eine Aufgabe aufgerufen wird."""
        if not isinstance(node, tuple) or not node or not isinstance(node[0], str):
            return
        if node[0] == "var":
            namen.add(node[1])
        elif node[0] == "aufruf":
            aufrufe.append(node)
        for kind in node[1:]:
            if isinstance(kind, tuple):
                cls._scan(kind, namen, aufrufe)
            elif isinstance(kind, list):
                for k in kind:
                    cls._scan(k, namen, aufrufe)

    @staticmethod
    def _geschrieben(node):
        """Namen, die dieser Satz anlegt oder verändert."""
        tag = node[0]
        if tag in ("merke", "frage"):
            return [node[3]]
        if tag in ("setze", "aendere"):
            ziel = node[2]
            if ziel[0] == "var":
                return [ziel[1]]
            if ziel[0] == "feld" and ziel[3][0] == "var":
                return [ziel[3][1]]
            return []
        if tag == "zaehle":
            return [node[5][0]] if node[5] else []
        if tag == "fuer":
            return [node[2]]
        if tag in ("liste_neu", "tabelle_neu"):
            return [node[2]]
        if tag in ("liste_add", "liste_weg"):
            return [node[3]]
        if tag in ("liste_weg_pos", "sortiere", "kopiere"):
            return [node[3]] if tag != "sortiere" else [node[2]]
        if tag == "ersetze":
            return [node[4]]
        if tag == "trage":
            return [node[4]]
        if tag == "verbinde" or tag == "lies":
            return [node[3]]
        if tag == "teile":
            return [node[4]]
        if tag == "erschaffe":
            return [node[5]]
        if tag == "versuche":
            return ["fehlermeldung"]
        return []

    def _info(self, stmts, in_schleife=False, info=None):
        info = info or _Info()
        for node in stmts:
            tag = node[0]
            if tag == "abbruch" and not in_schleife:
                info.abbruch = True
            if tag == "gib":
                info.gib = True
            info.namen.update(self._geschrieben(node))
            for e in self._ausdruecke_von(node):
                aufrufe = []
                self._scan(e, set(), aufrufe)
                if aufrufe:
                    info.aufruf = True
            for block, ist_schleife in self._bloecke(node):
                if node[0] != "aufgabe":
                    self._info(block, in_schleife or ist_schleife, info)
        return info

    def _terminal(self, node):
        tag = node[0]
        if tag in ("gib", "abbruch", "weiter"):
            return True
        if tag == "wenn" and node[3] is not None:
            return all(self._endet(body) for _, body in node[2]) and self._endet(node[3])
        return False

    def _endet(self, stmts):
        return bool(stmts) and self._terminal(stmts[-1])

    # ── Durchgang 1: Aufgaben und Dinge einsammeln ──────────────────
    def _registriere(self):
        for node in self._alle(self.programm):
            if node[0] == "aufgabe":
                _, z, n, anz, params, body = node
                if n in self.aufgaben:
                    self.melde("Warnung", z, f"Die Aufgabe '{anz}' ist schon in Zeile {self.aufgaben[n]['zeile']} "
                               "definiert – die spätere überschreibt die frühere.", "doppelte-aufgabe")
                inhalt = list(self._alle(body, in_aufgaben=False))
                self.aufgaben[n] = dict(anz=anz, zeile=z, params=params,
                                        hat_gib=any(s[0] == "gib" for s in inhalt),
                                        hat_wenn=any(s[0] == "wenn" for s in inhalt))
            elif node[0] == "struktur":
                _, z, n, anz, felder = node
                if n in self.strukturen:
                    self.melde("Warnung", z, f"Das Ding '{anz}' ist schon in Zeile {self.strukturen[n][2]} "
                               "beschrieben.", "doppeltes-ding")
                self.strukturen[n] = (anz, felder, z)
                for fn, fa in felder:
                    self.feldnamen.setdefault(fn, fa)

    # ── Durchgang 2: Bereiche und Nutzungen ─────────────────────────
    def _def(self, bereich, n, anz, z, art, ctx, konstant=False):
        bereich.defs.setdefault(n, []).append((z, art, ctx.loops, konstant))
        bereich.namen.setdefault(n, anz)

    def _nutzung(self, bereich, n, anz, z, ctx, art="lese"):
        bereich.nutzungen.append((n, anz, z, ctx.loops, art))
        bereich.namen.setdefault(n, anz)
        if art == "schreibe":
            bereich.zuweisungen.setdefault(n, []).append(z)

    def _block(self, stmts, bereich, ctx):
        gemeldet = False
        for i, node in enumerate(stmts):
            self._satz(node, bereich, ctx)
            if not gemeldet and i + 1 < len(stmts) and self._terminal(node):
                self.melde("Warnung", stmts[i + 1][1], "Dieser Satz wird nie erreicht, weil davor "
                           "'Gib … zurück', 'Höre auf' oder 'Mach weiter' alles beendet.", "unerreichbar")
                gemeldet = True

    def _leer(self, body, z, was):
        if not body:
            self.melde("Hinweis", z, f"{was} ist leer.", "leerer-block")

    def _satz(self, node, b, ctx):
        tag, z = node[0], node[1]
        ausdruck = lambda e: self._ausdruck(e, b, ctx, z)          # noqa: E731

        if tag == "zeige":
            for e in node[2]:
                ausdruck(e)
        elif tag == "frage":
            ausdruck(node[2])
            self._def(b, node[3], node[4], z, "frage", ctx)
        elif tag == "merke":
            ausdruck(node[2])
            self._def(b, node[3], node[4], z, "merke", ctx, konstant=node[5])
        elif tag == "setze":
            ausdruck(node[3])
            self._ziel(node[2], b, ctx, z, lesen=False)
        elif tag == "aendere":
            ausdruck(node[4])
            self._ziel(node[2], b, ctx, z, lesen=True)
        elif tag == "wenn":
            for bed, body in node[2]:
                ausdruck(bed)
                self._konstante_bedingung(bed, z)
                self._leer(body, z, "Dieser Zweig")
                self._block(body, b, ctx)
            if node[3] is not None:
                self._leer(node[3], z, "Der Sonst-Zweig")
                self._block(node[3], b, ctx)
        elif tag == "wiederhole_n":
            ausdruck(node[2])
            if _ist_wert(node[2], (int, float)) and node[2][1] < 0:
                self.melde("Warnung", z, "Negativ oft wiederholen geht nicht.", "negative-wiederholung")
            self._leer(node[3], z, "Diese Schleife")
            self._block(node[3], b, ctx.schleife(z))
        elif tag == "solange":
            ausdruck(node[2])                                    # Bedingung wird vor jedem Durchlauf geprüft
            self._leer(node[3], z, "Diese Schleife")
            self._block(node[3], b, ctx.schleife(z))
            self._endlosschleife(node)
        elif tag == "zaehle":
            _, _, ka, kb, ks, var, body, rueck = node
            for e in (ka, kb, ks):
                if e is not None:
                    ausdruck(e)
            if _ist_wert(ka, (int, float)) and _ist_wert(kb, (int, float)) and ks is None:
                if not rueck and ka[1] > kb[1]:
                    self.melde("Warnung", z, f"Diese Schleife läuft nie: von {ka[1]} bis {kb[1]} zählt nur aufwärts. "
                               "Abwärts zählt man mit 'rückwärts'.", "schleife-laeuft-nie")
                if rueck and ka[1] < kb[1]:
                    self.melde("Warnung", z, f"Diese Schleife läuft nie: 'rückwärts' von {ka[1]} bis {kb[1]} geht nicht.",
                               "schleife-laeuft-nie")
            ctx2 = ctx.schleife(z)
            if var:
                self._def(b, var[0], var[1], z, "schleife", ctx2)
            self._leer(body, z, "Diese Schleife")
            self._block(body, b, ctx2)
        elif tag == "fuer":
            ausdruck(node[4])
            ctx2 = ctx.schleife(z)
            self._def(b, node[2], node[3], z, "schleife", ctx2)
            self._leer(node[5], z, "Diese Schleife")
            self._block(node[5], b, ctx2)
        elif tag in ("abbruch", "weiter"):
            if ctx.tiefe == 0:
                wort = "Höre auf" if tag == "abbruch" else "Mach weiter"
                self.melde("Fehler", z, f"'{wort}' gibt es nur innerhalb einer Schleife.", "ausserhalb-schleife")
        elif tag == "liste_neu":
            for e in node[4]:
                ausdruck(e)
            self._def(b, node[2], node[3], z, "liste", ctx)
        elif tag == "tabelle_neu":
            for k, v in node[4]:
                ausdruck(k)
                ausdruck(v)
            self._def(b, node[2], node[3], z, "liste", ctx)
        elif tag in ("liste_add", "liste_weg"):
            ausdruck(node[2])
            self._nutzung(b, node[3], node[4], z, ctx)
        elif tag == "liste_weg_pos":
            if isinstance(node[2], tuple):
                ausdruck(node[2])
            self._nutzung(b, node[3], node[4], z, ctx)
        elif tag == "sortiere":
            self._nutzung(b, node[2], node[3], z, ctx)
        elif tag == "kopiere":
            ausdruck(node[2])
            self._def(b, node[3], node[4], z, "kopiere", ctx)
        elif tag == "ersetze":
            ausdruck(node[2])
            ausdruck(node[3])
            self._nutzung(b, node[4], node[5], z, ctx)
            self._nutzung(b, node[4], node[5], z, ctx, "schreibe")
        elif tag == "trage":
            ausdruck(node[2])
            ausdruck(node[3])
            self._nutzung(b, node[4], node[5], z, ctx)
        elif tag == "aufgabe":
            _, _, n, anz, params, body = node
            f = Bereich(ist_aufgabe=True, anzeige=anz)
            for pn, pa in params:
                self._def(f, pn, pa, z, "param", Kontext())
            self.aufgabenbereiche.append((n, f))
            self._leer(body, z, f"Die Aufgabe '{anz}'")
            self._block(body, f, Kontext(func=n))
        elif tag == "gib":
            if ctx.func is None:
                self.melde("Fehler", z, "'Gib … zurück' gibt es nur innerhalb einer Aufgabe.", "gib-ausserhalb")
            ausdruck(node[2])
        elif tag == "fuehre":
            self._aufruf(node[2], b, ctx, als_wert=False)
        elif tag == "struktur":
            pass
        elif tag == "erschaffe":
            self._erschaffe(node, b, ctx)
        elif tag == "versuche":
            self._leer(node[2], z, "Der Versuche-Block")
            self._block(node[2], b, ctx)
            self._def(b, "fehlermeldung", "Fehlermeldung", z, "auto", ctx)
            self._block(node[3], b, ctx)
        elif tag == "lies":
            ausdruck(node[2])
            self._def(b, node[3], node[4], z, "lies", ctx)
        elif tag == "schreibe":
            ausdruck(node[2])
            ausdruck(node[3])
        elif tag == "verbinde":
            for e in node[2]:
                ausdruck(e)
            self._def(b, node[3], node[4], z, "verbinde", ctx)
        elif tag == "teile":
            ausdruck(node[2])
            ausdruck(node[3])
            self._def(b, node[4], node[5], z, "teile", ctx)
        elif tag == "sicher":
            ausdruck(node[2])
        # Zeichnen, Zeit und Takt: Diese Sätze legen nichts an, benutzen aber Werte —
        # ohne diesen Zweig hielte der Prüfer die darin gelesenen Namen für unbenutzt.
        elif tag in ("gehe", "drehe", "farbe", "strichstaerke", "warte", "wiederholung"):
            ausdruck(node[2])
        elif tag in ("stift", "mitte", "loesche_zeichnung"):
            pass

    def _ziel(self, ziel, b, ctx, z, lesen):
        if ziel[0] == "var":
            self._nutzung(b, ziel[1], ziel[2], ziel[3], ctx, "lese" if lesen else "schreibe")
            if lesen:
                self._nutzung(b, ziel[1], ziel[2], ziel[3], ctx, "schreibe")
        else:
            self._ausdruck(ziel, b, ctx, z)

    def _erschaffe(self, node, b, ctx):
        _, z, tn, tanz, paare, n, anz = node
        for _, _, e in paare:
            self._ausdruck(e, b, ctx, z)
        self._def(b, n, anz, z, "erschaffe", ctx)
        if tn not in self.strukturen:
            nahe = difflib.get_close_matches(tn, list(self.strukturen), n=1, cutoff=0.6)
            hinweis = f" Meintest du '{self.strukturen[nahe[0]][0]}'?" if nahe else \
                f" Beschreibe es zuerst, z. B.: Ein {tanz} hat einen Namen und ein Alter."
            self.melde("Fehler", z, f"Ich kenne kein Ding namens '{tanz}'.{hinweis}", "unbekanntes-ding")
            return
        anz2, felder, _ = self.strukturen[tn]
        gegeben = set()
        for fn, fa, _ in paare:
            ziel = next((f for f in felder if passt(f[0], fn)), None)
            if ziel is None:
                self.melde("Fehler", z, f"Ein {anz2} hat kein Feld '{fa}'. Vorhanden: "
                           f"{', '.join(f[1] for f in felder)}.", "unbekanntes-feld")
            else:
                gegeben.add(ziel[0])
        fehlend = [f[1] for f in felder if f[0] not in gegeben]
        if fehlend and not any(next((f for f in felder if passt(f[0], fn)), None) is None for fn, _, _ in paare):
            self.melde("Fehler", z, f"Beim Erschaffen von {anz2} fehlt noch: {', '.join(fehlend)}.", "fehlendes-feld")

    def _aufruf(self, node, b, ctx, als_wert):
        _, n, anz, args, z = node
        self.aufgerufen.add(n)
        if ctx.func:
            self.aufrufer.setdefault(ctx.func, set()).add(n)
        if als_wert:
            self.wert_aufrufe.append((n, anz, z))
        for a in args:
            self._ausdruck(a, b, ctx, z)

    def _feld(self, node, z):
        _, fn, fa, _, zz = node
        if not any(passt(f, fn) for f in self.feldnamen):
            pool = {**{k: v for k, v in self.feldnamen.items()},
                    **{k: v["anz"] for k, v in self.aufgaben.items()}}
            nahe = difflib.get_close_matches(fn, list(pool), n=1, cutoff=0.6)
            hinweis = f" Meintest du '{pool[nahe[0]]}'?" if nahe else ""
            self.melde("Fehler", zz or z, f"'{fa} von …' – weder ein Ding hat ein Feld '{fa}', "
                       f"noch gibt es eine Aufgabe '{fa}'.{hinweis}", "unbekanntes-feld")

    def _ausdruck(self, node, b, ctx, z):
        if not isinstance(node, tuple) or not node or not isinstance(node[0], str):
            return
        art = node[0]
        pos = ZEILENPOS.get(art)
        zz = node[pos] if pos and pos < len(node) and isinstance(node[pos], int) else z
        if art == "wert":
            return
        if art == "var":
            self._nutzung(b, node[1], node[2], node[3], ctx)
            return
        if art == "aufruf":
            self._aufruf(node, b, ctx, als_wert=True)
            return
        if art == "feld":
            self._feld(node, z)
        elif art == "bin":
            _, op, a, c = node[:4]
            if op != "hoch" or True:
                if _ist_wert(a, str) or _ist_wert(c, str):
                    self.melde("Warnung", zz, f"Mit Text kann man nicht rechnen ('{op}'). Texte verbindest du mit "
                               "'Verbinde … zu …'.", "rechnen-mit-text")
            if op == "geteilt" and _null(c):
                self.melde("Warnung", zz, "Hier wird durch 0 geteilt – das ergibt immer einen Fehler.", "division-durch-null")
        elif art == "rest" and _null(node[2]):
            self.melde("Warnung", zz, "Hier wird durch 0 geteilt – das ergibt immer einen Fehler.", "division-durch-null")
        elif art == "vgl" and node[1] == "teilbar" and _null(node[3]):
            self.melde("Warnung", zz, "'teilbar' durch 0 ergibt immer einen Fehler.", "division-durch-null")
        elif art == "element" and _ist_wert(node[1], (int, float)) and node[1][1] <= 0:
            self.melde("Warnung", zz, f"Element {node[1][1]} gibt es nie – gezählt wird ab 1.", "element-null")
        elif art == "ausschnitt":
            for x in (node[2], node[3]):
                if _ist_wert(x, (int, float)) and x[1] <= 0:
                    self.melde("Warnung", zz, f"Die Nummer {x[1]} gibt es nie – gezählt wird ab 1.", "element-null")
        elif art == "zufall" and _ist_wert(node[1], int) and _ist_wert(node[2], int) and node[1][1] > node[2][1]:
            self.melde("Warnung", zz, f"Zufallszahl von {node[1][1]} bis {node[2][1]} geht nicht: "
                       "die erste Zahl darf nicht größer sein.", "zufall-grenzen")
        for kind in node[1:]:
            if isinstance(kind, tuple):
                self._ausdruck(kind, b, ctx, z)
            elif isinstance(kind, list):
                for k in kind:
                    self._ausdruck(k, b, ctx, z)

    def _konstante_bedingung(self, bed, z):
        if bed[0] == "wahrheit" and _ist_wert(bed[1]) and isinstance(bed[1][1], bool):
            self.melde("Hinweis", z, f"Diese Bedingung ist immer {'wahr' if bed[1][1] else 'falsch'}.", "konstante-bedingung")
        elif bed[0] == "vgl" and _ist_wert(bed[2]) and _ist_wert(bed[3]):
            self.melde("Hinweis", z, "Hier werden zwei feste Werte verglichen – das Ergebnis steht schon fest.",
                       "konstante-bedingung")

    @staticmethod
    def _wartet(knoten):
        """Steckt irgendwo in diesem Baumstück ein 'Warte'? Dann ist eine Dauerschleife
        Absicht (Uhr, laufende Anzeige) und keine vergessene Abbruchbedingung."""
        if isinstance(knoten, tuple):
            if knoten and knoten[0] == "warte":
                return True
            return any(Pruefer._wartet(teil) for teil in knoten)
        if isinstance(knoten, list):
            return any(Pruefer._wartet(teil) for teil in knoten)
        return False

    def _endlosschleife(self, node):
        _, z, bed, body = node
        info = self._info(body)
        if info.abbruch or info.gib:
            return
        if self._wartet(body):
            # Eine Schleife, die regelmäßig wartet, läuft absichtlich weiter — so entstehen
            # Uhren und laufende Anzeigen. Kein Grund zur Warnung.
            return
        if bed[0] == "wahrheit" and _ist_wert(bed[1]) and isinstance(bed[1][1], bool):
            if bed[1][1]:
                self.melde("Warnung", z, "Endlosschleife: Die Bedingung ist immer wahr, und in der Schleife gibt es "
                           "weder 'Höre auf' noch 'Gib … zurück'.", "endlosschleife")
            else:
                self.melde("Warnung", z, "Diese Schleife läuft nie: Die Bedingung ist immer falsch.", "schleife-laeuft-nie")
            return
        namen, aufrufe = set(), []
        self._scan(bed, namen, aufrufe)
        if aufrufe or info.aufruf:
            return                                              # Aufgaben könnten globale Werte ändern
        if not namen:
            self.melde("Warnung", z, "Endlosschleife? Die Bedingung besteht nur aus festen Werten und ändert sich nie.",
                       "endlosschleife")
        elif not namen & info.namen:
            liste = ", ".join(sorted(namen))
            self.melde("Warnung", z, f"Endlosschleife? Die Bedingung hängt nur von {liste} ab, und das wird in der "
                       "Schleife nie verändert (auch kein 'Höre auf').", "endlosschleife")

    # ── Abschluss: Auswertungen über das ganze Programm ─────────────
    def _alle_bereiche(self):
        return [self.glob] + [f for _, f in self.aufgabenbereiche]

    def _namen_pruefen(self):
        for bereich in self._alle_bereiche():
            sichtbar = set(bereich.defs)
            if bereich.ist_aufgabe:
                sichtbar |= set(self.glob.defs)
            anzeige = {}
            for n in sichtbar:
                anzeige[n] = bereich.namen.get(n) or self.glob.namen.get(n) or n
            for n, anz, z, _, art in bereich.nutzungen:
                if n in sichtbar:
                    continue
                nahe = difflib.get_close_matches(n, list(sichtbar - {"fehlermeldung"}), n=1, cutoff=0.6)
                hinweis = f" Meintest du '{anzeige[nahe[0]]}'?" if nahe else ""
                if art == "schreibe":
                    text = f"Ich kenne '{anz}' nicht. Lege es zuerst mit 'Merke … als {anz}.' an.{hinweis}"
                else:
                    text = f"Ich kenne '{anz}' nicht – es wird nirgends angelegt.{hinweis}"
                if bereich.ist_aufgabe:
                    text += f" (in der Aufgabe „{bereich.anzeige}“)"
                self.melde("Fehler", z, text, "unbekannter-name")

    def _reihenfolge(self):
        for bereich in self._alle_bereiche():
            gemeldet = set()
            for n, anz, z, loops, art in bereich.nutzungen:
                if art != "lese" or n in gemeldet or n not in bereich.defs:
                    continue
                defs = bereich.defs[n]
                if any(d[1] in ("param", "auto") for d in defs):
                    continue
                if bereich.ist_aufgabe and n in self.glob.defs:
                    continue
                erste = min(defs, key=lambda d: d[0])
                if z < erste[0] and not (set(loops) & set(erste[2])):
                    self.melde("Warnung", z, f"'{anz}' wird hier benutzt, aber erst in Zeile {erste[0]} angelegt.",
                               "benutzt-vor-anlegen")
                    gemeldet.add(n)

    def _unbenutzt(self):
        gelesen_global = {n for n, _, _, _, art in self.glob.nutzungen if art == "lese"}
        for _, f in self.aufgabenbereiche:
            gelesen_global |= {n for n, _, _, _, art in f.nutzungen if art == "lese" and n not in f.defs}
        for bereich in self._alle_bereiche():
            gelesen = {n for n, _, _, _, art in bereich.nutzungen if art == "lese"}
            for n, defs in bereich.defs.items():
                art = defs[0][1]
                if art in ("schleife", "auto"):
                    continue
                benutzt = (n in gelesen_global) if not bereich.ist_aufgabe else (n in gelesen)
                if benutzt:
                    continue
                anz = bereich.namen.get(n, n)
                if art == "param":
                    self.melde("Hinweis", defs[0][0], f"Der Wert '{anz}' der Aufgabe „{bereich.anzeige}“ wird nie benutzt.",
                               "unbenutzter-parameter")
                else:
                    self.melde("Hinweis", defs[0][0], f"'{anz}' wird angelegt, aber nie gelesen.", "unbenutzte-variable")

    def _konstanten(self):
        for bereich in self._alle_bereiche():
            for n, defs in bereich.defs.items():
                konst = [d for d in defs if d[3]]
                if not konst:
                    continue
                anz = bereich.namen.get(n, n)
                if konst[0][2]:
                    self.melde("Warnung", konst[0][0], f"'Merke für immer … als {anz}' steht in einer Schleife: "
                               "ab dem zweiten Durchlauf ist das ein Fehler, denn eine Konstante lässt sich "
                               "nicht neu anlegen.", "konstante-in-schleife")
                for d in defs:
                    if not d[3]:
                        self.melde("Fehler", d[0], f"'{anz}' ist eine Konstante ('für immer') und lässt sich "
                                   "nicht ändern.", "konstante-aendern")
                for z in bereich.zuweisungen.get(n, []):
                    self.melde("Fehler", z, f"'{anz}' ist eine Konstante ('für immer') und lässt sich nicht "
                               "ändern.", "konstante-aendern")
                for d in konst[1:]:
                    self.melde("Fehler", d[0], f"Die Konstante '{anz}' wird ein zweites Mal angelegt.", "konstante-aendern")

    def _aufgaben_auswerten(self):
        for n, a in self.aufgaben.items():
            if n not in self.aufgerufen:
                self.melde("Hinweis", a["zeile"], f"Die Aufgabe '{a['anz']}' wird nie aufgerufen.", "unbenutzte-aufgabe")
            if n in self.aufrufer.get(n, set()) and not a["hat_wenn"]:
                self.melde("Warnung", a["zeile"], f"Die Aufgabe '{a['anz']}' ruft sich selbst auf, hat aber kein 'Wenn' "
                           "als Abbruchbedingung – das endet nie.", "endlose-rekursion")
        for n, anz, z in self.wert_aufrufe:
            a = self.aufgaben.get(n)
            if a and not a["hat_gib"]:
                self.melde("Warnung", z, f"Die Aufgabe '{anz}' hat kein 'Gib … zurück', wird hier aber als Wert benutzt.",
                           "aufgabe-ohne-rueckgabe")

    def _lokale_schatten(self):
        for n_f, f in self.aufgabenbereiche:
            for n, defs in f.defs.items():
                if n not in self.glob.defs or any(d[1] in ("param", "auto") for d in defs):
                    continue
                lokal = [d for d in defs if d[1] == "merke"]
                if not lokal:
                    continue
                erste = min(d[0] for d in lokal)
                if any(art == "lese" and nn == n and z <= erste for nn, _, z, _, art in f.nutzungen):
                    anz = f.namen.get(n, n)
                    self.melde("Warnung", erste, f"'Merke … als {anz}' legt in der Aufgabe „{f.anzeige}“ eine eigene, lokale "
                               f"Variable an – das globale '{anz}' bleibt unverändert. Zum Ändern des globalen Werts "
                               f"nimm 'Setze {anz} auf …'.", "lokale-verdeckt-globale")

    def analysiere(self):
        self._registriere()
        self._block(self.programm, self.glob, Kontext())
        self._namen_pruefen()
        self._reihenfolge()
        self._unbenutzt()
        self._konstanten()
        self._aufgaben_auswerten()
        self._lokale_schatten()
        for z, spalte, text in self.parser_hinweise:
            self.melde("Hinweis", z, text, "klammern", spalte, 1)
        self.befunde.sort(key=lambda b: (b.zeile, SCHWERE[b.schwere]))
        return self.befunde


def pruefe(quelltext):
    """Prüft ein Programm und gibt eine Liste von Befund-Objekten zurück (leer = alles in Ordnung)."""
    try:
        parser = Parser(lexer(quelltext))
        programm = parser.programm()
    except SyntaxFehler as e:
        return [Befund("Fehler", e.zeile or 0, e.meldung, e.spalte, e.laenge, "syntax")]
    return Pruefer(programm, parser.hinweise).analysiere()


def formatiere_befunde(befunde, quelltext, dateiname=None):
    zeilen = quelltext.splitlines()
    ausgabe = []
    if dateiname:
        ausgabe.append(f"{dateiname}:")
    for b in befunde:
        ort = f"Zeile {b.zeile}" + (f", Spalte {b.spalte + 1}" if b.spalte is not None else "")
        ausgabe.append(f"{ort} – {b.schwere}: {b.meldung}")
        ausgabe += _quellzeile(zeilen, b.zeile, b.spalte, b.laenge)
    zaehlung = []
    for name, mehrzahl in (("Fehler", "Fehler"), ("Warnung", "Warnungen"), ("Hinweis", "Hinweise")):
        n = sum(1 for b in befunde if b.schwere == name)
        if n:
            zaehlung.append(f"{n} {name if n == 1 else mehrzahl}")
    ausgabe.append("Gefunden: " + ", ".join(zaehlung) + "." if zaehlung else "Keine Probleme gefunden.")
    return "\n".join(ausgabe)
