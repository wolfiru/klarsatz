# Zeichnen mit Klarsatz

Acht Lektionen. Am Ende hast du ein Bild gemalt, das sich bewegt.

Dieser Kurs ist der zweite Teil. Er setzt voraus, dass du [das Tutorial](TUTORIAL.md) kennst —
also Variablen, Schleifen, Bedingungen und eigene Aufgaben. Wenn du damit schon umgehen kannst,
bist du hier richtig, denn Zeichnen ist nichts Neues: Es sind dieselben Schleifen, nur sieht man
sie diesmal.

**Wo gemalt wird.** In der [Spielwiese](https://www.ruthner.at/klarsatz/spielplatz.html) erscheint
neben der Ausgabe eine Leinwand, sobald ein Programm den ersten Strich zieht. Auf dem eigenen
Rechner schreibt `python3 -m klarsatz --bild bild.svg meins.klar` das Ergebnis in eine Bilddatei.

> **Wo tippe ich das ein?** In der Spielwiese — das ist der Editor mit dem grünen
> *Ausführen*-Knopf. Du kommst auf zwei Wegen hin:
>
> * Über jedem Beispiel steht **„Im Spielplatz öffnen“**. Ein Klick, und das Programm steht
>   dort schon im Editor — du kannst es sofort ändern und laufen lassen.
> * Für die Aufgaben („Deine Aufgabe: …“) brauchst du ein **[leeres Blatt](https://www.ruthner.at/klarsatz/spielplatz.html#beispiel=)**.
>   Dort tippst du selbst.
>
> Am besten lässt du die Spielwiese in einem zweiten Fenster offen, neben diesem Kurs.

Auch hier gilt: **vorhersagen → ausprobieren → verändern.** Zeichne auf Papier, was du erwartest,
bevor du auf *Ausführen* drückst. Bei Grafik lohnt sich das doppelt — man sieht sofort, ob man
richtig lag.

| | Lektion | Darum geht es |
|---|---|---|
| 1 | [Der Stift](#lektion-1--der-stift) | vor, zurück, drehen |
| 2 | [Ecken zählen](#lektion-2--ecken-zählen) | Vielecke und die 360er-Regel |
| 3 | [Farbe und Strich](#lektion-3--farbe-und-strich) | Farben, Strichstärke |
| 4 | [Den Stift heben](#lektion-4--den-stift-heben) | mehrere Figuren nebeneinander |
| 5 | [Schleife in der Schleife](#lektion-5--schleife-in-der-schleife) | Muster |
| 6 | [Der Zufall malt mit](#lektion-6--der-zufall-malt-mit) | Zufallszahlen |
| 7 | [Eigene Bausteine](#lektion-7--eigene-bausteine) | Aufgaben mit Werten |
| 8 | [Bewegung](#lektion-8--bewegung) | löschen, warten, Takt |

Jede Zeichnung in diesem Kurs wird nachgerechnet: Anzahl der Striche, Farben, und ob die Figur
geschlossen ist. Was hier steht, entsteht auch wirklich.

---

## Lektion 1 — Der Stift

**Das Problem:** Auf der Leinwand soll eine Linie erscheinen.

Stell dir einen Stift vor. Er steht in der **Mitte** der Fläche und schaut **nach oben**. Wenn du
ihn losschickst, zieht er eine Linie hinter sich her.

```klar
Gehe 100 Schritte vor.
```
```zeichnung
striche: 1
```

Ein Strich, 100 Schritte lang, nach oben. Jetzt drehen wir ihn:

**Vorhersagen.** Zeichne auf Papier, was hier entsteht — erst dann ausführen.

```klar
Gehe 100 Schritte vor.
Drehe dich um 90 Grad nach rechts.
Gehe 100 Schritte vor.
```
```zeichnung
striche: 2
geschlossen: nein
```

Ein Winkel. Der Stift merkt sich zwei Dinge: **wo** er steht und **wohin** er schaut. `Gehe`
ändert das eine, `Drehe` das andere.

**Verändern.** Jedes Mal erst vorhersagen:

* `Drehe dich um 90 Grad nach links.` statt nach rechts
* `Gehe 100 Schritte zurück.` statt vor
* eine dritte und vierte Zeile anhängen — was fehlt dann noch zum Quadrat?

Mit `Gehe zur Mitte.` schickst du den Stift zurück an den Anfang, und er schaut wieder nach oben.
**Dieser Rückweg malt nicht mit** — er zählt nicht als Strich:

```klar
Gehe 80 Schritte vor.
Gehe zur Mitte.
Drehe dich um 90 Grad nach rechts.
Gehe 80 Schritte vor.
```
```zeichnung
striche: 2
```

Zwei Striche, nicht drei. Deshalb eignet sich `Gehe zur Mitte` gut, um zwischen zwei Figuren
umzusetzen.

**Deine Aufgabe:** Zeichne ein Kreuz aus vier Strichen, die alle in der Mitte beginnen.

---

## Lektion 2 — Ecken zählen

**Das Problem:** Ein Quadrat braucht vier Mal dasselbe: geradeaus, abbiegen. Viermal
hinschreiben geht — aber bei einem Zwanzigeck?

Du kennst die Lösung schon aus dem Tutorial:

```klar
Wiederhole 4 Mal:
    Gehe 100 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```
```zeichnung
striche: 4
geschlossen: ja
```

Die Figur ist **geschlossen** — der Stift landet genau dort, wo er losgelaufen ist. Das ist kein
Zufall: Vier Mal 90 Grad sind 360 Grad, eine volle Drehung.

**Vorhersagen.** Was passiert bei `3 Mal` und `120 Grad`?

```klar
Wiederhole 3 Mal:
    Gehe 120 Schritte vor.
    Drehe dich um 120 Grad nach rechts.
Ende.
```
```zeichnung
striche: 3
geschlossen: ja
```

Ein Dreieck. Und jetzt die Regel, die dahintersteckt:

> **360 geteilt durch die Anzahl der Ecken.** Bei 4 Ecken sind es 90 Grad, bei 3 Ecken 120, bei
> 6 Ecken 60, bei 36 Ecken 10 Grad.

Das lässt sich direkt hinschreiben, statt es jedes Mal im Kopf auszurechnen:

```klar
Merke 6 als Ecken.
Wiederhole Ecken Mal:
    Gehe 60 Schritte vor.
    Drehe dich um 360 geteilt durch Ecken Grad nach rechts.
Ende.
```
```zeichnung
striche: 6
geschlossen: ja
```

**Verändern.** Setz `Ecken` auf 3, 5, 8, 12 — und schließlich auf 36. Was siehst du bei 36?

<details><summary>Antwort</summary>

Einen Kreis. Ein Kreis *ist* ein Vieleck mit sehr vielen, sehr kurzen Seiten — genau so zeichnet
ihn jedes Grafikprogramm. Bei 36 Ecken sieht das Auge die Ecken schon nicht mehr.

</details>

**Deine Aufgabe:** Zeichne ein Achteck. Ändere dann nur die Schrittzahl, damit es halb so groß wird.

---

## Lektion 3 — Farbe und Strich

**Das Problem:** Alles ist bisher gleich dünn und gleich hell. Ein Bild braucht Unterschiede.

```klar
Nimm die Farbe "gold".
Nimm die Strichstärke 4.
Wiederhole 4 Mal:
    Gehe 90 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```
```zeichnung
striche: 4
farben: gold
geschlossen: ja
```

Beides gilt **ab jetzt**, bis du es wieder änderst — wie wenn man zu einem anderen Stift greift.
Es gibt dreizehn Farben:

> `rot` · `blau` · `grün` · `gelb` · `gold` · `orange` · `lila` · `rosa` · `türkis` · `braun` ·
> `grau` · `schwarz` · `weiß`

Und weil die Farbe mitten in der Schleife gewechselt werden darf, wird daraus ein Stern in vier
Farben:

```klar
Nimm die Strichstärke 3.
Nimm die Farbe "rot".
Gehe 70 Schritte vor.
Gehe zur Mitte.
Drehe dich um 90 Grad nach rechts.
Nimm die Farbe "blau".
Gehe 70 Schritte vor.
Gehe zur Mitte.
Drehe dich um 180 Grad nach rechts.
Nimm die Farbe "grün".
Gehe 70 Schritte vor.
Gehe zur Mitte.
Drehe dich um 270 Grad nach rechts.
Nimm die Farbe "türkis".
Gehe 70 Schritte vor.
```
```zeichnung
striche: 4
farben: rot, blau, grün, türkis
```

Vier Striche in vier Farben — die Rückwege zur Mitte sind unsichtbar, wie in Lektion 1.

**Deine Aufgabe:** Zeichne drei ineinanderliegende Quadrate in drei Farben, jedes 20 Schritte
größer als das vorige.

---

## Lektion 4 — Den Stift heben

**Das Problem:** Zur Mitte kommst du unsichtbar zurück. Aber was, wenn du **woandershin** willst —
zum Beispiel ein Stück zur Seite, um die nächste Figur danebenzusetzen? Dann malt jeder Schritt mit.

Dafür gibt es `Hebe den Stift.` und `Senke den Stift.` — dazwischen bewegst du dich spurlos.

**Vorhersagen.** Wie viele Striche entstehen hier?

```klar
Nimm die Farbe "gold".
Gehe 40 Schritte vor.
Hebe den Stift.
Gehe 30 Schritte vor.
Senke den Stift.
Gehe 40 Schritte vor.
```
```zeichnung
striche: 2
farben: gold
```

Zwei Striche mit einer Lücke dazwischen — obwohl der Stift die ganze Zeit geradeaus gelaufen ist.
Die mittleren 30 Schritte hat er zurückgelegt, ohne zu malen. Ohne `Hebe den Stift.` wäre daraus
**ein** Strich von 110 Schritten geworden.

Damit lassen sich Figuren **nebeneinander** setzen:

```klar
Nimm die Farbe "türkis".
Wiederhole 3 Mal:
    Wiederhole 4 Mal:
        Gehe 40 Schritte vor.
        Drehe dich um 90 Grad nach rechts.
    Ende.
    Hebe den Stift.
    Drehe dich um 90 Grad nach rechts.
    Gehe 60 Schritte vor.
    Drehe dich um 90 Grad nach links.
    Senke den Stift.
Ende.
```
```zeichnung
striche: 12
farben: türkis
```

Drei Quadrate, zwölf Striche — die Wege dazwischen sind unsichtbar.

**Deine Aufgabe:** Zeichne eine gestrichelte Linie: zehn kurze Striche mit Lücken dazwischen.

---

## Lektion 5 — Schleife in der Schleife

**Das Problem:** Aus einer Figur soll ein Muster werden.

Der Trick ist einfach: Zeichne eine Figur, dreh dich ein Stück, zeichne sie wieder. Die äußere
Schleife dreht, die innere zeichnet.

**Vorhersagen.** Zwölf Quadrate, jedes um 30 Grad gedreht — wie viele Striche werden das?

```klar
Nimm die Farbe "lila".
Wiederhole 12 Mal:
    Wiederhole 4 Mal:
        Gehe 70 Schritte vor.
        Drehe dich um 90 Grad nach rechts.
    Ende.
    Drehe dich um 30 Grad nach rechts.
Ende.
```
```zeichnung
striche: 48
farben: lila
```

Zwölf mal vier. Aus zwei Schleifen und sechs Zeilen entsteht eine Rosette.

Und wenn die Figur bei jedem Durchlauf ein bisschen größer wird, entsteht eine Spirale:

```klar
Nimm die Farbe "gold".
Zähle von 1 bis 60 mit i:
    Gehe i mal 3 Schritte vor.
    Drehe dich um 91 Grad nach rechts.
Ende.
```
```zeichnung
striche: 60
farben: gold
```

**Verändern.** Hier steckt der ganze Reiz im Ausprobieren:

* `91 Grad` → `90 Grad`. Warum wird aus der Spirale ein Quadrat?
* `91` → `89`, `120`, `144`
* `i mal 3` → `i mal 1`

**Deine Aufgabe:** Bau aus der Rosette ein Muster aus Dreiecken statt Quadraten.

---

## Lektion 6 — Der Zufall malt mit

**Das Problem:** Alles ist bisher exakt geplant. Manchmal will man, dass es das nicht ist.

`Zufallszahl von 1 bis 10` kennst du aus dem Tutorial. Beim Zeichnen wird daraus ein Werkzeug:

```klar
Nimm die Strichstärke 2.
Erstelle eine Liste namens Palette mit "rot" und "gold" und "türkis" und "lila".
Wiederhole 20 Mal:
    Nimm die Farbe ein zufälliges Element von Palette.
    Gehe Zufallszahl von 20 bis 90 Schritte vor.
    Hebe den Stift.
    Gehe zur Mitte.
    Senke den Stift.
    Drehe dich um Zufallszahl von 1 bis 360 Grad nach rechts.
Ende.
```
```zeichnung
striche: 20
```

Zwanzig Strahlen aus der Mitte, jeder in zufälliger Länge, Richtung und Farbe.

> **Derselbe Zufall auf Wunsch.** In der Spielwiese kommt bei jedem Lauf ein anderes Bild heraus.
> Auf der Kommandozeile liefert `--seed 42` immer dasselbe — praktisch, wenn man ein Bild
> wiederfinden will, das einem gefallen hat.

**Deine Aufgabe:** Zeichne einen Sternenhimmel: fünfzig sehr kurze Striche an zufälligen Stellen.
(Tipp: hingehen mit gehobenem Stift, einen kurzen Strich malen, zurück zur Mitte.)

---

## Lektion 7 — Eigene Bausteine

**Das Problem:** Du willst drei Häuser zeichnen. Das Haus besteht aus einem Quadrat und einem
Dreieck — und du willst es nicht dreimal hinschreiben.

Aufgaben kennst du aus dem Tutorial. Beim Zeichnen zahlen sie sich besonders aus, weil eine
Figur damit einen **Namen** bekommt:

```klar
Definiere Aufgabe Quadrat von Seite:
    Wiederhole 4 Mal:
        Gehe Seite Schritte vor.
        Drehe dich um 90 Grad nach rechts.
    Ende.
Ende.

Nimm die Farbe "türkis".
Führe Quadrat mit 40 aus.
Führe Quadrat mit 70 aus.
Führe Quadrat mit 100 aus.
```
```zeichnung
striche: 12
farben: türkis
geschlossen: ja
```

Ein Baustein, drei Größen. Jetzt das Haus:

```klar
Definiere Aufgabe Haus von Breite:
    Anmerkung: erst die Wände …
    Wiederhole 4 Mal:
        Gehe Breite Schritte vor.
        Drehe dich um 90 Grad nach rechts.
    Ende.
    Anmerkung: … dann hinauf zur Dachkante und das Dach als Dreieck
    Hebe den Stift.
    Gehe Breite Schritte vor.
    Senke den Stift.
    Drehe dich um 30 Grad nach links.
    Wiederhole 3 Mal:
        Gehe Breite Schritte vor.
        Drehe dich um 120 Grad nach rechts.
    Ende.
Ende.

Nimm die Farbe "braun".
Nimm die Strichstärke 3.
Führe Haus mit 80 aus.
```
```zeichnung
striche: 7
farben: braun
```

Sieben Striche: vier Wände, drei Dachkanten.

**Verändern.** Schreib eine Aufgabe `Vieleck von Ecken und Seite`, die jedes Vieleck aus Lektion 2
zeichnen kann. Dann bau daraus eine Reihe: Dreieck, Viereck, Fünfeck, Sechseck nebeneinander.

**Deine Aufgabe:** Erweitere `Haus` um ein Fenster. Die Aufgabe soll danach immer noch mit einer
einzigen Zeile aufrufbar sein.

---

## Lektion 8 — Bewegung

**Das Problem:** Bis jetzt entsteht ein Bild und bleibt stehen. Jetzt soll es sich bewegen.

Dafür brauchst du zwei neue Sätze:

* `Lösche die Zeichnung.` räumt die Fläche leer — der Stift bleibt, wo er ist.
* `Warte 1 Sekunde.` hält an, ohne als Rechenzeit zu zählen.

Und damit ist eine Bewegung immer dasselbe Muster: **löschen → zeichnen → warten.**

```klar
Nimm die Farbe "gold".
Zähle von 3 bis 10 mit Ecken:
    Lösche die Zeichnung.
    Gehe zur Mitte.
    Wiederhole Ecken Mal:
        Gehe 50 Schritte vor.
        Drehe dich um 360 geteilt durch Ecken Grad nach rechts.
    Ende.
    Warte 1 Sekunde.
Ende.
```

Das Vieleck wächst vor deinen Augen von drei auf zehn Ecken. Auf der Leinwand siehst du immer nur
das aktuelle, weil jeder Durchlauf mit `Lösche die Zeichnung.` beginnt.

Wenn du genau hinsiehst, stört dabei aber etwas: Das Bild **zappelt**. Die Fläche sucht sich ihren
Ausschnitt nämlich selbst und passt ihn an das an, was gerade gezeichnet ist — und das ändert sich
ja in jedem Durchlauf. Ein Satz stellt das ab:

* `Nimm die Leinwand 400 mal 400.` legt die Fläche fest. Die Mitte ist (0, 0), links ist −200,
  rechts 200, und das bleibt so, egal was gezeichnet wird.

Und weil ein bewegtes Bild gern dazusagt, was es gerade zeigt, gibt es noch einen Satz:

* `Beschrifte "Text".` schreibt an die Stelle, an der der Stift steht — in seiner Farbe. Mehrere
  Teile darfst du mit `und` verbinden, genau wie bei `Zeige`. `mit 20` macht die Schrift größer.

```klar
Nimm die Leinwand 400 mal 400.
Nimm die Farbe "gold".
Zähle von 3 bis 10 mit Ecken:
    Lösche die Zeichnung.
    Gehe zur Mitte.
    Wiederhole Ecken Mal:
        Gehe 50 Schritte vor.
        Drehe dich um 360 geteilt durch Ecken Grad nach rechts.
    Ende.

    Hebe den Stift.
    Gehe zur Mitte.
    Gehe 120 Schritte zurück.
    Beschrifte Ecken und " Ecken" mit 18.

    Warte 1 Sekunde.
Ende.
```

Jetzt steht das Vieleck still und wächst nur noch nach außen — und darunter steht, was man sieht.

> **Warum das überhaupt geht.** Die Spielwiese zeigt Ausgaben und Striche in dem Moment, in dem sie
> entstehen — ein Programm muss nicht fertig sein, um etwas zu zeigen. Genau deshalb darf eine
> Anzeige auch endlos laufen.

Für eine Anzeige, die **nie** aufhört, gibt es eine Kurzform. Sie lässt das ganze Programm im Takt
von vorne beginnen:

```klar
Merke die aktuelle Sekunde als Sekunde.
Nimm die Farbe "türkis".
Nimm die Strichstärke 4.
Gehe zur Mitte.
Drehe dich um Sekunde mal 6 Grad nach rechts.
Gehe 90 Schritte vor.
Wiederhole dieses Programm jede Sekunde.
```
```zeichnung
striche: 1
farben: türkis
```

Das ist ein Sekundenzeiger: 360 Grad geteilt durch 60 Sekunden sind 6 Grad pro Sekunde. In der
Spielwiese wird aus dem Knopf *Ausführen* dabei ein *Anhalten*.

**Deine Aufgabe:** Bau daraus eine ganze Uhr — mit Stunden-, Minuten- und Sekundenzeiger in
verschiedenen Längen und Farben. `die aktuelle Stunde` und `die aktuelle Minute` gibt es auch.
Wenn du nicht weiterkommst: In der Spielwiese liegt sie als Beispiel *Uhr* bereit.

---

## Und jetzt?

Du kannst alles, was zum Zeichnen gehört. Was jetzt noch kommt, sind Ideen, keine neuen Befehle:

* **Baum** — eine Aufgabe, die sich selbst aufruft und dabei kleiner wird. Rekursion, gezeichnet.
* **Wellen** — `Sinus` und `Kosinus` ergeben Schwingungen in zwei Farben.
* **Grafikadventure** — Räume, Türen und ein Strichmännchen, gezeichnet aus Bedingungen.

Alle drei liegen in der Spielwiese zum Hineinladen und Zerlegen. Nimm dir eines vor, ändere eine
Zahl und schau, was passiert — genau so hat dieser Kurs angefangen.

Und wenn dich einmal ein größeres Programm reizt: Im Spielplatz liegen zwei, die alles
zusammenbringen, was hier vorkam — *21 Spiel des Lebens* (ein Gitter, das sich selbst überlässt)
und *22 Routenplaner* (eine Karte mit beschrifteten Orten und der kürzesten Strecke darin).

Die vollständige Liste aller Zeichenbefehle steht im Kapitel
[Zeichnen](https://www.ruthner.at/klarsatz/doku-zeichnen.html).
