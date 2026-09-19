# Klarsatz

Eine Programmiersprache, die wie Deutsch klingt – Hobby- und Lernprojekt.

```
Frage "Wie heißt du? " und merke die Antwort als Name.
Wenn Name gleich "" ist:
    Zeige "Hallo, Unbekannter!".
Sonst:
    Zeige "Hallo, " und Name und "!".
Ende.
```

## Schnellstart

Voraussetzung: Python 3.10 oder neuer. Es gibt **keine** weiteren Abhängigkeiten.

```
python3 -m klarsatz programme/03_taschenrechner.klar     # Programm ausführen
python3 -m klarsatz                                      # interaktive Konsole
python3 -m klarsatz --pruefe programm.klar               # Fehler finden, ohne auszuführen
python3 -m klarsatz --formatiere --ersetzen programm.klar
python3 -m klarsatz --help
```
Optional installieren (dann heißt der Befehl nur `klarsatz`): `pip install -e .`

## Inhalt
| Ordner / Datei | Was |
|---|---|
| `klarsatz/` | das Python-Paket (Lexer, Parser, Interpreter, Prüfer, Formatierer, Konsole, Web-Schnittstelle) |
| `programme/` | zwölf Beispielprogramme zum Spielen (Taschenrechner, Galgenmännchen, To-do-Liste …) |
| `beispiele/` | kleine Sprachbeispiele |
| `docs/` | `SPRACHE.md` (Sprachreferenz), `PROGRAMME.md`, `SICHERHEIT.md` |
| `playground/` | Spielwiese für die Webseite (Editor, Ausführen im Browser mit Pyodide) |
| `editor/` | VS-Code-Erweiterung, TextMate-Grammatik, Regeln für JavaScript |
| `tools/` | Generatoren (`baue_editor.py`, `baue_playground.py`) und Entwicklerwerkzeuge |
| `tests/` | Testsuite (`python3 -m unittest discover -s tests -t .`) |
| `ÜBERGABE.md`, `CLAUDE.md` | Stand, offene Punkte und Arbeitsregeln für die Weiterarbeit |

## Tests
```
python3 -m unittest discover -s tests -t .                 # alles (Browser-Test wird übersprungen, wenn Playwright fehlt)
KLARSATZ_KEIN_BROWSER=1 python3 -m unittest discover -s tests -t .
```

## Lizenz
MIT – benutzen, ändern und weitergeben ausdrücklich erwünscht, solange der Urheberhinweis
erhalten bleibt. Ohne Gewähr: Klarsatz ist ein Lern- und Hobbyprojekt. Einzelheiten in `LICENSE`.
