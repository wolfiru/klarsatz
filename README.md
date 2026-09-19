# Klarsatz

**Eine Programmiersprache, die wie Deutsch klingt.**

[![Tests](https://github.com/wolfiru/klarsatz/actions/workflows/tests.yml/badge.svg)](https://github.com/wolfiru/klarsatz/actions/workflows/tests.yml)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-gold.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Ohne Abhängigkeiten](https://img.shields.io/badge/Abh%C3%A4ngigkeiten-keine-brightgreen.svg)](pyproject.toml)

```klarsatz
Frage "Wie heißt du? " und merke die Antwort als Name.

Wenn Name gleich "" ist:
    Zeige "Hallo, Unbekannter!".
Sonst:
    Zeige "Hallo, " und Name und "!".
Ende.
```

Klarsatz schreibt man in ganzen Sätzen, mit Punkt am Ende. Es gibt keine geschweiften Klammern,
kein `;`, kein `==` und keine englischen Schlüsselwörter — dafür Artikel, die überlesen werden,
und Fehlermeldungen, die auf Deutsch sagen, was zu tun ist.

> *A programming language whose syntax is written in plain German — keywords, error messages,
> documentation and all. Pure Python 3, no dependencies, runs in the browser via Pyodide.*

## Gleich ausprobieren

**→ [Spielwiese im Browser](https://www.ruthner.at/klarsatz/spielplatz.html)** — nichts zu
installieren. Der Interpreter läuft als WebAssembly in einem Web-Worker, ohne Server und ohne
Zugriff auf die Festplatte. 29 Beispielprogramme sind zum Hineinladen hinterlegt, vom Zahlenraten
bis zum grafischen Textadventure.

Du willst die Sprache von Grund auf lernen? Das **[Tutorial](docs/TUTORIAL.md)** führt in elf
Lektionen vom ersten Satz bis zum eigenen Spiel — [auch als
Webseite](https://www.ruthner.at/klarsatz/tutorial.html). Jedes Beispiel darin läuft wirklich: Ein
Test führt alle 42 Programme aus und vergleicht ihre Ausgabe mit dem, was im Text steht. Das
Tutorial kann also nicht veralten.

Dazu gibt es die **[Projektseite mit Dokumentation](https://www.ruthner.at/klarsatz/)**.

## Auf dem eigenen Rechner

Voraussetzung: Python 3.10 oder neuer. **Keine weiteren Abhängigkeiten** — nur die Standardbibliothek.

```bash
git clone https://github.com/wolfiru/klarsatz.git
cd klarsatz

python3 -m klarsatz programme/03_taschenrechner.klar   # ein Programm ausführen
python3 -m klarsatz                                    # interaktive Konsole
python3 -m klarsatz --pruefe meins.klar                # Fehler finden, ohne auszuführen
python3 -m klarsatz --formatiere --ersetzen meins.klar # einheitlich einrücken
python3 -m klarsatz --nach-python meins.klar           # als lesbares Python ausgeben
python3 -m klarsatz --help
```

Mit `pip install -e .` heißt der Befehl danach einfach `klarsatz`.

## Was die Sprache kann

<table>
<tr><th>Rechnen und Entscheiden</th><th>Wiederholen</th></tr>
<tr><td>

```klarsatz
Merke 7 als Zahl.
Erhöhe Zahl um 3.
Wenn Zahl größer als 5 ist:
    Zeige "groß".
Ende.
```
</td><td>

```klarsatz
Wiederhole 3 Mal:
    Zeige "hallo".
Ende.

Für jedes Tier in Tiere:
    Zeige Tier.
Ende.
```
</td></tr>
<tr><th>Eigene Aufgaben</th><th>Eigene Dinge</th></tr>
<tr><td>

```klarsatz
Definiere Aufgabe Fakultät von n:
    Wenn n kleiner als 2 ist:
        Gib 1 zurück.
    Ende.
    Gib n mal (Fakultät von (n minus 1)) zurück.
Ende.
```
</td><td>

```klarsatz
Ein Hund hat einen Namen und ein Alter.

Erschaffe einen Hund mit Name "Rocco"
    und Alter 5 als Rocco.
Erhöhe das Alter von Rocco um 1.
```
</td></tr>
</table>

Dazu: Listen und Tabellen, Textwerkzeuge, Zufall, Dateien, Winkelfunktionen, Datum und Uhrzeit,
Fehlerbehandlung mit `Versuche` … `Bei Fehler`, und eine Schildkrötengrafik:

```klarsatz
Nimm die Farbe "gold".
Wiederhole 4 Mal:
    Gehe 120 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```

Die vollständige Sprachbeschreibung steht in **[`docs/SPRACHE.md`](docs/SPRACHE.md)**.

## Beispielprogramme

In `programme/` liegen zwanzig lauffähige Programme, nach Schwierigkeit geordnet — vorne genügen
Eingabe und Rechnen, hinten kommen Tabellen, Dateien, Rekursion und Zeichnen zusammen:

| | | |
|---|---|---|
| `01_zahlenraten_du_raetst` | `08_zahlenraten_computer_raet` | `15_baum` (rekursiv gezeichnet) |
| `03_taschenrechner` | `11_galgenmaennchen` | `16_uhr` (tickt wirklich) |
| `05_primzahlen` | `13_spirale` | `18_todo_liste` (mit Datei) |
| `07_schere_stein_papier` | `14_wellen` (Sinus und Kosinus) | `20_grafisches_adventure` |

Alle mit Kurzbeschreibung in **[`docs/PROGRAMME.md`](docs/PROGRAMME.md)**. Jedes Programm wird von
der Testsuite mit einem simulierten Spieler durchgespielt, damit die Beispiele nie veralten.

## Sicherheit

Weil Klarsatz im Browser läuft und Anfänger damit experimentieren, ist der Interpreter auf
Schadensbegrenzung gebaut: Grenzen für Schritte, Zeit, Speicher und Ausgabe; Dateizugriff nur im
Arbeitsordner (im Browser gar nicht); **kein `eval`, kein `exec`, kein Nachladen**, und ein
Klarsatz-Programm erreicht nie ein Python-Objekt. Ein Python-Traceback dringt nie nach außen —
jeder Fehler endet als deutsche Meldung.

Damit das nicht bloß behauptet ist, gibt es einen **Fuzz-Test**: Er zerhackt die Beispielprogramme
zufällig und verfüttert die Trümmer an Interpreter, Prüfer, Formatierer und Python-Übersetzer.
Erlaubt ist nur eine freundliche deutsche Fehlermeldung — jede Python-Ausnahme und jeder Hänger gilt
als Fund. Er prüft auch sich selbst: Untergeschobene Fehler *müssen* auffallen.

Eine geprüfte Sandbox ist das trotzdem nicht, und der Fuzz-Test ist ein Beleg, kein Beweis. Was
abgesichert ist und was nicht, steht ehrlich in **[`docs/SICHERHEIT.md`](docs/SICHERHEIT.md)**.

## Projektaufbau

| Ordner | Inhalt |
|---|---|
| `klarsatz/` | das Paket: Lexer, Parser, Interpreter, Prüfer, Formatierer, Konsole, Web-Schnittstelle, Python-Übersetzer |
| `programme/` | zwanzig Beispielprogramme |
| `beispiele/` | kleine Sprachbeispiele, je ein Thema |
| `docs/` | Tutorial, Sprachreferenz, Programmübersicht, Sicherheit |
| `playground/` | die Spielwiese für den Browser (Editor, Pyodide-Worker) |
| `editor/` | VS-Code-Erweiterung, TextMate-Grammatik |
| `webseite/` | die Seiten von [ruthner.at/klarsatz](https://www.ruthner.at/klarsatz/): `seiten/` und `assets/` von Hand, `kapitel/` als Quelle der Doku-Kapitel |
| `tools/` | Generatoren und Werkzeuge für Webseite und Archiv |
| `tests/` | 462 Tests |

Der Weg durch den Code in einem Satz: Quelltext → `lexer.py` (Wörter, Artikel werden überlesen) →
`parser.py` (Satzmuster werden zu einem Baum) → `interpreter.py` (Baum ausführen). Die
Hervorhebung für VS Code, Pygments und den Browser stammt aus **einer** Regelliste
(`sprachdaten.py`) — ein Test vergleicht alle drei Token für Token.

## Tests

```bash
python3 -m unittest discover -s tests -t .
KLARSATZ_KEIN_BROWSER=1 python3 -m unittest discover -s tests -t .   # ohne Chromium
```

Optional für die vollständige Abdeckung: `pip install pygments playwright && playwright install chromium`.
Fehlen sie, werden die betroffenen Tests übersprungen statt zu scheitern.

## Mitmachen

Fehlermeldungen, Ideen und Verbesserungen sind willkommen — siehe
[`CONTRIBUTING.md`](CONTRIBUTING.md). Alles im Projekt ist auf Deutsch: Code, Kommentare,
Dokumentation, Commit-Texte.

## Lizenz

MIT — benutzen, ändern und weitergeben ausdrücklich erwünscht, solange der Urheberhinweis erhalten
bleibt. Ohne Gewähr: Klarsatz ist ein Lern- und Hobbyprojekt von
[Wolfgang Ruthner](https://www.ruthner.at). Einzelheiten in [`LICENSE`](LICENSE).
