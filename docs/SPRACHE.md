# Klarsatz – Sprachdefinition (Prototyp 0.1)

Klarsatz ist eine *kontrollierte natürliche Sprache*: Programme lesen sich wie deutsche Anweisungen,
folgen aber festen Satzmustern. Der Interpreter (Paket `klarsatz/`, reines Python 3) besteht aus
**Lexer → Satzmuster-Parser → AST → Interpreter**.

```
python3 -m klarsatz beispiele/fizzbuzz.klar
python3 -m klarsatz programm.klar --ohne-dateien --limit 1000000 --seed 42
python3 -m klarsatz              # interaktive Konsole
python3 -m unittest discover -s tests -t .
```

## 1. Grundregeln

| Regel | Beispiel |
|---|---|
| Ein Satz ist ein Befehl und endet mit einem **Punkt**. | `Zeige "Hallo".` |
| Befehle stehen im **Imperativ** am Satzanfang. | `Merke`, `Setze`, `Zeige`, `Füge … hinzu` |
| **Blöcke** beginnen mit `:` und enden mit `Ende.` | `Wiederhole 3 Mal: … Ende.` |
| **Artikel** (der, die, das, den, dem, ein, eine, einen …) werden überlesen. | `Zeige die Summe.` = `Zeige Summe.` |
| **Füllwörter** (dir, dich, mir, mich, uns, sich, bitte) ebenso. | `Merke dir 5 als Zahl.` = `Merke 5 als Zahl.` |
| Groß-/Kleinschreibung ist egal, `ä ö ü ß` = `ae oe ue ss`. | `Zähle` = `zaehle` = `ZAEHLE` |
| **Namen werden nicht gebeugt** (Ausnahme: Feldnamen, siehe 10). | `Zahl`, nicht „der Zahl“ |
| Zeilenumbrüche und Einrückung sind bedeutungslos (Einrückung dient nur dem Lesen). | |
| Kommentar: `Anmerkung:` bis zum Zeilenende. | `Anmerkung: erklärt etwas.` |
| Texte: `"…"` oder `„…“`. Zahlen: `42`, `3.14` (Punkt, keine Dezimalkomma-Eingabe). | |
| Ausgabe von Kommazahlen erfolgt deutsch: `3.5` wird als `3,5` angezeigt. | |

Wahrheitswerte: `wahr`, `falsch`. Klammern `( )` gibt es nur für Rechnungen und Argumente.

## 2. Ausgabe und Eingabe

```
Zeige "Hallo Welt".
Zeige "Summe: " und Summe.                    Anmerkung: 'und' klebt Teile direkt aneinander
Frage "Wie heißt du?" und merke die Antwort als Name.
```
Eine Antwort, die wie eine Zahl aussieht, wird zur Zahl. Einen einzelnen Buchstaben eines Textes
bekommst du mit `Element 1 von Antwort` (Zahl-Antworten führen dabei zu einem Fehler, den man mit
`Versuche` abfangen kann – siehe `programme/08_zahlenraten_computer_raet.klar`).

## 3. Variablen

```
Merke 5 als Zahl.                 Anmerkung: anlegen (oder überschreiben)
Merke für immer 3.14159 als Pi.   Anmerkung: Konstante
Setze die Zahl auf 7.             Anmerkung: ändern (Name muss existieren)
Erhöhe die Zahl um 1.             Anmerkung: ohne 'um' wird um 1 erhöht
Verringere die Zahl um 2.
Verdopple die Zahl.
Halbiere die Zahl.
Verbinde "Hallo, " und Name zu Gruss.
```
Unbekannte Namen führen zu einer Fehlermeldung mit Vorschlag („Meintest du 'Summe'?“).

## 4. Rechnen

