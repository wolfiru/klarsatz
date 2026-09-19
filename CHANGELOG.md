# Änderungen

## Unveröffentlicht
- **Tutorial** (`docs/TUTORIAL.md`): elf Lektionen vom ersten Satz bis zum selbstgebauten
  Zahlenraten — Ausgabe, Variablen, Eingabe, Entscheidungen, Schleifen, Listen, Tabellen, Aufgaben,
  Dinge, Fehlerbehandlung, ein Spiel. `tests/test_tutorial.py` führt alle 42 Beispiele aus und
  vergleicht ihre Ausgabe mit dem Text; das Tutorial kann also nicht veralten.
  `tools/baue_tutorial.py` macht daraus die Seite `tutorial.html` — eine Quelle, zwei Ausgaben.
- **Richtiggestellt:** Mehrere Stellen der Webseite nannten noch Version 0.2 (Kopf der Startseite,
  Doku-Übersicht, Referenz), während der Download bei 0.7.1 stand. Sie tragen jetzt
  `data-download="version"` und werden beim Archivbau mitgezogen.
- **Fuzz-Test** (`tests/test_fuzz.py`, `tests/fuzzer.py`, `tools/fuzze.py`): Gültige Programme werden
  zufällig zerhackt — Zeichen, Wörter, Zeilen, Einrückung, Punkte, Zahlen, Texte — und an alles
  verfüttert, was Quelltext entgegennimmt: Ausführen, Prüfen, Formatieren, Übersetzen nach Python.
  Erwartet wird ausschließlich ein `KlarsatzFehler`. Jeder Beschuss hat seine eigene Saat und ist
  damit einzeln wiederholbar (`python3 tools/fuzze.py --wiederhole SAAT`).
  Der Test enthält **Gegenproben**: Ein untergeschobener Python-Fehler und ein untergeschobener
  Hänger müssen erkannt werden, und ein Teil der Mutanten muss wirklich bis in den Interpreter
  vordringen — sonst prüfte der Test nur den Parser.
- **Richtiggestellt:** Die README nannte die Fehlerbehandlung `Versuche` … `Falls schiefgeht`.
  Sie heißt `Versuche` … `Bei Fehler`.

## 0.7.1
- **Programme nach Komplexität geordnet** (01–20): vorne Eingabe und Rechnen, dann Aufgaben und
  Listen, Texte und Dinge, Zeichnen — und am Ende die großen Programme. Das Grafikadventure steht
  jetzt als letztes, die Wellen weiter vorne. Alle Dateien wurden umbenannt; Tests, Doku und
  Webseite ziehen mit.
- **`Rechtsbündig von x auf n Zeichen`** und **`Linksbündig …`**: füllen mit Leerzeichen auf, damit
  Tabellen untereinander stehen. `Formatiert` setzt ja nur die Nachkommastellen — sobald Werte
  unterschiedlich lang sind, verrutschten die Spalten. Die Wertetabelle in `14_wellen.klar` nutzt es.

## 0.7.0
- **Winkelfunktionen** in Grad: `der Sinus von g`, `der Kosinus von g` (auch `Cosinus`),
  `der Tangens von g` sowie die Umkehrungen `Arkussinus`, `Arkuskosinus`, `Arkustangens`.
  Rechenrauschen wird weggerundet (`Kosinus von 90` ist glatt `0`); der Tangens von 90 und 270 Grad
  meldet einen Fehler statt einer riesigen Zahl. Übersetzt sich nach `math.sin(math.radians(…))`.
- Neues Programm `14_wellen.klar`: Sinus und Kosinus als Wellenlinien in zwei Farben, mit einer
  Aufgabe `LinieZu`, die Richtung und Länge selbst ausrechnet.

## 0.6.2
- **Behoben:** Ein Feldzugriff auf etwas, das kein Ding ist (`Zeige den Sinus von 30.`), ließ einen
  Python-Fehler durch (`'int' object has no attribute 'werte'`). Ursache: Der Zugriff `obj.werte[…]`
  wurde ausgewertet, bevor die freundliche Prüfung greifen konnte. Jetzt kommt die Meldung
  „'Sinus von …' geht nur bei Dingen (Strukturen), hier ist es eine Zahl.“
