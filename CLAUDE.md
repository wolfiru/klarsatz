# Arbeitsregeln für Claude (Claude Code auf dem Raspi)

Projekt: **Klarsatz** – eine deutsche Programmiersprache (Interpreter in Python). Besitzer: Wolfgang (Hobby, Lernprojekt).
Lies zuerst `ÜBERGABE.md` (Stand, offene Punkte, Pläne) und `docs/SPRACHE.md` (Sprache).

## Sprache und Ton
- Alles auf **Deutsch**: Fehlermeldungen, Kommentare, Docstrings, Dokumentation, Commit-Texte. Bezeichner im Code sind
  ebenfalls deutsch (`fuehre_aus`, `Grenzen`, `Bereich`), Umlaute in Bezeichnern als ae/oe/ue.
- Meldungen an Programmierende sind freundlich, konkret und sagen, was zu tun ist („Meintest du 'Zeige'?“).

## Regeln
- **Keine Abhängigkeiten** im Paket `klarsatz/` (nur Standardbibliothek). Es muss in Pyodide laufen.
- **Kein `eval`/`exec`/`__import__` auf Programmtext.** Programme dürfen nie Python-Objekte erreichen.
- Jede neue Funktion bekommt Tests in `tests/`. Fehlermeldungen werden mit `assertRaisesRegex` getestet.
- Kein Python-Traceback darf zum Anwender durchdringen: alles endet in `KlarsatzFehler` (Syntax/Laufzeit/Limit).
- Ressourcen begrenzen (`grenzen.py`): neue Wachstumsstellen (Text, Liste, Zahl, Ausgabe) prüfen.
- Nach Änderungen an Sprache/Wortlisten: `python3 tools/baue_editor.py` und `python3 tools/baue_playground.py`
  ausführen (sonst schlägt `tests/test_hervorhebung.py` bzw. die Spielwiese an).
- Parser-Änderungen: neue reservierte Wörter in `parser.RESERVIERT`/`STARTER` eintragen **und** in `sprachdaten.py`
  einordnen (ein Test erzwingt das). Alltagswörter (Zahl, Text, Wert …) NICHT reservieren.
- Der Formatierer darf nie den Inhalt ändern; `tests/test_formatierer.py` prüft das für alle Programme.

## Versionsverwaltung
Das Projekt liegt seit 19.09.2026 in einem Git-Repository (Zweig `main`). Vor größeren Umbauten einen
sauberen Stand committen; Commit-Texte auf Deutsch, Betreffzeile im Imperativ oder als Aussage.
Versionssprünge aus `CHANGELOG.md` mit `git tag -a vX.Y.Z` markieren.

## Architektur in einem Satz
Quelltext → `lexer.py` (Tokens mit Spalte, Artikel werden überlesen) → `parser.py` (Satzmuster → Syntaxbaum aus Tupeln)
→ `interpreter.py` (Baum ausführen; Werte in `werte.py`; Dateien über `dateisystem.py`; Grenzen aus `grenzen.py`).
Daneben: `pruefer.py` (statische Analyse), `formatierer.py`, `repl.py`, `web.py` (Abspielen statt Blockieren),
`hervorhebung.py` + `sprachdaten.py` (Regeln für Pygments/TextMate/JavaScript), `cli.py`.

## Befehle
```
python3 -m unittest discover -s tests -t .                   # alle Tests
KLARSATZ_KEIN_BROWSER=1 python3 -m unittest discover -s tests -t .   # ohne Browser-Test
python3 -m klarsatz --pruefe programme/11_galgenmaennchen.klar
python3 tools/baue_editor.py && python3 tools/baue_playground.py
```
Optionale Werkzeuge (nicht nötig zum Arbeiten): Node + `cd tools && npm install` (Vergleich mit dem VS-Code-Tokenizer),
`pip install pygments playwright` + `playwright install chromium` (Hervorhebungs- und Browser-Tests; ohne diese werden
die Tests übersprungen). Auf dem Raspi sind zeitabhängige Tests (`test_zeitlimit*`) ggf. knapp – dann Grenzen in den
Tests lockern, nicht in `grenzen.py`.