```
a plus b        a minus b        a mal b        a geteilt durch b        a hoch b
den Rest von a geteilt durch b
die Wurzel von x     der Betrag von x     die Länge von Text_oder_Liste
Kleinbuchstaben von Text     Großbuchstaben von Text
Abgerundet von x     Aufgerundet von x     Gerundet von x        Anmerkung: ergibt ganze Zahlen (2.5 -> 3)
Formatiert von x auf 2 Stellen                                    Anmerkung: ergibt Text: 3.14159 -> "3,14"
Zufallszahl von 1 bis 10                                          Anmerkung: ganze Zahl, beide Grenzen inklusive
minus 5
```
Punkt vor Strich, `hoch` bindet am stärksten. `geteilt durch` liefert eine ganze Zahl, wenn es aufgeht.
**Argumente** von `Wurzel von`, `Länge von` und Aufgaben sind einfache Werte – bei mehr Rechnung
Klammern setzen: `Wurzel von (a plus b)`.

## 5. Vergleiche und Logik

```
a gleich b        a nicht gleich b        a größer als b        a kleiner als b
a mindestens b    a höchstens b           a durch 3 teilbar     a nicht durch 3 teilbar
Liste enthält Wert          Text enthält Textstück
Antwort eine Zahl           Antwort keine Zahl          Antwort ein Text          Wert eine Liste
```
Das `ist` darf vor oder hinter dem Vergleich stehen: `Wenn a größer als 10 ist:` oder `Wenn a ist größer als 10:`.
`enthält` prüft bei Listen, ob ein Wert vorkommt, bei Texten, ob ein Textstück vorkommt:
`Wenn Vokale enthält Buchstabe, …` – verneint mit `Wenn nicht Vokale enthält Buchstabe ist:`.
`eine Zahl` / `keine Zahl` / `ein Text` / `eine Liste` prüfen den Typ – nützlich nach `Frage`,
denn Antworten, die wie Zahlen aussehen, sind Zahlen; alles andere ist Text.

Verknüpfen mit `und`, `oder`, `nicht` (**und** bindet stärker als **oder**). Texte werden nach deutscher
Reihenfolge verglichen (Äpfel < Birnen).

## 6. Bedingungen

Blockform:
```
Wenn die Zahl größer als 10 ist:
    Zeige "groß".
Sonst wenn die Zahl gleich 10 ist:
    Zeige "genau zehn".
Sonst:
    Zeige "klein".
Ende.
```
Kurzform (ein Satz, **kein** eigenes `Ende.`):
```
Wenn i durch 15 teilbar ist, zeige "FizzBuzz".
Sonst wenn i durch 3 teilbar ist, zeige "Fizz".
Sonst zeige i.
```

## 7. Schleifen

```
Wiederhole 5 Mal:                     … Ende.
Wiederhole solange n kleiner als 10 ist:   … Ende.
Zähle von 1 bis 10 mit i:             … Ende.       Anmerkung: nur aufwärts; ist Start > Ziel, läuft nichts
Zähle von 10 bis 1 rückwärts mit i:   … Ende.       Anmerkung: abwärts (statt "rückwärts" geht auch "abwärts")
Zähle von 0 bis 100 in Schritten von 10 mit i:  … Ende.
Für jedes Element in Einkauf:         … Ende.       Anmerkung: auch über Texte
Höre auf.        Anmerkung: Schleife verlassen
Mach weiter.     Anmerkung: nächster Durchlauf
```

## 8. Listen

```
Erstelle eine Liste namens Einkauf.
Erstelle eine Liste namens Zahlen mit 3 und 1 und 2.
Füge "Milch" zur Einkauf hinzu.
Entferne "Milch" aus Einkauf.
Sortiere Einkauf.                       Anmerkung: auch: Sortiere Einkauf absteigend.
Zeige das erste Element von Einkauf.    Anmerkung: auch: das letzte Element
Zeige Element 2 von Einkauf.            Anmerkung: gezählt wird ab 1
Zeige die Länge von Einkauf.
```
```
Teile Satz bei " " zu Woerter.       Anmerkung: Text in eine Liste von Texten zerlegen
Teile Inhalt bei "\n" zu Zeilen.     Anmerkung: \n = Zeilenumbruch
```
`Element Nr von Liste`: `Nr` darf eine Zahl, ein Name oder eine Rechnung in Klammern sein.