- Grafikadventure: Türzustand steht nicht mehr fest in der Raumbeschreibung, Kreise (Kopf, Sonne,
  Baumkrone, Schlüsselring) werden über `KreisUm` um ihre Mitte gezeichnet, Befehle verstehen
  Umgangssprache (`nimm`, `mach auf`, `geh`) und Umlaut-Umschreibungen.

## 0.6.1
- **Behoben:** `web.Ergebnis.ausgabe` zerbrach, sobald ein Programm zeichnete — es packte jeden
  Verlaufseintrag in genau zwei Teile aus, Striche haben aber sieben und `("loeschen",)` nur einen.
- Neues Programm `20_grafisches_adventure.klar`: Textadventure mit gezeichnetem Raum, Türen
  (gold = offen, rot = verschlossen) und sichtbaren Gegenständen.
- Spielwiese: Knopf **✎ Neu** für ein leeres Blatt, gleich neben der Beispielauswahl.

## 0.6.0
- **„Zeig mir das in Python"** (`klarsatz/nach_python.py`): übersetzt ein Programm in lesbares Python.
  `python3 -m klarsatz --nach-python programm.klar`, in der Spielwiese der Knopf *Als Python*.
  Zeichnen wird zu `turtle`, Dinge werden zu `@dataclass`, Listen rechnen von 1 auf 0 um.
  Ziel ist Lesbarkeit, nicht Gleichheit bis ins Zeichen: Wo Klarsatz anders rechnet, steht ein
  Hinweis im Kopf des erzeugten Programms. Für vier Beispielprogramme prüft ein Test, dass Python
  **dieselbe Ausgabe** liefert wie Klarsatz.
- **Spielwiese:** *Leeres Blatt* ganz oben in der Beispielauswahl; die Fläche wächst, sobald gezeichnet
  wird, damit unter der Leinwand genug zum Lesen bleibt.
- Beispiele: `17_warenkorb.klar`, `15_baum.klar`, `19_textadventure.klar`. Der Hund heißt jetzt Rocco.
- Doku: „Häufige Stolperfallen", Warnung zum vergessenen `gleich`, Aufgabennamen sind ein Wort.

## 0.5.0
- **`Warte n Sekunden.`** und **`Lösche die Zeichnung.`** — damit wird aus einem Standbild eine
  laufende Anzeige: *Löschen → Zeichnen → Warten* in einer Endlosschleife. Gewartete Zeit zählt nicht
  als Rechenzeit (sonst bräche die Zeitgrenze jede Uhr ab); neue Grenze `warte` deckelt die Pause,
  Tests laufen mit `Grenzen(warte=0)` in voller Geschwindigkeit.
- **Mitlesen statt Abwarten:** `web.laufe(…, melde=…)` reicht jeden Verlaufseintrag sofort weiter.
  Der Worker meldet ihn an die Spielwiese, die Ausgaben und Striche zeigt, während das Programm läuft.
  Ein endloses Programm bleibt dadurch nicht mehr stumm. Der Verlauf im Ergebnis wird dabei auf die
  jüngsten 5000 Einträge begrenzt.
- **Spielwiese:** Leinwand und Ausgabe füllen sich live, der Knopf wird während eines Laufs zu
  *Anhalten* und bricht ab, das Zeitlimit wirkt als Wachhund (Lebenszeichen setzen es zurück),
  und ganz oben in der Beispielauswahl steht jetzt ein **leeres Blatt** zum Selberschreiben.
- **Behoben:** Beim Neustart des Hintergrundprozesses blieben die Zeitlimit-Wächter der alten
  Aufträge stehen und beendeten später den frisch gestarteten Prozess mitten im Laden.
- **Prüfer:** kennt die Zeichen- und Zeitsätze (sonst galten dort gelesene Namen als unbenutzt) und
  hält eine Endlosschleife mit `Warte` für Absicht statt für einen Fehler.
