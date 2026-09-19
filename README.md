# Klarsatz

**Eine Programmiersprache, die wie Deutsch klingt.**

Zwei Sätze zur Einordnung, damit die Erwartung stimmt:

**Klarsatz ist keine natürliche Sprache.** Es ist eine Programmiersprache, deren Syntax sich an
deutscher Alltagssprache orientiert: feste Satzmuster, die sich vorlesen lassen. `Sag Hallo.`
versteht sie nicht — `Zeige "Hallo".` schon.

**Und sie will keine Zielsprache sein.** Am ehesten ist Klarsatz eine *didaktische Notation für das
Erlernen von Programmierdenken*: eine Schreibweise, in der man Variablen, Bedingungen, Schleifen und
Funktionen zum ersten Mal sieht, ohne gleichzeitig eine Fremdsprache zu lernen. Danach zieht man
weiter — der Knopf *Als Python* übersetzt jedes eigene Programm.

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

Du willst programmieren lernen? Das **[Tutorial](docs/TUTORIAL.md)** führt in elf Lektionen vom
ersten Satz bis zum eigenen Programm — und zeigt dir am Ende dasselbe Programm in Python
([auch als Webseite](https://www.ruthner.at/klarsatz/tutorial.html)). Es lehrt nicht Befehle,
sondern das Muster *vorhersagen → ausprobieren → verändern*, hat eine eigene Lektion übers
Fehlerlesen und endet mit einem Projekt ohne Musterlösung.

Danach gibt es einen zweiten Kurs: **[Zeichnen](docs/TUTORIAL-ZEICHNEN.md)** in acht Lektionen,
vom ersten Strich bis zum bewegten Bild ([auch als
Webseite](https://www.ruthner.at/klarsatz/tutorial-zeichnen.html)).

Nichts darin ist abgetippt. Ein Test führt jedes Beispiel aus und vergleicht Ausgaben,
Fehlermeldungen und die Python-Übersetzung mit dem, was im Text steht — beim Grafikkurs sogar die
Bilder selbst: Anzahl der Striche, Farben, und ob eine Figur geschlossen ist.

Dazu gibt es die **[Projektseite mit Dokumentation](https://www.ruthner.at/klarsatz/)**.

## Für wen ist Klarsatz — und für wen nicht?

Klarsatz ist eine **Lernsprache**. Sie nimmt eine einzige Hürde weg — die fremde Schreibweise — und
lässt alles andere am Programmieren unangetastet. Das macht sie für manche Leute sehr gut und für
andere überflüssig. Ehrlich eingeschätzt:

| | Für wen | Eignung | |
|---|---|---|---|
| ✓ | **Anfänger ab etwa 10 Jahren, deutschsprachig** | `●●●●●●●●●○` 9/10 | Der Quelltext ist der erklärende Satz. Es gibt nichts zu übersetzen, bevor man denken kann. |
| ✓ | **Schule und Kurse: der allererste Einstieg** | `●●●●●●●●●○` 9/10 | Elf Lektionen, Lernstufen, Spielwiese im Browser — nichts zu installieren, nichts einzurichten. |
| ✓ | **Erwachsene ohne Englischkenntnisse** | `●●●●●●●●○○` 8/10 | Befehle, Fehlermeldungen und die ganze Doku sind deutsch. |
| ✓ | **Wer danach Python lernen will** | `●●●●●●●●○○` 8/10 | Der Knopf *Als Python* übersetzt jedes eigene Programm — dieselben Ideen, andere Schreibweise. |
| ✓ | **Wer schnell ein Bild sehen will** | `●●●●●●●○○○` 7/10 | Stift, Farben und Schleifen ergeben in fünf Zeilen ein Vieleck. |
| ~ | **Hobby: kleine Rechnungen und Spielereien für sich selbst** | `●●●●●○○○○○` 5/10 | Reicht für Listen, Tabellen, Dateien und Text — aber ohne fremde Bibliotheken. |
| ✗ | **Kinder, die noch nicht sicher lesen (unter etwa 8)** | `●●●○○○○○○○` 3/10 | Klarsatz wird getippt und gelesen. Zum Klicken und Ziehen ist Scratch das bessere Werkzeug. |
| ✗ | **Wer Englisch kann und sofort Python will** | `●●●○○○○○○○` 3/10 | Dann ist der Umweg keiner. Klarsatz spart genau die Hürde, die es bei dir nicht gibt. |
| ✗ | **Erfahrene Programmierer als Zweitsprache** | `●●○○○○○○○○` 2/10 | Hier gibt es nichts Neues zu lernen — außer aus Neugier, wie eine deutsche Syntax sich anfühlt. |
| ✗ | **Programme über ein paar hundert Zeilen** | `●●○○○○○○○○` 2/10 | Es gibt keine Module, keine Pakete und keinen Namensraum über die Datei hinaus. |
| ✗ | **Webseiten, Apps, Datenauswertung, KI** | `●○○○○○○○○○` 1/10 | Dafür fehlt alles: Netzwerk, Bibliotheken, Ökosystem. Das ist Absicht, siehe Sicherheit. |

Die kurze Fassung: **Klarsatz ist die erste Sprache, nicht die einzige.** Wer damit programmieren
gelernt hat, soll weiterziehen — dafür gibt es den Knopf *Als Python*.

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
| `docs/` | die beiden Kurse, Sprachreferenz, Programmübersicht, Sicherheit |
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