Zugriffe außerhalb der Liste sind **immer** ein Fehler mit klarer Meldung, nie ein stiller Fehlgriff.

## 9. Aufgaben (Funktionen)

```
Definiere Aufgabe Begrüße mit Name:
    Zeige "Hallo, " und Name.
Ende.

Definiere Aufgabe Summe von a und b:
    Gib a plus b zurück.
Ende.

Führe Begrüße mit "Wolfgang" aus.          Anmerkung: als Befehl
Zeige Summe von 3 und 4.                   Anmerkung: als Wert; mehrere Argumente mit 'und'
```
`von` und `mit` sind austauschbar. Aufgaben dürfen sich selbst aufrufen und dürfen **vor** ihrer Definition
benutzt werden (die Parameterzahl wird vorab gelesen, so bleibt `und` eindeutig). Lokale Namen
sind außen unsichtbar; globale Namen sind lesbar. Maximal 150 ineinander verschachtelte Aufrufe.

## 10. Dinge (Strukturen)

```
Ein Hund hat einen Namen und ein Alter.
Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Rocco.
Zeige den Namen von Rocco.
Setze das Alter von Rocco auf 6.
```
Beim Erschaffen müssen **alle** Felder angegeben werden, ein Wert ist nie „einfach leer“.
Feldnamen dürfen leicht gebeugt sein (`Name` = `Namen`, `Zahl` = `Zahlen`).

## 11. Fehler, Zusicherungen, Dateien

```
Versuche:
    Merke 10 geteilt durch 0 als x.
Bei Fehler:
    Zeige "Problem: " und Fehlermeldung.     Anmerkung: 'Fehlermeldung' füllt die Sprache selbst
Ende.

Stelle sicher, dass die Zahl größer als 0 ist.   Anmerkung: bricht sonst ab

Lies die Datei "daten.txt" als Inhalt.
Schreibe "Text" in die Datei "out.txt".
```

## 12. Wörter, die nicht als Namen taugen

`ist sind und oder nicht plus minus mal geteilt durch hoch als auf um von mit zu aus in bis hinzu wenn sonst
ende solange dass hat bei gleich größer kleiner mindestens höchstens teilbar wahr falsch jedes jede jeden zurück enthält keine`

## 13. Sicherheitsvorkehrungen des Prototyps

* `--limit N`: bricht nach N Schritten ab (Endlosschleifen). Das Limit lässt sich **nicht** mit `Versuche` abfangen.
* `--ohne-dateien`: `Lies`/`Schreibe` sind gesperrt.
* `--seed N`: macht Zufallszahlen reproduzierbar (für Tests).
* Rekursionstiefe und Größe von Potenzen sind begrenzt.
* Es gibt kein `eval`, kein Nachladen von Code und keinen Zugriff auf Python-Funktionen.

Das ist ein **Lernprojekt**: Der Interpreter ist keine Sandbox für fremden, nicht vertrauenswürdigen Code.

## 14. Bekannte Grenzen und nächste Schritte

* Kein Dezimalkomma in Zahlen*eingaben* (Komma trennt Satzteile). Ausgabe ist deutsch.
* Die Kurzform von `Wenn … , …` führt genau **einen** Satz aus; für mehrere Befehle die Blockform nehmen.
* Bedingungen lassen sich nicht klammern; `und` bindet vor `oder`.
* Beim Anzeigen eines Dings steht der Feldname so, wie er in der Definition stand (`Namen: Rocco`).
* Es gibt (noch) keine Möglichkeit, eine Liste zu einem Text zusammenzufügen; das geht mit `Für jedes` und `Verbinde`.
* Noch offen aus dem Entwurf: `Falls vorhanden:` (Optionalwerte), `Diese Aufgabe darf nur lesen`
  (Fähigkeiten), ein Bytecode-Compiler.


## Neu ab Version 0.2