- **Uhr** (`16_uhr.klar`) läuft jetzt wirklich. Neue Programme: `17_warenkorb.klar`,
  `15_baum.klar` (rekursiver Baum), `19_textadventure.klar`.
- **Dokumentation:** neuer Abschnitt „Häufige Stolperfallen", Warnung zum vergessenen `gleich`,
  Hinweis, dass ein Aufgabenname ein einzelnes Wort ist, und die beiden Aufrufarten klar getrennt.

## 0.4.1
- **Browser-Tests laufen jetzt auf dem Raspberry Pi** (`playwright install chromium`, arm64-Build).
  Der bisher offene Testteil nach einem Zeitlimit-Abbruch ist geklärt und wieder aktiv; neu geprüft
  werden außerdem die Leinwand (erscheint, malt wirklich, bleibt sonst weg) und die Option `pyodideUrl`.
  403 Tests, davon 21 im Browser.
- **Füllwörter** werden wie Artikel überlesen: `dir`, `dich`, `mir`, `mich`, `uns`, `sich`, `bitte`.
  Damit sind `Merke dir 5 als Zahl.`, `Zeige mir die Summe.` und `Bitte zeige n.` erlaubt — sie bedeuten
  dasselbe wie die knappe Schreibweise. `Drehe dich um 90 Grad` braucht dadurch keinen Sonderfall mehr
  im Parser.
