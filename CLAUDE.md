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

## Webseite
Die Seite https://www.ruthner.at/klarsatz/ wird **in `webseite/` bearbeitet, nie im Webordner** — sonst geht die
Änderung beim nächsten Veröffentlichen verloren. `webseite/seiten/` (index, doku, spielplatz) und `webseite/assets/`
von Hand, `webseite/kapitel/` sind die Quellen der Doku-Kapitel. Veröffentlichen:
```
python3 tools/veroeffentliche_webseite.py     # Seiten + Bausteine, baut die Kapitel mit und stempelt
python3 tools/veroeffentliche_spielwiese.py   # playground/ -> spielwiese/
python3 tools/baue_archiv.py                  # ZIP + Prüfsumme + Versionsangaben in den Seiten
```
Die **Kurse** sind die Ausnahme: `docs/TUTORIAL.md` und `docs/TUTORIAL-ZEICHNEN.md` werden als
Markdown geschrieben (dort prüfen `tests/test_tutorial.py` und `tests/test_tutorial_zeichnen.py`
jeden Block nach) und von `tools/baue_tutorial.py` zu `tutorial.html` bzw. `tutorial-zeichnen.html`
gemacht — nie die HTML-Seiten bearbeiten, sonst ist die Änderung beim nächsten Bauen weg.
Codeblöcke bekommen dabei einen `code-kopf`; **nur daran** hängt `assets/app.js` den Link
„Im Spielplatz öffnen".

Das Bild neben dem Zeichenkurs ist kein Symbol, sondern das Ergebnis von
`webseite/assets/zeichnung.klar` — `python3 tools/baue_zeichnung.py` erzeugt daraus das SVG, die CI
prüft, ob es aktuell ist, und ein Test vergleicht es mit dem Programm, das die Seite daneben zeigt.

Cache-Stempel (`?v=…`) stehen **nicht** in `webseite/`; die setzt `tools/stempel_webseite.py` beim Veröffentlichen
aus dem Dateiinhalt. Nur im Webordner liegen: `doku-*.html` (erzeugt), `spielwiese/`, `downloads/`, `pyodide/`.

## Versionsverwaltung
Das Projekt liegt seit 19.09.2026 in einem Git-Repository (Zweig `main`), öffentlich auf
**https://github.com/wolfiru/klarsatz**. Vor größeren Umbauten einen sauberen Stand committen;
Commit-Texte auf Deutsch, Betreffzeile im Imperativ oder als Aussage. Hochladen mit
`git push origin main`; eine Marke braucht ein eigenes `git push origin vX.Y.Z`.

**Eine Version anheben:** `python3 tools/hebe_version.py 0.9.1` setzt die Nummer an allen zehn
Stellen. Von Hand bleiben die neue Überschrift in `CHANGELOG.md`, danach `baue_editor.py`, die drei
Veröffentlichungsbefehle und `git tag -a vX.Y.Z`.
`tests/test_doku_konsistenz.py` prüft all das nach — die Nummer auf der Seite setzt nämlich nicht
das Veröffentlichen, sondern erst `tools/baue_archiv.py`, und genau dadurch stand sie schon einmal
tagelang falsch da.

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
python3 tools/fuzze.py --laeufe 100000        # Dauerbeschießung mit verdorbenen Programmen
```
Optionale Werkzeuge (nicht nötig zum Arbeiten): Node + `cd tools && npm install` (Vergleich mit dem VS-Code-Tokenizer),
`pip install pygments playwright` + `playwright install chromium` (Hervorhebungs- und Browser-Tests; ohne diese werden
die Tests übersprungen). Auf dem Raspi sind zeitabhängige Tests (`test_zeitlimit*`) ggf. knapp – dann Grenzen in den
Tests lockern, nicht in `grenzen.py`.