**Negative Zahlen:** `Zeige -5 plus 2.` (nur direkt vor einer Zahl; sonst `minus`).

**Tabellen** (Schlüssel → Wert; Schlüssel sind Texte oder Zahlen, die Reihenfolge bleibt erhalten):
```
Erstelle eine Tabelle namens Preise mit "Apfel" als 3 und "Birne" als 2.
Trage "Kiwi" mit 5 in Preise ein.
Zeige Wert für "Apfel" in Preise.
Wenn Preise enthält "Kiwi", zeige "ja".
Entferne "Birne" aus Preise.
Für jedes Frucht in Preise:            Anmerkung: geht durch die Schlüssel
    Zeige Frucht und ": " und Wert für Frucht in Preise.
Ende.
```

**Listen und Texte:**
```
Kopiere Einkauf als Sicherung.                 Anmerkung: echte Kopie (Listen sind sonst Verweise)
Zeige Verkettet von Einkauf mit ", ".          Anmerkung: Liste -> Text
Zeige Zeichen 2 bis 4 von "Hallo".               Anmerkung: "all" (ab 1 gezählt); Elemente 2 bis 3 von Liste
Ersetze "Welt" durch "Klarsatz" in Text.
Zeige Zahlenwert von "3,5" plus 1.
Zeige ein zufälliges Element von Einkauf.
Entferne Element 2 aus Einkauf.   Entferne das erste Element aus Einkauf.   Entferne das letzte Element aus Einkauf.
Teile Satz bei " " zu Woerter.
```

**Spalten ausrichten** (für Tabellen — `Formatiert` setzt nur die Nachkommastellen):
```
Rechtsbündig von Wert auf 8 Zeichen        Linksbündig von Wert auf 8 Zeichen
```
Ist der Wert länger als die Breite, bleibt er ungekürzt stehen.

**Winkelfunktionen** (in **Grad**, passend zu `Drehe dich um 90 Grad`):
```
der Sinus von 30          0,5          der Arkussinus von 0.5       30
der Kosinus von 60        0,5          der Arkuskosinus von 1        0
der Tangens von 45        1            der Arkustangens von 1       45
```
`Cosinus` geht auch mit C. Rechenrauschen wird weggerundet: `Kosinus von 90` ist glatt `0`.
Der Tangens von 90 oder 270 Grad ist nicht bestimmt und meldet einen Fehler.

**Zahlen:** `Zufallszahl von 1 bis 10`, `Abgerundet/Aufgerundet/Gerundet von x` (kaufmännisch),
`Gerundet von x auf 2 Stellen`, `Formatiert von x auf 2 Stellen` (Text mit Komma: `3,14`).

**Bedingungen:** Klammern (`Wenn (a kleiner als 1 oder b gleich 2) und c gleich 3 ist:`), Typtests
(`Antwort eine Zahl ist`, `keine Zahl`, `ein Text`, `eine Liste`, `eine Tabelle`), `Liste enthält Wert`.

