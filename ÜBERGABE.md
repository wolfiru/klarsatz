# Übergabe – Stand 19.09.2026, Version 0.7.1

> **Umbenannt:** Das Projekt hieß bis 18.09.2026 *Klartext*; der Name war schon vergeben.
> Alles heißt jetzt **Klarsatz** — nur die Dateiendung der Programme bleibt `.klar`.

Klarsatz ist eine deutsche Programmiersprache mit Python-Interpreter (Lernprojekt von Wolfgang). Diese Datei ist für
die Weiterarbeit (z. B. mit Claude Code auf dem Raspberry Pi). Arbeitsregeln: `CLAUDE.md`. Sprache: `docs/SPRACHE.md`.

## Was fertig ist (462 Tests, alle grün)
- **Interpreter** mit Aufgaben, Dingen, Listen, Tabellen, Textwerkzeugen, Zufall, Dateien, Fehlerbehandlung.
- **Härtung:** Grenzen (`grenzen.py`), Dateisystem-Abstraktion mit Ordnerschutz (`dateisystem.py`), Absturzschutz.
- **Fehlermeldungen:** Spalte + Markierung, Aufrufkette, deutsche Texte, „Meintest du …?“.
- **Prüfmodus** (`pruefer.py`, `--pruefe`), **Formatierer** (`--formatiere`), **Konsole** (`python3 -m klarsatz`).
- **Web-Schnittstelle** (`web.py`): Programme laufen bis zur nächsten `Frage`, danach wird mit allen Antworten und
  gleichem Zufalls-Startwert erneut abgespielt (kein blockierendes `input`, keine Threads nötig).
- **Spielwiese** (`playground/`): Editor mit Hervorhebung, Ausführen/Prüfen/Formatieren, Eingaben, läuft mit Pyodide
  in einem Web-Worker. Ende-zu-Ende-getestet in Chromium (`tests/test_browser.py`).
- **Editor-Unterstützung:** VS-Code-Erweiterung, TextMate-Grammatik, Pygments-Lexer, JS-Regeln – alle aus **einer**
  Regelliste (`hervorhebung.py`/`sprachdaten.py`); Tests vergleichen Pygments, VS-Code-Tokenizer und JS Token für Token.
- **Programme:** zwanzig Beispielprogramme (`programme/`), nach Schwierigkeit geordnet,
  jedes mit simuliertem Spieler getestet.
- **Versionsverwaltung:** seit 19.09.2026 ein Git-Repository in `/home/pi/klarsatz` (Zweig `main`,
  erster Commit als `v0.7.1` markiert). Erzeugte Dateien liegen bewusst mit im Repository, damit ein
  ausgecheckter Stand sofort läuft — geprüft: ein frischer Klon besteht alle 462 Tests.
  Es gibt **kein** entferntes Gegenstück; das Repository liegt auf derselben Karte wie das Projekt.

## Offen (in dieser Reihenfolge sinnvoll)
1. **Fuzz-Test — gebaut am 19.09.2026.** `tests/fuzzer.py` (Maschinerie), `tests/test_fuzz.py` (kurz und
   deterministisch, läuft immer mit), `tools/fuzze.py` (lange Läufe von Hand). Sechzehn Arten, ein Programm zu
   verderben; beschossen werden `laufe()`, `pruefe()`, `formatiere()` und `nach_python()`. Erlaubt ist nur ein
   `KlarsatzFehler`; ein Hänger wird über `signal.setitimer` als Fund gemeldet statt die Suite anzuhalten.
   Jeder Beschuss hat seine eigene Saat: `python3 tools/fuzze.py --wiederhole SAAT` stellt ihn allein nach.
   Ergebnis bisher: **keine Panne** (siehe `docs/SICHERHEIT.md`). Rund ein Fünftel der Mutanten dringt bis in
   den Interpreter vor — ein eigener Test wacht darüber, damit der Fuzzer nicht unbemerkt flach wird.
