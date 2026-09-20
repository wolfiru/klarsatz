# Übungsaufgaben

Zwölf Aufgaben zum Selbstprüfen. Jede nennt die Lernstufe und die Lektion, nach der sie zu
schaffen ist — du brauchst also nie etwas, das noch nicht dran war.

**Wie geprüft wird:** Nicht auf wortgleiche Ausgabe. Dein Programm wird mit festen Antworten
ausgeführt, und dann wird nachgesehen, ob das Wesentliche stimmt: Kommt die Zahl vor? Hat die
Ausgabe die richtige Zahl an Zeilen? Wird überhaupt gefragt? Dadurch darfst du deine Sätze
selbst formulieren — *„Die Fläche ist 12“* und *„12 Quadratmeter“* sind beide richtig.

**Wo du sie löst:** Auf der Seite [Übungsaufgaben](https://www.ruthner.at/klarsatz/aufgaben.html),
direkt im Browser. Dort steht die Angabe, daneben ein Editor, und der Knopf *Abgeben* sagt dir,
welche Regel noch nicht erfüllt ist — nicht, wie die Lösung aussieht.

---

## 1 — Begrüßung
*Stufe 1 · nach Lektion 2*

Frage nach dem Namen und begrüße die Person damit. Der Name muss in der Antwort vorkommen.

```probe
eingabe: Wolfgang
fragt: 1
zeilen: 1
enthält: Wolfgang
```
```probe
eingabe: Mia
enthält: Mia
```
```loesung
Frage "Wie heißt du?" und merke die Antwort als Name.
Zeige "Hallo, " und Name und "!".
```
```gegenprobe
Zeige "Hallo, Wolfgang!".
```

---

## 2 — Rechteck
*Stufe 2 · nach Lektion 2*

Frage nach Länge und Breite eines Rechtecks und zeige die Fläche. Rechne sie aus — schreib sie
nicht hin.

```probe
eingabe: 4
eingabe: 3
fragt: 2
enthält: 12
```
```probe
eingabe: 7
eingabe: 5
enthält: 35
benutzt nicht: 35
```
```loesung
Frage "Wie lang?" und merke die Antwort als Laenge.
Frage "Wie breit?" und merke die Antwort als Breite.
Zeige "Die Fläche ist " und Laenge mal Breite und " Quadratmeter".
```
```gegenprobe
Frage "Wie lang?" und merke die Antwort als Laenge.
Frage "Wie breit?" und merke die Antwort als Breite.
Zeige "Die Fläche ist 12 Quadratmeter".
```

---

## 3 — Gerade oder ungerade
*Stufe 3 · nach Lektion 3*

Frage nach einer ganzen Zahl und sage, ob sie gerade oder ungerade ist.

```probe
eingabe: 4
enthält: gerade
enthält nicht: ungerade
```
```probe
eingabe: 7
enthält: ungerade
```
```probe
eingabe: 0
enthält: gerade
enthält nicht: ungerade
```
```loesung
Frage "Welche Zahl?" und merke die Antwort als Zahl.
Wenn Zahl durch 2 teilbar ist, zeige "Die Zahl ist gerade".
Sonst zeige "Die Zahl ist ungerade".
```
```gegenprobe
Frage "Welche Zahl?" und merke die Antwort als Zahl.
Zeige "Die Zahl ist gerade".
```

---

## 4 — Die größere Zahl
*Stufe 3 · nach Lektion 3*

Frage nach zwei Zahlen und zeige die größere. Sind sie gleich groß, sag das.

```probe
eingabe: 3
eingabe: 9
letzte zeile: 9
```
```probe
eingabe: 12
eingabe: 4
letzte zeile: 12
```
```probe
eingabe: 5
eingabe: 5
enthält: gleich
```
```loesung
Frage "Erste Zahl?" und merke die Antwort als Erste.
Frage "Zweite Zahl?" und merke die Antwort als Zweite.
Wenn Erste gleich Zweite ist:
    Zeige "Beide sind gleich groß".
Sonst wenn Erste größer als Zweite ist:
    Zeige Erste.
Sonst:
    Zeige Zweite.
Ende.
```
```gegenprobe
Frage "Erste Zahl?" und merke die Antwort als Erste.
Frage "Zweite Zahl?" und merke die Antwort als Zweite.
Zeige Zweite.
```

---

## 5 — Countdown
*Stufe 4 · nach Lektion 5*

Frage nach einer Zahl und zähle von ihr rückwärts bis 1. Zum Schluss: „Los!“

```probe
eingabe: 3
zeilen: 4
letzte zeile: Los!
enthält: 3
enthält: 1
```
```probe
eingabe: 5
zeilen: 6
benutzt: Zähle
```
```loesung
Frage "Von welcher Zahl?" und merke die Antwort als Start.
Zähle von Start bis 1 rückwärts mit i:
    Zeige i.
Ende.
Zeige "Los!".
```
```gegenprobe
Zeige 3.
Zeige 2.
Zeige 1.
Zeige "Los!".
```

---

## 6 — Summe bis n
*Stufe 4 · nach Lektion 5*

Frage nach einer Zahl und zeige die Summe aller Zahlen von 1 bis dorthin. Bei 10 sind das 55.
Rechne — die Formel darfst du benutzen, das Ergebnis nicht hinschreiben.

```probe
eingabe: 10
letzte zeile: 55
benutzt nicht: 55
```
```probe
eingabe: 4
letzte zeile: 10
```
```probe
eingabe: 1
letzte zeile: 1
```
```loesung
Frage "Bis wohin?" und merke die Antwort als Ziel.
Merke 0 als Summe.
Zähle von 1 bis Ziel mit i:
    Erhöhe Summe um i.
Ende.
Zeige Summe.
```
```gegenprobe
Frage "Bis wohin?" und merke die Antwort als Ziel.
Zeige Ziel.
```

---

## 7 — Das Einmaleins
*Stufe 4 · nach Lektion 5*

Frage nach einer Zahl und zeige ihre Einmaleins-Reihe von 1 bis 10 — eine Zeile je Schritt.

```probe
eingabe: 7
zeilen: 10
enthält: 70
benutzt: Zähle
```
```probe
eingabe: 3
zeilen: 10
letzte zeile: 3 mal 10 ist 30
```
```loesung
Frage "Welche Reihe?" und merke die Antwort als Reihe.
Zähle von 1 bis 10 mit i:
    Zeige Reihe und " mal " und i und " ist " und Reihe mal i.
Ende.
```
```gegenprobe
Frage "Welche Reihe?" und merke die Antwort als Reihe.
Zähle von 1 bis 10 mit i:
    Zeige Reihe mal i.
Ende.
```

---

## 8 — Eine eigene Aufgabe
*Stufe 5 · nach Lektion 7*

Schreibe eine Aufgabe namens `Doppelt`, die eine Zahl verdoppelt zurückgibt, und benutze sie
dreimal: für 4, für 10 und für eine erfragte Zahl.

```probe
eingabe: 7
zeilen: 3
enthält: 8
enthält: 20
letzte zeile: 14
benutzt: Definiere Aufgabe
```
```loesung
Definiere Aufgabe Doppelt von x:
    Gib x mal 2 zurück.
Ende.

Zeige Doppelt von 4.
Zeige Doppelt von 10.
Frage "Welche Zahl?" und merke die Antwort als Zahl.
Zeige Doppelt von Zahl.
```
```gegenprobe
Zeige 8.
Zeige 20.
Frage "Welche Zahl?" und merke die Antwort als Zahl.
Zeige Zahl mal 2.
```

---

## 9 — Die längste Eingabe
*Stufe 6 · nach Lektion 8*

Frage dreimal nach einem Wort, sammle die Wörter in einer Liste und zeige am Ende das längste.

```probe
eingabe: Hund
eingabe: Nashorn
eingabe: Igel
fragt: 3
letzte zeile: Nashorn
benutzt: Liste
```
```probe
eingabe: aa
eingabe: b
eingabe: c
letzte zeile: aa
```
```loesung
Erstelle eine Liste namens Woerter.
Wiederhole 3 Mal:
    Frage "Ein Wort?" und merke die Antwort als Wort.
    Füge Wort zur Woerter hinzu.
Ende.

Merke das erste Element von Woerter als Laengstes.
Für jedes Wort in Woerter:
    Wenn die Länge von Wort größer als die Länge von Laengstes ist:
        Setze Laengstes auf Wort.
    Ende.
Ende.
Zeige Laengstes.
```
```gegenprobe
Erstelle eine Liste namens Woerter.
Wiederhole 3 Mal:
    Frage "Ein Wort?" und merke die Antwort als Wort.
    Füge Wort zur Woerter hinzu.
Ende.
Zeige das erste Element von Woerter.
```

---

## 10 — Der Kassenzettel
*Stufe 7 · nach Lektion 9*

Lege eine Tabelle mit mindestens drei Waren und ihren Preisen an, zeige jede Zeile einzeln und
darunter die Summe.

```probe
zeilen: 4
enthält: Summe
benutzt: Tabelle
fragt: 0
```
```loesung
Erstelle eine Tabelle namens Preise mit "Brot" als 3 und "Milch" als 1 und "Käse" als 6.

Merke 0 als Summe.
Für jede Ware in Preise:
    Zeige Ware und ": " und Wert für Ware in Preise.
    Erhöhe Summe um Wert für Ware in Preise.
Ende.
Zeige "Summe: " und Summe.
```
```gegenprobe
Zeige "Brot: 3".
Zeige "Milch: 1".
Zeige "Käse: 6".
Zeige "Summe: 10".
```

---

## 11 — Ein Quadrat
*Stufe 7 · nach Lektion 2 des Zeichenkurses*

Zeichne ein Quadrat mit vier gleich langen Seiten — mit einer Schleife, nicht mit vier Sätzen.

```probe
striche: 4
benutzt: Wiederhole
```
```loesung
Wiederhole 4 Mal:
    Gehe 80 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```
```gegenprobe
Gehe 80 Schritte vor.
Drehe dich um 90 Grad nach rechts.
Gehe 80 Schritte vor.
Drehe dich um 90 Grad nach rechts.
Gehe 80 Schritte vor.
Drehe dich um 90 Grad nach rechts.
Gehe 80 Schritte vor.
```

---

## 12 — Eine Treppe
*Stufe 7 · nach Lektion 5 des Zeichenkurses*

Zeichne eine Treppe mit fünf Stufen: immer ein Stück nach rechts, dann ein Stück nach oben.
Das sind zehn Striche.

```probe
striche: 10
benutzt: Wiederhole
```
```loesung
Drehe dich um 90 Grad nach rechts.
Wiederhole 5 Mal:
    Gehe 30 Schritte vor.
    Drehe dich um 90 Grad nach links.
    Gehe 30 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```
```gegenprobe
Wiederhole 5 Mal:
    Gehe 30 Schritte vor.
Ende.
```