**Lernstufen** (`--stufe N`): Wer anfängt, hat mit `Zeige`, `Frage` und `Merke` schon ein Programm –
alles andere wartet. Greift man zu früh nach einem Wort, sagt Klarsatz freundlich, wo es hingehört
(„Das kommt später: 'Wenn' lernst du in Stufe 3"). Die Stufen folgen den Lektionen des Tutorials:

| Stufe | Name | Neu darin |
|---|---|---|
| 1 | Zeigen, fragen, merken | `Zeige`, `Frage`, `Merke` |
| 2 | Rechnen | `plus`, `mal`, `Setze`, `Erhöhe`, `Wurzel von`, `Gerundet von` |
| 3 | Entscheiden | `Wenn`, `Sonst`, `gleich`, `größer als`, `wahr`, `falsch` |
| 4 | Wiederholen | `Wiederhole`, `Zähle`, `Für jedes`, `Höre auf` |
| 5 | Eigene Bausteine | `Definiere Aufgabe`, `Gib … zurück`, `Führe … aus` |
| 6 | Listen und Tabellen | `Erstelle`, `Füge hinzu`, `Element n von`, `Sortiere`, `Teile` |
| 7 | Alles | Dinge, `Versuche`, Dateien, Zeichnen, Uhrzeit |

`--stufen` zeigt alle Wörter je Stufe. Ohne `--stufe` ist nichts gesperrt. In der Spielwiese steht
die Auswahl oben; ein geladenes Beispiel setzt sie zurück, denn Beispiele soll man immer ansehen
können. Die Einteilung steht in `sprachdaten.py` neben den Wortgruppen, geprüft wird sie in
`stufen.py`.

**Werkzeuge:** `--pruefe` (findet Fehler, ohne auszuführen), `--formatiere [--ersetzen]`,
`--nach-python` (dasselbe Programm als lesbares Python), `--tokens`, `--ast`,
Konsole ohne Datei. Grenzen und Dateien: siehe SICHERHEIT.md.

**Namen:** Eine Variable darf nicht wie eine Aufgabe heißen. `hoch`, `mal`, `plus` … sind reserviert.

## Zeichnen (neu)

Ein Stift steht in der **Mitte** und schaut **nach oben**. Er zieht eine Linie, wenn er unten ist.

```
Gehe 100 Schritte vor.               Anmerkung: auch: zurück
Drehe dich um 90 Grad nach rechts.   Anmerkung: auch: nach links ('dich' und 'nach' sind freiwillig)
Hebe den Stift.                      Anmerkung: bewegen, ohne zu malen
Senke den Stift.
Nimm die Farbe "gold".               Anmerkung: rot blau grün gelb gold orange lila rosa türkis braun grau schwarz weiß
Nimm die Strichstärke 3.             Anmerkung: 1 bis 50
Gehe zur Mitte.                      Anmerkung: zurück zum Start, wieder nach oben schauend
```

Ein Quadrat ist damit vier Sätze lang:
```
Wiederhole 4 Mal:
    Gehe 100 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```

**Bewegung:**
```
Lösche die Zeichnung.                  Anmerkung: Fläche leeren, Stift bleibt stehen
Warte 1 Sekunde.                       Anmerkung: 0 bis 60 s; zählt nicht als Rechenzeit
Wiederhole dieses Programm jede Sekunde.   Anmerkung: Kurzform: ganzes Programm im Takt neu
```
Eine laufende Anzeige ist damit eine Endlosschleife aus *Löschen → Zeichnen → Warten*. Der Browser zeigt
Ausgaben und Striche, sobald sie entstehen — ein Programm muss also nicht enden, um etwas zu zeigen.

**Wo das Bild entsteht:** Der Interpreter malt nicht selbst — er meldet nur Striche. Im Browser nimmt die
Spielwiese sie auf eine Leinwand, auf der Kommandozeile schreibt `--bild bild.svg` sie in eine SVG-Datei.
Ein Programm ohne Zeichenfläche läuft trotzdem, es entsteht dann eben kein Bild.

## Uhrzeit und Datum (neu)

```
Merke die aktuelle Stunde als h.     Anmerkung: 0 bis 23
die aktuelle Minute                  die aktuelle Sekunde
der aktuelle Tag                     der aktuelle Monat        das aktuelle Jahr
```
Die Zeit wird **je Lauf einmal** abgelesen: Innerhalb eines Programms passen Stunde, Minute und Sekunde
immer zusammen — eine Uhr kann also nicht zwischen zwei Zeigern springen. Wer Zeit *und* `Frage` benutzt,
sollte wissen, dass die Web-Schnittstelle das Programm nach jeder Antwort neu abspielt und die Zeit dabei
neu abliest.

Eine Analoguhr ist damit ein kurzes Programm — siehe `programme/16_uhr.klar`:
```
Merke die aktuelle Minute als Minute.
Gehe zur Mitte.
Drehe dich um Minute mal 6 Grad nach rechts.   Anmerkung: 360 Grad / 60 Minuten = 6
Gehe 100 Schritte vor.
```