2. **Tutorial** (`docs/TUTORIAL.md`, noch nicht gemacht): ~10 kurze Lektionen mit lauffähigen Blöcken. Idee: Blöcke
   ```` ```klar ````, optional ```` ```eingabe ```` und ```` ```ausgabe ````; ein Test führt sie mit festem Seed aus und
   vergleicht – so bleibt das Tutorial korrekt. Lektionen: Hallo, Variablen/Rechnen, Eingabe, Entscheidungen,
   Schleifen, Listen, Aufgaben, Dinge, Tabellen, Fehler abfangen, ein Spiel bauen. Später als Seiten der Webseite.
3. **Webseite** – ~~offen~~ **gebaut am 18.09.2026**, siehe Abschnitt „Webseite" weiter unten.
   Offen geblieben: Tutorial-Seiten (hängt an Punkt 2).
4. **Browser-Testfehler — geklärt und erledigt (19.09.2026).** Deine Vermutung stimmte: An der Spielwiese lag
   es nicht. Nach dem Zeitlimit-Abbruch ist `#zweite .kp-lauf` vorhanden, sichtbar und nicht deaktiviert,
   und der zweite Lauf gelingt — er dauert nur rund 11 Sekunden, weil Pyodide dabei neu geladen wird.
   Der Testteil ist wieder aktiv (mit 180 s Zeitlimit für den zweiten Lauf). Die wahrscheinlichste Ursache
   für „Element nicht gefunden“: `zerstoere()` lief vor dem zweiten Klick — es räumt die Wurzel leer.
5. **Sprachideen** aus dem ursprünglichen Entwurf: Optionalwerte (`Falls vorhanden:`), Fähigkeiten
   (`Diese Aufgabe darf nur lesen`), später Bytecode-VM oder Compiler (C/Wasm). Kleines: mehrere Sätze in
   der Kurzform von `Wenn`, Wörterbuch-Werte direkt durchgehen.
   `Warte N Sekunden` ist seit 0.5.0 **gebaut** – zusammen mit dem Mitlesen (siehe unten).

## Webseite (Stand 19.09.2026)

**Die Webseite liegt seit 19.09.2026 mit im Repository** (`webseite/`) und wird dort bearbeitet, nicht im
Webordner: `seiten/` (index, doku, spielplatz) und `assets/` von Hand, `kapitel/` als Quelle der Doku-Kapitel.
Veröffentlicht mit `python3 tools/veroeffentliche_webseite.py` — das kopiert, baut die Kapitel und stempelt.
Nur im Webordner liegen die erzeugten `doku-*.html`, `spielwiese/`, `downloads/` und `pyodide/` (14 MB Fremdcode).


Adresse: **https://www.ruthner.at/klarsatz/** – Ordner `/var/www/html/klarsatz/`. Auf der Startseite
(`/var/www/html/index.html`) prominent verlinkt, im selben Muster wie Video Wallpaper, mit einem animierten
SVG-Symbolbild (`assets/klarsatz-symbolbild.svg`).

| Was | Wo |
|---|---|
| Hauptseite, Doku (6 Kapitel), Spielplatz | `index.html`, `doku*.html`, `spielplatz.html` |
| Design, Hintergrund-Animation, Hervorhebung | `assets/` |
| Vorlage der Doku-Kapitel (im Projekt) | `webseite/kapitel/` + `webseite/baue_doku.sh` |
| Spielwiese (unverändert aus `playground/`) | `spielwiese/` |
| Download-Archiv (`klarsatz-<version>.zip`) | `downloads/` |
| Pyodide, selbst gehostet (14 MB) | `pyodide/` (v0.26.4: pyodide.js, .asm.js, .asm.wasm, python_stdlib.zip, pyodide-lock.json) |

Der alte Pfad `/klartext/` liegt noch als Weiterleitungsseite im Webroot (kein echter 301 — `AllowOverride` ist aus, dafür bräuchte es einen Eintrag im VHost).

