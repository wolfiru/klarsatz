"""Formatierer: rückt ein Klarsatz-Programm nach seiner Blockstruktur sauber ein.

Ändert nur Leerraum am Zeilenanfang und -ende sowie überzählige Leerzeilen – nie den Inhalt.
Kommentare und Zeilenumbrüche innerhalb eines Satzes bleiben erhalten."""
from .lexer import lexer


def formatiere(quelltext, einzug=4):
    tokens = [t for t in lexer(quelltext) if t.art != "EOF"]
    pro_zeile = {}
    for t in tokens:
        pro_zeile.setdefault(t.zeile, []).append(t)

    ausgabe = []
    ebene = 0
    mitten = False            # steht die vorige Codezeile mitten in einem Satz?
    leer = True               # letzte ausgegebene Zeile war leer (oder es gibt noch keine)
    for nr, roh in enumerate(quelltext.split("\n"), start=1):
        text = roh.strip()
        if not text:
            if not leer:
                ausgabe.append("")
                leer = True
            continue
        toks = pro_zeile.get(nr)
        if not toks:                                       # reine Kommentarzeile
            stufe = ebene + 1 if mitten else ebene
        else:
            erste = toks[0].norm if toks[0].art == "WORT" else None
            letzte = toks[-1].art
            if mitten:
                stufe = ebene + 1
            elif erste == "ende":
                ebene = max(0, ebene - 1)
                stufe = ebene
            elif erste in ("sonst", "bei") and letzte == ":":
                stufe = max(0, ebene - 1)                  # 'Sonst:' steht auf der Höhe seines 'Wenn'
            else:
                stufe = ebene
            if letzte == ":" and not mitten:
                if erste not in ("sonst", "bei"):
                    ebene += 1                             # neuer Block; bei 'Sonst:' bleibt die Ebene gleich
            mitten = letzte not in (".", ":")
        ausgabe.append(" " * (einzug * stufe) + text)
        leer = False
    while ausgabe and ausgabe[-1] == "":
        ausgabe.pop()
    return "\n".join(ausgabe) + "\n" if ausgabe else ""
