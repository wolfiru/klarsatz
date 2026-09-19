"""Grenzen für Rechenzeit, Speicher und Größe – Schutz vor Endlosschleifen und Ressourcenfressern."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Grenzen:
    schritte: int | None = None      # Anweisungen + Schleifendurchläufe insgesamt (None = unbegrenzt)
    sekunden: float | None = None    # Rechenzeit in Sekunden (None = unbegrenzt)
    tiefe: int = 150                 # ineinander verschachtelte Aufgabenaufrufe
    text: int = 10_000_000           # längster Text (Zeichen)
    liste: int = 5_000_000           # größte Liste bzw. Tabelle (Einträge)
    zahl_bits: int = 200_000         # größte ganze Zahl (Bits)
    ausgabe: int = 50_000_000        # Gesamtausgabe (Zeichen)
    eingabe: int = 100_000           # längste Eingabezeile (Zeichen)
    quelltext: int = 1_000_000       # Größe des Programms (Zeichen)
    verschachtelung: int = 50        # Ebenen von Klammern/Blöcken im Programm
    datei: int = 10_000_000          # Größe einer Datei beim Lesen/Schreiben (Zeichen)
    striche: int = 200_000           # Linien einer Zeichnung
    warte: float = 60.0              # längste einzelne Wartezeit in Sekunden (0 = gar nicht warten)

    @classmethod
    def streng(cls):
        """Für fremde, nicht vertrauenswürdige Programme (z. B. auf einer Webseite)."""
        return cls(schritte=5_000_000, sekunden=5.0, tiefe=100, text=1_000_000, liste=200_000,
                   zahl_bits=50_000, ausgabe=1_000_000, eingabe=10_000, quelltext=100_000,
                   verschachtelung=40, datei=1_000_000, striche=20_000, warte=10.0)