**Entscheidungen:** Pyodide wird selbst ausgeliefert (kein fremder CDN sieht die Besucher; die Zusage „nichts
verlässt deinen Browser" stimmt damit buchstäblich). Die Doku ist handgeschrieben statt aus `docs/SPRACHE.md`
erzeugt – dafür prüft ein Werkzeug jedes Codebeispiel gegen den echten Interpreter.

**Neue Werkzeuge:**
```
python3 tools/veroeffentliche_spielwiese.py   # baut playground/ und kopiert es nach spielwiese/
python3 tools/pruefe_webseite.py             # führt jeden <pre class="klar">-Block der Seite aus
python3 tools/stempel_webseite.py            # ?v=… für CSS/JS auffrischen (Browser-Zwischenspeicher)
python3 tools/baue_archiv.py                 # Download-Archiv schnüren und auf der Seite eintragen
```
`stempel_webseite.py` wird von `webseite/baue_doku.sh` und `veroeffentliche_spielwiese.py` selbst
aufgerufen; von Hand braucht man es nur nach direkten Änderungen an `assets/` oder an den drei
Seiten ohne Vorlage. Ohne frischen Stempel zeigen Browser hartnäckig die alte Fassung.

**Die Stempel-Kette der Spielwiese** (wichtig, weil sonst ein alter Interpreter im Browser hängen bleibt):
`spielplatz.html` lädt `assets/spielplatz.js?v=…`; dessen `import` von `spielwiese/klarsatz-playground.js`
trägt einen Stempel über **alle** Dateien im Ordner `spielwiese/`; und `klarsatz-playground.js` hängt
genau diesen Stempel (aus `import.meta.url`) an `beispiele.json`, `hervorhebung.json`, `klarsatz-worker.js`
und `klarsatz-py.zip`. Ändert sich also die Sprache, ändert sich der Ordner-Stempel und jeder Browser
holt Paket und Beispiele neu. Deshalb stempelt `stempel_webseite.py` die Skripte **vor** den Seiten.
`pruefe_webseite.py` meldet nur Befunde der Schwere „Fehler"; Blöcke mit `data-pruefung="nein"` werden
übersprungen. Stand: 42 Blöcke, 39 davon ausgeführt, 0 beanstandet.

**Änderung an der Spielwiese:** `erstelle()` kennt die Option `pyodideUrl`; sie wird als `?pyodide=…` an die
Worker-Adresse gehängt, der Worker liest sie dort aus. Ohne Angabe bleibt es beim CDN – `playground/index.html`
und `tests/test_browser.py` verhalten sich also unverändert. Ein Test dafür fehlt noch (bräuchte Chromium).

**Doku-Kapitel ändern:** Die sechs Kapitel liegen als HTML-Abschnitte in `webseite/kapitel/`;
`bash webseite/baue_doku.sh` setzt sie in die gemeinsame Hülle (Navigation, Seitenleiste, Blättern, Fußzeile)
und schreibt die fertigen Seiten nach `/var/www/html/klarsatz/`. Wer direkt an den erzeugten Dateien arbeitet,
schreibt die Änderung nach `webseite/kapitel/` zurück — sonst überschreibt der nächste Lauf sie.
Hauptseite, Doku-Übersicht und Spielplatz haben keine Vorlage, die werden direkt bearbeitet.

**Download für Besucher:** `tools/baue_archiv.py` packt Paket, Programme, Beispiele, Doku, Tests,
Editor-Erweiterung und Spielwiese in ein ZIP (ohne `ÜBERGABE.md`, `CLAUDE.md` und `webseite/` — die
betreffen nur den Betrieb dieser Seite), legt die SHA256-Summe daneben und trägt Dateiname, Version,
Größe und Prüfsumme in die Seiten ein (Stellen mit `data-download="…"`). Nach jeder Versionsänderung
einmal laufen lassen. Lizenz: **MIT** (`LICENSE`, seit 18.09.2026).

**Wenn sich die Sprache ändert:** `python3 tools/veroeffentliche_spielwiese.py` (bringt Beispiele, Paket und
Hervorhebungsregeln auf die Seite) und danach `python3 tools/pruefe_webseite.py` (findet Doku-Beispiele, die
nicht mehr laufen).

## Nächste Ausbaustufen (Wolfgangs Reihenfolge, 18.09.2026)

Vier Vorschläge, hier mit der Stelle im Code, an der sie ansetzen, und dem jeweiligen Knackpunkt.

### 1. Lernstufen (`--stufe 1`)
Nur `Zeige`, `Frage`, `Merke`; höhere Stufen schalten Rechnen, Bedingungen, Schleifen, Listen, Aufgaben frei.
Wer zu früh greift, liest: „Das lernst du in Stufe 3."

* **Ansatz:** je Satzanfang eine Stufe in `sprachdaten.py` (dort liegen schon `GRUPPEN` für die Hervorhebung —
  die Stufe gehört daneben, damit es *eine* Regelliste bleibt), Prüfung in `parser.py` beim Lesen des Starters,
  `--stufe` in `cli.py`, Auswahl in der Spielwiese, und die Doku-Kapitel der Webseite entsprechen fast schon
  den Stufen.
* **Knackpunkt:** Nicht nur Satzanfänge brauchen eine Stufe. `Zeige die Wurzel von 4.` beginnt mit Stufe 1,
  benutzt aber eine höhere Funktion — `FUNKTIONEN` und die Operatoren müssen mit eingestuft werden, sonst ist
  die Sperre löchrig.
* Kleinster Eingriff der vier, und er gibt allem anderen eine Ordnung.

### 2. Grafik im Browser — **gebaut am 18.09.2026 (0.3.0)**
Umgesetzt wie unten beschrieben: der Interpreter meldet nur Striche, die Oberfläche malt. Offen geblieben:
Testabdeckung für die Leinwand selbst (bräuchte den Browser-Test) und `Schreibe die Zeichnung in "bild.svg".`
als Satz in der Sprache — bisher geht das nur über `--bild`.

<details><summary>ursprüngliche Planung</summary>
* **Ansatz:** neue Satzmuster in `parser.py`/`interpreter.py` (Position, Winkel, Stift als Zustand) und — das ist
  der elegante Teil — **keine** Zeichenlogik im Interpreter: `web.py` führt schon einen `verlauf` aus
  `("aus", Text)`, `("frage", …)`, `("antwort", …)`. Ein weiterer Eintrag `("linie", x1, y1, x2, y2, farbe)`
  fügt sich nahtlos ein. Die Oberfläche entscheidet dann, was daraus wird: im Browser ein Canvas neben der
  Ausgabe, auf der Kommandozeile eine SVG-Datei.
* **Knackpunkt:** genau diese Trennung durchhalten — sobald der Interpreter selbst zeichnet, ist sie dahin.
* Größter sichtbarer Gewinn für die Webseite.
</details>

### 3. „Zeig mir das in Python" — **gebaut am 19.09.2026 (0.6.0)**
`klarsatz/nach_python.py`, `--nach-python`, Knopf *Als Python* in der Spielwiese. Entschieden wurde
**lesbar statt exakt**: Wo Klarsatz anders rechnet (Listen ab 1, Komma statt Punkt, ganzzahliges Teilen,
deutsche Sortierung), steht ein Hinweis im Kopf des erzeugten Programms statt einer Hilfsbibliothek.
Zeichnen wird zu `turtle`, Dinge zu `@dataclass`. Ein Test vergleicht für vier Programme die Ausgabe
von Klarsatz mit der des erzeugten Python — sie ist identisch.

Zwei Fallen, die beim Bauen auftauchten und im Modul gelöst sind: Klarsatz unterscheidet Groß- und
Kleinschreibung nicht (Python schon → Namensspeicher), und Feldnamen dürfen gebeugt sein
(`Name`/`Namen` → `werte.passt`).

<details><summary>ursprüngliche Planung</summary>
* **Ansatz:** neues Modul `nach_python.py`, ein Besucher über die 29 Satzformen
  (`('merke', zeile, wert, norm, name, konstante)` usw.), `--nach-python` in der CLI, in der Spielwiese ein
  vierter Knopf neben Prüfen und Formatieren.
* **Knackpunkt — entschieden: lesbar.** *lesbar* oder *exakt*. Klarsatz teilt ganzzahlig, wenn es aufgeht,
  zählt ab 1, sortiert nach deutscher Reihenfolge und gibt Kommazahlen deutsch aus. Wer das alles exakt
  abbildet, erzeugt Python mit einer kleinen Hilfsbibliothek — lesbar ist das nicht mehr. Für den Zweck
  („die Brücke zeigen") wäre schlichtes, idiomatisches Python richtig, mit ehrlichem Hinweis an den
  Stellen, an denen es abweicht.
</details>

### 4. Übungsaufgaben mit Selbstprüfung
* **Ansatz:** `web.laufe(quelltext, antworten, seed)` ist bereits deterministisch — eine Aufgabe ist damit
  ein Datensatz aus Angabe, vorgegebenen Antworten und Prüfregel. Dazu ein Test, der alle Musterlösungen
  durchspielt (wie `tools/pruefe_webseite.py` es für die Doku-Beispiele tut), und eine Übungsseite.
* **Knackpunkt:** nicht auf wortgleiche Ausgabe prüfen, das ist zu spröde — besser Regeln („enthält",
  „letzte Zeile ist 42").
* Überschneidet sich stark mit dem noch offenen **Tutorial** (Punkt 2 der Liste oben): beides sind Lektionen
  mit lauffähigem Code. Sinnvollerweise zusammen planen, sonst entstehen zwei Systeme für dasselbe.

**Vorgeschlagene Reihenfolge:** 1 → 2 → 4 (mit Tutorial) → 3. Die Stufen geben Doku und Übungen ihre Ordnung,
die Grafik macht den Spielplatz attraktiv, die Python-Brücke ist eigenständig und jederzeit nachrüstbar.

## Schreibweise in den Beispielen (bewusst so)

`hallo.klar` und die Programme 01–03 nutzen durchgängig die gesprochene Form (`Merke dir 5 als Zahl.`,
`… und merke dir die Antwort als a.`), ab Programm 04 die knappe (`Merke 5 als Zahl.`). Das ist Absicht:
Die ersten Programme sollen klingen wie gesprochene Sprache, später tritt die Form zurück. Innerhalb
einer Datei bitte nicht mischen — sonst entsteht der Eindruck, die Formen bedeuteten Verschiedenes.
`Zeige mir` steht nur in Lernbeispielen; in Dialogprogrammen richtet sich `Zeige` an den Spieler,
nicht an die programmierende Person.

## Mitlesen statt Abwarten (0.5.0)

Bis 0.4 lief ein Programm im Worker komplett durch, und erst danach kam alles auf einmal zurück. Eine
Endlosschleife blieb damit stumm — eine gehende Uhr war unmöglich. Seit 0.5.0 reicht `web.laufe(…, melde=…)`
jeden Verlaufseintrag **sofort** weiter; `klarsatz-worker.js` schickt ihn per `postMessage` an die Spielwiese,
die Ausgabe und Leinwand live füllt.

Was daran hängt, und was man beim Ändern wissen muss:
* **Zeitlimit als Wachhund:** Jede Teilmeldung setzt den Timer zurück (`auftrag.frisch()`). Ein Programm,
  das etwas meldet, gilt nicht als hängend — auch wenn es wartet. Eine stumme Endlosschleife wird weiterhin
  nach `zeitlimitMs` abgebrochen.
* **Abbrechen** beendet den Worker und startet ihn neu (Python lädt dabei erneut, ~11 s). Wichtig: In
  `neuStarten()` werden die Wächter der alten Aufträge abgeräumt — sonst beendet ein altes Zeitlimit später
  den frischen Worker mitten im Laden (genau dieser Fehler war 0.4 lange unentdeckt).
* **Speicher:** Wer mitliest, bekommt alles; im Ergebnis bleiben nur die jüngsten 5000 Einträge. Die Spielwiese
  zeigt höchstens 4000 Ausgabezeilen und wirft ältere weg.
* **`Warte`** schläft echt (`time.sleep` im Worker). Die Wartezeit wird von der Rechenzeit abgezogen und über
  `Grenzen.warte` gedeckelt — Tests setzen `Grenzen(warte=0)` und laufen dadurch in voller Geschwindigkeit.

## Bekannte Eigenheiten (bewusst so, aber gut zu wissen)
- Artikel (der, die, das, ein, eine …) werden vom Lexer **überlesen**; deshalb ist `… ein.` am Satzende von
  `Trage … in T ein.` optional. Seit 0.4.1 gilt dasselbe für Füllwörter (`lexer.FUELLWOERTER`:
  dir, dich, mir, mich, uns, sich, bitte) — daher braucht `Drehe dich um 90 Grad` keinen Sonderfall
  im Parser. Wer die Liste ändert: `sprachdaten.ARTIKEL` zieht sie automatisch mit, aber
  `tools/baue_editor.py` und `tools/baue_playground.py` müssen laufen.
- `hoch`, `mal`, `plus`, `minus`, `von`, `mit`, `zu`, `in` … sind reserviert (z. B. keine Aufgabe „Hoch“).
- Argumente von Aufgaben/Funktionen sind einfache Werte: `Quadrat von x plus 1` = `(Quadrat von x) plus 1`.
  `--pruefe` gibt dazu einen Hinweis.
- Kurzform `Wenn …, tue einen Satz.` – für mehr die Blockform. Bei `Sonst`-Ketten in der Kurzform bindet ein
  `Sonst` an das nächstliegende passende `Wenn`.
- Feldnamen dürfen leicht gebeugt sein (`Name`/`Namen`) – Heuristik in `werte.passt`.
- `Zähle von 5 bis 1` läuft **nie** (rückwärts: `… rückwärts`). Das war in 0.1 anders.
- Die Zeitgrenze wird nur zwischen Schritten geprüft (siehe `docs/SICHERHEIT.md`).
- Der Prüfer arbeitet ohne Datenfluss: kein Typwissen, „benutzt vor angelegt“ nur nach Zeilenreihenfolge.

## Entscheidungen und Gründe
- **Python statt Rust:** schnell zum Ausprobieren der Sprache; Pyodide erlaubt die Spielwiese ohne zweite Implementierung.
- **Syntaxbaum aus Tupeln** (`("zeige", zeile, [...])`): kompakt; Formen stehen im Parser (`s_…`) und werden im
  Interpreter (`_a_…`) und Prüfer (`_satz`) gelesen. Wer eine Form ändert, muss alle drei anfassen.
- **Abspielen statt Coroutinen** für den Web-Betrieb: einfacher und deterministisch (Zufall über Seed).
- **Eine Regelliste für alle Hervorhebungen**, damit VS Code, Pygments und die Webseite nie auseinanderlaufen.
- **Ordnerschutz als Standard** für Dateien: sicherer Ausgangswert; Lockerungen nur per ausdrücklichem Schalter.

## Raspberry Pi
- Python ≥ 3.10 genügt (Raspberry Pi OS „Bookworm“ hat 3.11). Keine Installation nötig: `python3 -m klarsatz …`.
- Tests: `python3 -m unittest discover -s tests -t .` — seit 19.09.2026 läuft auch der Browser-Test auf dem Pi:
  `python3 -m playwright install chromium` holt einen arm64-Build (kein System-Chromium nötig). Die 21
  Browser-Tests brauchen Internet (Pyodide vom CDN) und rund 70 Sekunden. Ohne Browser weiterhin:
  `KLARSATZ_KEIN_BROWSER=1 python3 -m unittest discover -s tests -t .`
- Auf dem Pi sind `test_zeitlimit*` und der Test „Endlosschleife“ in `test_haertung.py` zeitabhängig; bei Wackeln die
  Testgrenzen lockern.
- Spielwiese lokal ansehen: `python3 tools/baue_playground.py && python3 -m http.server -d playground 8000`
  → `http://<pi>:8000/`.