- Neues Beispiel `schreibweise.klar` („So darf man schreiben"): führt Artikel, Füllwörter,
  Groß-/Kleinschreibung, Umlaute und mehrzeilige Sätze an einem Stück vor.
- Die Einsteigerprogramme (`hallo.klar`, 01–03) sprechen jetzt durchgängig die gesprochene Form
  (`Merke dir …`, `und merke dir die Antwort`); ab Programm 04 bleibt es bei der knappen Schreibweise.

## 0.4.0
- **Uhrzeit und Datum:** `die aktuelle Stunde`, `… Minute`, `… Sekunde`, `der aktuelle Tag`,
  `… Monat`, `das aktuelle Jahr`. Die Zeit wird je Lauf einmal abgelesen, damit eine Uhr stimmig bleibt;
  für Tests ist sie austauschbar (`Interpreter(uhr=…)`).
- Neues Programm `16_uhr.klar`: Analoguhr mit Zifferblatt und drei Zeigern.

## 0.3.0
- **Zeichnen:** `Gehe … Schritte vor/zurück.`, `Drehe dich um … Grad nach links/rechts.`,
  `Hebe/Senke den Stift.`, `Gehe zur Mitte.`, `Nimm die Farbe "…".`, `Nimm die Strichstärke n.`
  Der Stift startet in der Mitte und schaut nach oben; dreizehn Farben mit deutschen Namen,
  Tippfehler bekommen einen Vorschlag.
- Der Interpreter **malt nicht selbst**: Striche gehen als `("linie", x1, y1, x2, y2, Farbe, Breite)`
  an einen Rückruf (`Interpreter(zeichne=…)`), sonst in `interpreter.zeichnung`. Die Web-Schnittstelle
  hängt sie in den Verlauf, die Spielwiese malt sie auf eine Leinwand, die Kommandozeile schreibt
  mit `--bild bild.svg` eine SVG-Datei (`klarsatz/zeichnung.py`).
- Neue Grenze `striche` (Voreinstellung 200 000, streng 20 000).
- Neue Programme: `12_vielecke.klar`, `13_spirale.klar`, Beispiel `zeichnen.klar`.

## Nachgetragen (zwischen 0.2.0 und 0.3.0)
- **MIT-Lizenz** (`LICENSE`) — Klarsatz darf benutzt, geändert und weitergegeben werden.
- **Download-Archiv:** `tools/baue_archiv.py` schnürt ein ZIP zum Ausprobieren am eigenen Rechner
  und hält die Angaben auf der Webseite aktuell.
- **Umbenannt: Klartext → Klarsatz** (18.09.2026). Der Name „Klartext" ist anderweitig vergeben.
  Betroffen: Paket `klarsatz/`, Aufruf `python3 -m klarsatz`, Projektordner `/home/pi/klarsatz`,
  Spielwiesen-Dateien `klarsatz-*`, VS-Code-Erweiterung `vscode-klarsatz`, Umgebungsvariable
  `KLARSATZ_KEIN_BROWSER`, Fehlerklasse `KlarsatzFehler`, Webseite unter `/klarsatz/`.
  Die Dateiendung der Programme bleibt **`.klar`**.
- **Spielwiese:** neue Option `pyodideUrl` für `erstelle()` – die Pyodide-Laufzeit kann von der eigenen Seite
  ausgeliefert werden statt vom CDN. Voreinstellung unverändert (jsdelivr).
- **Werkzeuge:** `tools/veroeffentliche_spielwiese.py` (Spielwiese in den Webordner bringen) und
  `tools/pruefe_webseite.py` (alle Codebeispiele der Webseite gegen den Interpreter laufen lassen).
- **Webseite** unter https://www.ruthner.at/klarsatz/ – siehe ÜBERGABE.md.

## 0.2.0
- **Paket** statt Einzeldatei: `klarsatz/` (lexer, parser, interpreter, werte, fehler, grenzen, dateisystem, pruefer,
  formatierer, repl, web, hervorhebung, sprachdaten, cli). Start mit `python3 -m klarsatz` oder `pip install -e .`.
- **Härtung:** Grenzen (Schritte, Zeit, Text, Liste, Zahl, Ausgabe, Eingabe, Programmgröße, Verschachtelung),
  Dateizugriff standardmäßig nur im Arbeitsordner (`--dateien-ordner`, `--ohne-dateien`, `--dateien-ueberall`),
  Absturzschutz (kein Python-Traceback mehr bei tiefen Klammern, riesigen Zahlen, selbstenthaltenden Listen).
- **Fehlermeldungen:** Spalte mit ^^^-Markierung, Aufrufkette bei Fehlern in Aufgaben, Namenskollisionen
  (Variable/Aufgabe) schon beim Lesen, deutsche Meldungen statt Python-Texten.
- **Prüfmodus** `--pruefe`: unbekannte Namen mit „Meintest du …?“, Endlosschleifen, unerreichbarer Code,
  Konstanten, Dinge/Felder, Aufgaben ohne Rückgabe, lokale Variable verdeckt globale u. v. m.
- **Formatierer** `--formatiere [--ersetzen]`.
- **Konsole** (REPL): `python3 -m klarsatz` ohne Datei; Ausdrücke, mehrzeilige Blöcke, `:hilfe`, `:laden` …
- **Sprache neu:** negative Zahlen (`-5`), Tabellen (`Erstelle Tabelle`, `Trage … ein`, `Wert für … in …`),
  `Kopiere`, `Verkettet von`, `Zeichen A bis B von`, `Ersetze … durch … in`, `Zahlenwert von`,
  `zufälliges Element von`, `Entferne Element N / das erste / das letzte`, Klammern in Bedingungen,
  `Gerundet … auf N Stellen` und `Formatiert …` (kaufmännisch), Typtests (`eine Zahl`, `keine Tabelle` …),
  `Zufallszahl von … bis …`, `--seed`.
- **Änderung mit Wirkung:** `Zähle von 5 bis 1` läuft jetzt **nie** (früher automatisch rückwärts);
  rückwärts zählt man mit `rückwärts`.
- **Web:** `klarsatz/web.py` (Abspielen statt blockierendem `input`), `playground/` (Spielwiese mit Pyodide,
  Web-Worker, Hervorhebung, Prüfen, Formatieren).
- **Editor:** VS-Code-Erweiterung, TextMate-Grammatik, Pygments-Lexer – erzeugt aus den Sprachdaten des Parsers.
- **Programme:** zwölf Beispielprogramme in `programme/` (Taschenrechner … Kopfrechnen).

## 0.1.0
Erster Prototyp als Einzeldatei `klarsatz.py`.
