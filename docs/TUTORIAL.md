# Klarsatz lernen

Elf kurze Lektionen. Am Ende hast du ein kleines Spiel gebaut.

Du brauchst nichts zu installieren: Öffne die [Spielwiese](https://www.ruthner.at/klarsatz/spielplatz.html),
wähle oben **Leeres Blatt** und tippe mit. Wer Klarsatz auf dem eigenen Rechner hat, schreibt die
Programme in eine Datei `meins.klar` und startet sie mit `python3 -m klarsatz meins.klar`.

Jedes Beispiel hier läuft wirklich. Die Ausgaben darunter sind nicht abgetippt, sondern werden bei
jedem Testlauf neu ausgerechnet und verglichen — was hier steht, stimmt also.

| | Lektion | Darum geht es |
|---|---|---|
| 1 | [Der erste Satz](#lektion-1--der-erste-satz) | Etwas anzeigen |
| 2 | [Sich etwas merken](#lektion-2--sich-etwas-merken) | Variablen und Rechnen |
| 3 | [Fragen stellen](#lektion-3--fragen-stellen) | Eingaben entgegennehmen |
| 4 | [Entscheiden](#lektion-4--entscheiden) | Wenn, Sonst |
| 5 | [Wiederholen](#lektion-5--wiederholen) | Schleifen |
| 6 | [Viele Dinge auf einmal](#lektion-6--viele-dinge-auf-einmal) | Listen |
| 7 | [Nachschlagen](#lektion-7--nachschlagen) | Tabellen |
| 8 | [Eigene Befehle](#lektion-8--eigene-befehle) | Aufgaben |
| 9 | [Eigene Dinge](#lektion-9--eigene-dinge) | Strukturen |
| 10 | [Wenn etwas schiefgeht](#lektion-10--wenn-etwas-schiefgeht) | Fehler abfangen |
| 11 | [Ein Spiel bauen](#lektion-11--ein-spiel-bauen) | Alles zusammen |

---

## Lektion 1 — Der erste Satz

Ein Klarsatz-Programm ist eine Liste von Sätzen. Jeder Satz ist ein Befehl, beginnt mit einem
Befehlswort und endet mit einem **Punkt** — wie im Deutschen.

```klar
Zeige "Hallo Welt".
```
```ausgabe
Hallo Welt
```

Der Punkt am Ende ist Pflicht. Vergisst du ihn, sagt Klarsatz dir das:

> Ich verstehe das Programm nicht (Zeile 1): Hier fehlt ein Punkt am Satzende.

Mehrere Sätze stehen untereinander und laufen der Reihe nach:

```klar
Zeige "Guten Morgen.".
Zeige "Heute ist ein guter Tag zum Programmieren.".
```
```ausgabe
Guten Morgen.
Heute ist ein guter Tag zum Programmieren.
```

Mit `und` klebst du mehrere Teile zu einer Zeile zusammen:

```klar
Zeige "Drei mal vier ist " und 3 mal 4 und ".".
```
```ausgabe
Drei mal vier ist 12.
```

Und wenn du dir selbst etwas notieren willst, ohne dass es ausgeführt wird, schreibst du eine
**Anmerkung**. Alles dahinter bis zum Zeilenende ist nur für Menschen:

```klar
Anmerkung: Dieses Programm grüßt.
Zeige "Hallo".          Anmerkung: auch am Satzende erlaubt
```
```ausgabe
Hallo
```

**Zum Selbermachen:** Lass das Programm drei Zeilen über dich ausgeben — Name, Wohnort, Lieblingsfarbe.

---

## Lektion 2 — Sich etwas merken

Damit ein Programm rechnen kann, muss es sich Werte merken. Das macht `Merke`:

```klar
Merke 5 als Zahl.
Zeige Zahl.
```
```ausgabe
5
```

`Merke 5 als Zahl` heißt: *Merk dir den Wert 5 unter dem Namen „Zahl".* Den Namen darfst du frei
wählen. Er steht danach überall dort, wo sonst der Wert stünde.

Klarsatz überliest Artikel und Füllwörter. Diese drei Sätze bedeuten dasselbe:

```klar
Merke 5 als Zahl.
Merke dir 5 als Zahl.
Merke dir die 5 als Zahl.
Zeige Zahl.
```
```ausgabe
5
```

Schreib also so, wie es sich gut liest.

### Rechnen

```klar
Merke 7 als a.
Merke 3 als b.
Zeige a plus b.
Zeige a minus b.
Zeige a mal b.
Zeige a geteilt durch b.
```
```ausgabe
10
4
21
2,33333333333
```

Zwei Dinge fallen auf: Klarsatz schreibt Kommazahlen **deutsch**, mit Komma. Und `geteilt durch`
liefert eine glatte ganze Zahl, wenn es aufgeht — `6 geteilt durch 3` ist `2`, nicht `2,0`.

Es gibt noch mehr:

```klar
Zeige die Wurzel von 144.
Zeige den Rest von 17 geteilt durch 5.
Zeige 2 hoch 10.
Zeige Gerundet von 2.7.
Zeige Formatiert von 3.14159 auf 2 Stellen.
```
```ausgabe
12
2
1024
3
3,14
```

### Werte ändern

Ist ein Name erst einmal angelegt, änderst du ihn mit `Setze`, `Erhöhe` oder `Verringere`:

```klar
Merke 10 als Punkte.
Erhöhe Punkte um 5.
Zeige Punkte.
Verringere Punkte um 3.
Zeige Punkte.
Verdopple Punkte.
Zeige Punkte.
Setze Punkte auf 0.
Zeige Punkte.
```
```ausgabe
15
12
24
0
```

Was sich nie ändern soll, merkst du **für immer**. Ein späterer Änderungsversuch ist dann ein Fehler:

```klar
Merke für immer 3.14159 als Pi.
Zeige Pi.
```
```ausgabe
3,14159
```

**Zum Selbermachen:** Rechne aus, wie viele Sekunden ein Tag hat. Merke dir 24 als Stunden, rechne
weiter und zeige das Ergebnis mit einem erklärenden Text davor.

---

## Lektion 3 — Fragen stellen

Ein Programm wird erst lebendig, wenn es fragt. Dafür gibt es `Frage`:

```klar
Frage "Wie heißt du? " und merke die Antwort als Name.
Zeige "Hallo, " und Name und "!".
```
```eingabe
Wolfgang
```
```ausgabe
Hallo, Wolfgang!
```

Der Satz macht zwei Dinge auf einmal: Er zeigt die Frage an und legt die Antwort unter einem Namen
ab. Das Leerzeichen am Ende von `"Wie heißt du? "` sorgt dafür, dass die Eingabe nicht direkt am
Fragezeichen klebt.

### Zahl oder Text?

Sieht eine Antwort wie eine Zahl aus, wird sie zur Zahl — und man kann mit ihr rechnen:

```klar
Frage "Wie alt bist du? " und merke die Antwort als Alter.
Zeige "In zehn Jahren bist du " und Alter plus 10 und ".".
```
```eingabe
40
```
```ausgabe
In zehn Jahren bist du 50.
```

Alles andere bleibt Text. Ob das eine oder das andere vorliegt, kannst du prüfen — das brauchen wir
in der nächsten Lektion:

```klar
Frage "Sag eine Zahl: " und merke die Antwort als Eingabe.
Wenn Eingabe eine Zahl ist:
    Zeige "Damit kann ich rechnen.".
Sonst:
    Zeige "Das ist keine Zahl.".
Ende.
```
```eingabe
sieben
```
```ausgabe
Das ist keine Zahl.
```

**Zum Selbermachen:** Frage nach zwei Zahlen und zeige ihre Summe.

---

## Lektion 4 — Entscheiden

`Wenn` führt einen Block nur aus, wenn eine Bedingung zutrifft. Der Block beginnt mit einem
Doppelpunkt und endet mit `Ende.`

```klar
Merke 15 als Zahl.
Wenn Zahl größer als 10 ist:
    Zeige "Das ist eine große Zahl.".
Ende.
```
```ausgabe
Das ist eine große Zahl.
```

Mit `Sonst` sagst du, was andernfalls passieren soll, mit `Sonst wenn` fragst du weiter:

```klar
Merke 7 als Note.
Wenn Note mindestens 9 ist:
    Zeige "Sehr gut".
Sonst wenn Note mindestens 7 ist:
    Zeige "Gut".
Sonst:
    Zeige "Geht besser".
Ende.
```
```ausgabe
Gut
```

### Die Vergleiche

| Schreibweise | Bedeutung |
|---|---|
| `a gleich b` | gleich — **nicht** `a ist b` |
| `a nicht gleich b` | ungleich |
| `a größer als b`, `a kleiner als b` | größer, kleiner |
| `a mindestens b`, `a höchstens b` | größer-gleich, kleiner-gleich |
| `a durch 3 teilbar` | ohne Rest teilbar |
| `Liste enthält Wert`, `Text enthält Textstück` | kommt darin vor |

Das Wörtchen **`gleich` ist Pflicht**. `Wenn Name "Anna" ist:` versteht Klarsatz nicht — es muss
`Wenn Name gleich "Anna" ist:` heißen.

Mehrere Bedingungen verknüpfst du mit `und`, `oder` und `nicht`:

```klar
Merke 25 als Alter.
Merke wahr als Hat_Zeit.
Wenn Alter mindestens 18 ist und Hat_Zeit gleich wahr ist:
    Zeige "Darf mitkommen.".
Ende.
```
```ausgabe
Darf mitkommen.
```

### Die Kurzform

Wenn nur **ein** Satz folgt, geht es kürzer — mit Komma statt Doppelpunkt, und ohne `Ende.`

```klar
Merke 4 als i.
Wenn i durch 2 teilbar ist, zeige "gerade".
Sonst zeige "ungerade".
```
```ausgabe
gerade
```

**Zum Selbermachen:** Frage nach einer Zahl und sage, ob sie negativ, null oder positiv ist.

---

## Lektion 5 — Wiederholen

Die einfachste Schleife zählt einfach mit:

```klar
Wiederhole 3 Mal:
    Zeige "Hallo".
Ende.
```
```ausgabe
Hallo
Hallo
Hallo
```

Brauchst du die laufende Nummer, nimm `Zähle`:

```klar
Zähle von 1 bis 5 mit i:
    Zeige i und " mal 7 ist " und i mal 7.
Ende.
```
```ausgabe
1 mal 7 ist 7
2 mal 7 ist 14
3 mal 7 ist 21
4 mal 7 ist 28
5 mal 7 ist 35
```

`Zähle` kann auch rückwärts und in Schritten:

```klar
Zähle von 10 bis 1 rückwärts mit i:
    Zeige i.
Ende.
Zeige "Start!".
```
```ausgabe
10
9
8
7
6
5
4
3
2
1
Start!
```

Weißt du vorher nicht, wie oft es sein wird, nimm `Wiederhole solange`:

```klar
Merke 1 als Zahl.
Wiederhole solange Zahl kleiner als 100 ist:
    Verdopple Zahl.
Ende.
Zeige "Erste Zweierpotenz über 100: " und Zahl.
```
```ausgabe
Erste Zweierpotenz über 100: 128
```

Vorsicht: Wenn die Bedingung nie falsch wird, läuft die Schleife ewig. In der Spielwiese bricht
Klarsatz dann von selbst ab — auf dem eigenen Rechner hilft Strg+C.

Aus einer Schleife kommst du mit `Höre auf.` heraus, und mit `Mach weiter.` springst du zum
nächsten Durchlauf:

```klar
Zähle von 1 bis 10 mit i:
    Wenn i durch 2 teilbar ist, mach weiter.
    Wenn i größer als 7 ist, höre auf.
    Zeige i.
Ende.
```
```ausgabe
1
3
5
7
```

**Zum Selbermachen:** Zeige das kleine Einmaleins von 1 bis 10 — eine Zeile pro Zahl.

---

## Lektion 6 — Viele Dinge auf einmal

Eine **Liste** hält viele Werte unter einem Namen:

```klar
Erstelle eine Liste namens Einkauf.
Füge "Milch" zu Einkauf hinzu.
Füge "Brot" zu Einkauf hinzu.
Füge "Äpfel" zu Einkauf hinzu.
Zeige Einkauf.
Zeige "Das sind " und die Länge von Einkauf und " Dinge.".
```
```ausgabe
[Milch, Brot, Äpfel]
Das sind 3 Dinge.
```

Kürzer geht es beim Anlegen:

```klar
Erstelle eine Liste namens Zahlen mit 3 und 1 und 2.
Sortiere Zahlen.
Zeige Zahlen.
Sortiere Zahlen absteigend.
Zeige Zahlen.
```
```ausgabe
[1, 2, 3]
[3, 2, 1]
```

### Durchgehen

`Für jedes` nimmt sich einen Eintrag nach dem anderen vor:

```klar
Erstelle eine Liste namens Tiere mit "Hund" und "Katze" und "Maus".
Für jedes Tier in Tiere:
    Zeige "Ich sehe einen " und Tier und ".".
Ende.
```
```ausgabe
Ich sehe einen Hund.
Ich sehe einen Katze.
Ich sehe einen Maus.
```

(Die Grammatik stimmt nicht ganz — Klarsatz beugt keine Wörter. Dafür weißt du jetzt, warum.)

### Einzelne Einträge

Gezählt wird **ab 1**, nicht ab 0:

```klar
Erstelle eine Liste namens Farben mit "rot" und "grün" und "blau".
Zeige das erste Element von Farben.
Zeige Element 2 von Farben.
Zeige das letzte Element von Farben.
Zeige Verkettet von Farben mit ", ".
```
```ausgabe
rot
grün
blau
rot, grün, blau
```

Greifst du daneben, bekommst du eine klare Meldung statt eines stillen Unfalls.

### Texte sind auch fast Listen

```klar
Merke "Hallo Welt" als Satz.
Zeige die Länge von Satz.
Zeige Zeichen 1 bis 5 von Satz.
Teile Satz bei " " zu Woerter.
Zeige Woerter.
Zeige Großbuchstaben von Satz.
```
```ausgabe
10
Hallo
[Hallo, Welt]
HALLO WELT
```

**Zum Selbermachen:** Lass den Benutzer drei Lieblingsessen eingeben, sammle sie in einer Liste,
sortiere sie und zeige sie durchnummeriert an.

---

## Lektion 7 — Nachschlagen

Eine **Tabelle** ordnet jedem Schlüssel einen Wert zu — wie ein Wörterbuch:

```klar
Erstelle eine Tabelle namens Preise mit "Apfel" als 3 und "Birne" als 2.
Trage "Kiwi" mit 5 in Preise ein.
Zeige Wert für "Apfel" in Preise.
Zeige Preise.
```
```ausgabe
3
{Apfel: 3, Birne: 2, Kiwi: 5}
```

Durchgehen kannst du sie auch — dabei bekommst du die Schlüssel:

```klar
Erstelle eine Tabelle namens Preise mit "Apfel" als 3 und "Birne" als 2.
Merke 0 als Summe.
Für jedes Frucht in Preise:
    Zeige Frucht und " kostet " und Wert für Frucht in Preise und " Euro.".
    Erhöhe Summe um Wert für Frucht in Preise.
Ende.
Zeige "Zusammen: " und Summe und " Euro.".
```
```ausgabe
Apfel kostet 3 Euro.
Birne kostet 2 Euro.
Zusammen: 5 Euro.
```

Ob ein Schlüssel vorkommt, fragst du mit `enthält`:

```klar
Erstelle eine Tabelle namens Preise mit "Apfel" als 3.
Wenn Preise enthält "Apfel", zeige "Äpfel haben wir.".
Wenn nicht Preise enthält "Mango" ist, zeige "Mangos leider nicht.".
```
```ausgabe
Äpfel haben wir.
Mangos leider nicht.
```

**Zum Selbermachen:** Bau ein kleines Wörterbuch Deutsch→Englisch und frage den Benutzer nach einem
Wort. Steht es drin, zeige die Übersetzung, sonst eine freundliche Meldung.

---

## Lektion 8 — Eigene Befehle

Wenn dasselbe mehrfach vorkommt, gib ihm einen Namen. Das ist eine **Aufgabe**:

```klar
Definiere Aufgabe Begrüße mit Name:
    Zeige "Hallo, " und Name und "!".
Ende.

Führe Begrüße mit "Anna" aus.
Führe Begrüße mit "Ben" aus.
```
```ausgabe
Hallo, Anna!
Hallo, Ben!
```

Der Name einer Aufgabe ist **ein einziges Wort** — `Begrüße`, nicht `Begrüße den Gast`. Mehrere
Wörter verbindest du mit einem Unterstrich: `Begrüße_Gast`.

### Aufgaben, die etwas zurückgeben

Mit `Gib … zurück` liefert eine Aufgabe ein Ergebnis. Dann benutzt du sie wie einen Wert:

```klar
Definiere Aufgabe Quadrat von x:
    Gib x mal x zurück.
Ende.

Zeige Quadrat von 7.
Zeige Quadrat von 3 plus Quadrat von 4.
```
```ausgabe
49
25
```

Mehrere Werte übergibst du mit `und`:

```klar
Definiere Aufgabe Rechteckflaeche von Breite und Hoehe:
    Gib Breite mal Hoehe zurück.
Ende.

Zeige Rechteckflaeche von 3 und 4.
```
```ausgabe
12
```

### Aufgaben dürfen sich selbst aufrufen

```klar
Definiere Aufgabe Fakultät von n:
    Wenn n kleiner als 2 ist:
        Gib 1 zurück.
    Ende.
    Gib n mal (Fakultät von (n minus 1)) zurück.
Ende.

Zeige Fakultät von 5.
```
```ausgabe
120
```

Wichtig ist der Ausstieg — hier `Wenn n kleiner als 2 ist`. Ohne ihn liefe die Aufgabe ewig, und
Klarsatz bricht nach 150 Ebenen ab.

**Zum Selbermachen:** Schreib eine Aufgabe `Grösser`, die von zwei Zahlen die größere zurückgibt.

---

## Lektion 9 — Eigene Dinge

Manchmal gehören mehrere Werte zusammen. Dann beschreibst du ein **Ding**:

```klar
Ein Hund hat einen Namen und ein Alter.

Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Rocco.
Zeige den Namen von Rocco.
Zeige Rocco.
```
```ausgabe
Rocco
Hund(Namen: Rocco, Alter: 5)
```

Der erste Satz sagt, **welche Felder** so ein Hund hat. Danach kannst du beliebig viele Hunde
erschaffen. Felder liest und änderst du mit `von`:

```klar
Ein Hund hat einen Namen und ein Alter.

Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Rocco.
Erhöhe das Alter von Rocco um 1.
Setze den Namen von Rocco auf "Rocco der Große".
Zeige den Namen von Rocco und " ist " und Alter von Rocco und " Jahre alt.".
```
```ausgabe
Rocco der Große ist 6 Jahre alt.
```

Dinge und Listen zusammen sind mächtig:

```klar
Ein Hund hat einen Namen und ein Alter.

Erstelle eine Liste namens Rudel.
Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Erster.
Erschaffe einen Hund mit Name "Bella" und Alter 2 als Zweiter.
Füge Erster zu Rudel hinzu.
Füge Zweiter zu Rudel hinzu.

Für jedes Hund in Rudel:
    Zeige Name von Hund und " (" und Alter von Hund und " Jahre)".
Ende.
```
```ausgabe
Rocco (5 Jahre)
Bella (2 Jahre)
```

**Zum Selbermachen:** Beschreibe ein Buch mit Titel, Autor und Seitenzahl. Leg drei Bücher an und
zeige nur die, die mehr als 200 Seiten haben.

---

## Lektion 10 — Wenn etwas schiefgeht

Manches lässt sich nicht verhindern: Eine Eingabe ist Unsinn, eine Datei fehlt, jemand teilt durch
null. Dafür gibt es `Versuche`:

```klar
Versuche:
    Merke 10 geteilt durch 0 als x.
    Zeige "Das klappt nie.".
Bei Fehler:
    Zeige "Da ist etwas schiefgegangen: " und Fehlermeldung.
Ende.
Zeige "Und das Programm läuft weiter.".
```
```ausgabe
Da ist etwas schiefgegangen: Durch null kann man nicht teilen.
Und das Programm läuft weiter.
```

Im `Bei Fehler`-Teil steht `Fehlermeldung` bereit — die füllt Klarsatz selbst.

Das ist besonders bei Eingaben nützlich. So fragt man so lange, bis etwas Brauchbares kommt:

```klar
Merke 0 als Zahl.
Wiederhole solange Zahl gleich 0 ist:
    Frage "Gib eine Zahl größer als 0 ein: " und merke die Antwort als Eingabe.
    Wenn Eingabe eine Zahl ist und Eingabe größer als 0 ist:
        Setze Zahl auf Eingabe.
    Sonst:
        Zeige "Das war keine Zahl größer als 0.".
    Ende.
Ende.
Zeige "Danke: " und Zahl.
```
```eingabe
abc
-5
12
```
```ausgabe
Das war keine Zahl größer als 0.
Das war keine Zahl größer als 0.
Danke: 12
```

Wenn eine Bedingung einfach gelten **muss**, sag es geradeheraus. `Stelle sicher` bricht ab, wenn
sie verletzt ist:

```klar
Definiere Aufgabe Wurzel_von_positiv von x:
    Stelle sicher, dass x mindestens 0 ist.
    Gib die Wurzel von x zurück.
Ende.

Zeige Wurzel_von_positiv von 16.
```
```ausgabe
4
```

**Zum Selbermachen:** Frage nach zwei Zahlen und teile die erste durch die zweite — aber so, dass
eine eingegebene 0 nicht das Programm abstürzen lässt.

---

## Lektion 11 — Ein Spiel bauen

Jetzt alles zusammen. Wir bauen Zahlenraten: Der Computer denkt sich eine Zahl aus, du rätst, er
sagt „höher" oder „tiefer" und zählt die Versuche.

Schritt für Schritt:

**1. Die Zahl auswürfeln.** `Zufallszahl von 1 bis 100` liefert eine ganze Zahl.

**2. So lange fragen, bis es stimmt.** Das ist `Wiederhole solange` aus Lektion 5.

**3. Vergleichen und Hinweis geben.** `Wenn` / `Sonst wenn` / `Sonst` aus Lektion 4.

**4. Versuche zählen.** Ein `Erhöhe` aus Lektion 2.

Zusammengesetzt:

```klar
Anmerkung: Zahlenraten – der Computer denkt sich etwas aus.

Merke Zufallszahl von 1 bis 100 als Gesucht.
Merke 0 als Versuche.
Merke falsch als Gefunden.

Zeige "Ich denke mir eine Zahl zwischen 1 und 100.".

Wiederhole solange Gefunden gleich falsch ist:
    Frage "Dein Tipp: " und merke die Antwort als Tipp.
    Wenn Tipp keine Zahl ist:
        Zeige "Das ist keine Zahl.".
        Mach weiter.
    Ende.
    Erhöhe Versuche um 1.
    Wenn Tipp kleiner als Gesucht ist:
        Zeige "Höher!".
    Sonst wenn Tipp größer als Gesucht ist:
        Zeige "Tiefer!".
    Sonst:
        Setze Gefunden auf wahr.
    Ende.
Ende.

Zeige "Richtig! Du hast " und Versuche und " Versuche gebraucht.".
```
```eingabe
fünfzig
25
80
60
50
```
```ausgabe
Ich denke mir eine Zahl zwischen 1 und 100.
Das ist keine Zahl.
Höher!
Tiefer!
Tiefer!
Richtig! Du hast 4 Versuche gebraucht.
```

Die Eingaben oben sind ein Beispiellauf — bei dir würfelt der Computer eine andere Zahl.

### Und jetzt?

Du kennst die ganze Sprache bis auf das **Zeichnen**. Ein Stift steht in der Mitte und schaut nach
oben; er zieht eine Linie, solange er unten ist. Ein Quadrat ist damit vier Sätze lang:

```klar
Nimm die Farbe "gold".
Wiederhole 4 Mal:
    Gehe 100 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```

Alles dazu steht im Kapitel [Zeichnen](https://www.ruthner.at/klarsatz/doku-zeichnen.html). Und
sonst:

* **Die Beispielprogramme** in `programme/` — nach Schwierigkeit geordnet. Nimm dir das nächste nach
  dem, was du schon verstehst, und bau es um.

* **Die Sprachreferenz** [`SPRACHE.md`](SPRACHE.md) — dort steht jeder Satz, den Klarsatz kennt.

* **Der Prüfmodus** `python3 -m klarsatz --pruefe meins.klar` findet Tippfehler und vergessene
  Variablen, ohne das Programm auszuführen.

---

## Häufige Stolperfallen

| Fehler | Richtig |
|---|---|
| `Zeige "Hallo"` | Der **Punkt** am Ende fehlt: `Zeige "Hallo".` |
| `Wenn Name "Anna" ist:` | `gleich` ist Pflicht: `Wenn Name gleich "Anna" ist:` |
| `Definiere Aufgabe Zeige Summe:` | Aufgabennamen sind **ein** Wort: `Zeige_Summe` |
| `Setze Punkte auf 0.` ohne vorheriges `Merke` | `Setze` ändert nur, was es schon gibt. Zuerst `Merke 0 als Punkte.` |
| `Zeige Element 0 von Liste.` | Gezählt wird ab **1**. |
| `Merke 3,5 als x.` | In der Eingabe wird der **Punkt** benutzt: `Merke 3.5 als x.` Angezeigt wird dann `3,5`. |
| Ein Block ohne `Ende.` | Jeder `:`-Block braucht sein `Ende.` — außer der Kurzform mit Komma. |
