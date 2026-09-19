# Mitmachen

Schön, dass du hier bist. Klarsatz ist ein Lern- und Hobbyprojekt — Fragen, Fehlermeldungen und
Ideen sind genauso willkommen wie Code.

## Das Wichtigste vorweg: alles auf Deutsch

Das ist keine Marotte, sondern der Zweck des Projekts. Auf Deutsch sind: die Sprache selbst,
Fehlermeldungen, Kommentare, Docstrings, Dokumentation, Commit-Texte — und auch die Bezeichner im
Python-Code (`fuehre_aus`, `Grenzen`, `Bereich`). Umlaute in Bezeichnern werden als `ae`/`oe`/`ue`
geschrieben, in Texten für Menschen natürlich nicht.

## Einen Fehler melden

Am hilfreichsten ist das kleinste Programm, das ihn zeigt, dazu die erwartete und die tatsächliche
Ausgabe sowie deine Python-Version. Die Vorlage beim Anlegen eines Issues fragt genau danach.

## Etwas ändern

```bash
git clone https://github.com/wolfiru/klarsatz.git
cd klarsatz
python3 -m unittest discover -s tests -t .
```

Es gibt nichts zu installieren — Klarsatz benutzt nur die Standardbibliothek, und dabei soll es
bleiben: **das Paket `klarsatz/` bekommt keine Abhängigkeiten.** Es muss auch unter Pyodide im
Browser laufen.

Vor einem Pull Request:

1. **Tests schreiben.** Jede neue Funktion bekommt Tests in `tests/`, Fehlermeldungen werden mit
   `assertRaisesRegex` geprüft.
2. **Alle Tests laufen lassen** (`python3 -m unittest discover -s tests -t .`).
3. **Generatoren laufen lassen**, falls du an der Sprache oder den Wortlisten etwas geändert hast:
   ```bash
   python3 tools/baue_editor.py && python3 tools/baue_playground.py
   ```
   Sonst passen Hervorhebung und Spielwiese nicht mehr zum Interpreter — die CI merkt das.
4. **`CHANGELOG.md` ergänzen.**

## Was beim Ändern der Sprache zu beachten ist

* Neue reservierte Wörter gehören in `parser.RESERVIERT`/`STARTER` **und** in `sprachdaten.py`
  (ein Test erzwingt das). Alltagswörter wie *Zahl*, *Text* oder *Wert* werden **nicht** reserviert —
  sonst kann man sie nicht mehr als Namen benutzen.
* Fehlermeldungen sind freundlich, konkret und sagen, was zu tun ist: „Meintest du `Zeige`?"
* Kein Python-Traceback darf nach außen dringen. Alles endet in einem `KlarsatzFehler`.
* Neue Stellen, an denen etwas wachsen kann (Text, Liste, Zahl, Ausgabe), brauchen eine Grenze in
  `grenzen.py`.
* Der Formatierer darf **nie** den Inhalt eines Programms ändern; ein Test prüft das für alle
  Beispielprogramme.

## Sprachideen

Klarsatz soll klingen wie ein Satz, den man laut vorlesen kann, ohne dass es albern wird. Wenn eine
neue Formulierung zur Diskussion steht: Schreib sie als vollständiges Beispielprogramm auf und lies
es jemandem vor, der nicht programmieren kann. Was dabei stockt, ist noch nicht fertig.

Größere Umbauten bitte vorher als Issue besprechen — bevor du Arbeit hineinsteckst, die dann nicht
zur Richtung des Projekts passt.
