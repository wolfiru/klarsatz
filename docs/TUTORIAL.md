# Programmieren lernen mit Klarsatz

Elf Lektionen. Am Ende hast du ein eigenes Programm gebaut — und siehst dasselbe Programm in
Python.

Du brauchst nichts zu installieren: Öffne die [Spielwiese](https://www.ruthner.at/klarsatz/spielplatz.html),
wähle oben **Leeres Blatt** und tippe mit.

> **Wo tippe ich das ein?** In der Spielwiese — das ist der Editor mit dem grünen
> *Ausführen*-Knopf. Du kommst auf zwei Wegen hin:
>
> * Über jedem Beispiel steht **„Im Spielplatz öffnen"**. Ein Klick, und das Programm steht
>   dort schon im Editor — du kannst es sofort ändern und laufen lassen.
> * Für die Aufgaben („Deine Aufgabe: …") brauchst du ein **[leeres Blatt](https://www.ruthner.at/klarsatz/spielplatz.html#beispiel=)**.
>   Dort tippst du selbst.
>
> Am besten lässt du die Spielwiese in einem zweiten Fenster offen, neben diesem Kurs.

**So funktioniert dieser Kurs.** Jede Lektion beginnt mit einem Problem, nicht mit einem Befehl.
Dann kommt immer dieselbe Schleife:

> **Vorhersagen** → **Ausprobieren** → **Verändern**

Lies das Programm und sag dir *vorher*, was herauskommt. Dann lass es laufen. Dann ändere etwas und
sieh nach, ob du recht behältst. Wer nur liest, lernt Vokabeln. Wer vorhersagt, lernt Programmieren.

**Die Stufenwahl.** In der Spielwiese steht oben ein Feld *Stufe*. Stell es auf die Stufe der
Lektion, an der du gerade bist — dann kennt Klarsatz nur die Wörter, die du schon gelernt hast, und
sagt dir freundlich Bescheid, wenn du zu weit greifst. Ein geladenes Beispiel setzt die Stufe
zurück.

| | Lektion | Stufe |
|---|---|---|
| 1 | [Dein erstes Programm](#lektion-1--dein-erstes-programm) | 1 |
| 2 | [Der Computer merkt sich Dinge](#lektion-2--der-computer-merkt-sich-dinge) | 2 |
| 3 | [Programme treffen Entscheidungen](#lektion-3--programme-treffen-entscheidungen) | 3 |
| 4 | [Fehler sind normal](#lektion-4--fehler-sind-normal) | 3 |
| 5 | [Etwas mehrfach tun](#lektion-5--etwas-mehrfach-tun) | 4 |
| 6 | [Dein erstes Spiel](#lektion-6--dein-erstes-spiel) | 4 |
| 7 | [Eigene Bausteine](#lektion-7--eigene-bausteine) | 5 |
| 8 | [Viele Werte auf einmal](#lektion-8--viele-werte-auf-einmal) | 6 |
| 9 | [Daten ordnen (Kür)](#lektion-9--daten-ordnen-kür) | 7 |
| ✦ | [Kür: Malen mit dem Stift](#kür--malen-mit-dem-stift) | 7 |
| 10 | [Dein Abschlussprojekt](#lektion-10--dein-abschlussprojekt) | 7 |
| 11 | [Dasselbe in Python](#lektion-11--dasselbe-in-python) | — |

Alle Beispiele hier laufen wirklich. Die Ausgaben, die Fehlermeldungen und sogar der Python-Code in
Lektion 11 sind nicht abgetippt, sondern werden bei jedem Testlauf neu ausgerechnet und verglichen.

---

## Lektion 1 — Dein erstes Programm

**Das Problem:** Der Computer soll dich begrüßen.

Ein Computer macht nichts von selbst. Er braucht genaue Anweisungen, eine nach der anderen. In
Klarsatz ist jede Anweisung ein Satz — er fängt mit einem Befehlswort an und hört mit einem
**Punkt** auf, wie im Deutschen.

**Vorhersagen.** Was gibt dieses Programm aus? Sag es dir, bevor du weiterliest.

```klar
Zeige "Hallo!".
Zeige "Ich lerne programmieren.".
```
```ausgabe
Hallo!
Ich lerne programmieren.
```

Zwei Sätze, zwei Zeilen — der Reihe nach von oben nach unten. Mehr ist ein Programm nicht.

**Verändern.** Tipp das Programm in die Spielwiese und bau eine dritte Zeile ein. Vertausche die
Zeilen. Was passiert mit der Ausgabe?

Mit `und` klebst du mehrere Teile zu **einer** Zeile zusammen:

```klar
Zeige "Ich bin " und 12 und " Jahre alt.".
```
```ausgabe
Ich bin 12 Jahre alt.
```

Und mit `Anmerkung:` schreibst du etwas, das der Computer überliest — nur für Menschen gedacht:

```klar
Anmerkung: Das hier ist mein erstes Programm.
Zeige "Fertig.".
```
```ausgabe
Fertig.
```

### Wie weit geht das mit dem Deutsch?

Klarsatz klingt wie Deutsch — aber es **ist** kein Deutsch. Es ist eine Programmiersprache, deren
Sätze sich an deutscher Alltagssprache orientieren. Der Computer versteht nicht, was du *meinst*;
er erkennt, welchem **festen Satzmuster** dein Satz entspricht.

Innerhalb eines Musters darfst du dich frei bewegen. Artikel und Höflichkeitswörter werden
überlesen:

```klar
Zeige mir bitte "Hallo".
```
```ausgabe
Hallo
```

Aber ein Satz, der auf kein Muster passt, geht nicht — auch wenn jeder Mensch ihn verstünde:

```klar
Sag Hallo.
```
```fehler
Ich verstehe den Satz nicht: er beginnt mit 'Sag'.
```

Das ist keine Schwäche, sondern der Grund, warum die Sprache funktioniert: **Eindeutigkeit.**
`Zeige` heißt immer genau dasselbe. Bei echtem Deutsch müsste der Computer raten — und raten ist
das Letzte, was ein Programm tun soll.

Welche Satzanfänge es gibt, lernst du in diesem Kurs Stück für Stück. Du musst sie nicht auswendig
können: Die Fehlermeldung sagt dir, wenn du danebenliegst.

> **Ein Helfer von Anfang an.** Neben *Ausführen* steht in der Spielwiese ein Knopf **Prüfen**.
> Der liest dein Programm durch, ohne es laufen zu lassen, und zeigt Tippfehler und vergessene
> Namen an. Wenn du unsicher bist, drück ihn — das ist kein Schummeln, das machen Profis den
> ganzen Tag. Auf der Kommandozeile heißt er `--pruefe`.

**Deine Aufgabe:** Lass den Computer eine kleine Biografie über dich ausgeben — Name, Wohnort,
Lieblingsessen. Drei Zeilen, eine Anmerkung oben drüber.

---

## Lektion 2 — Der Computer merkt sich Dinge

**Das Problem:** Wir wollen jemanden nach dem Namen fragen und diesen Namen später noch einmal
verwenden. Dafür muss der Computer ihn sich merken.

```klar
Frage "Wie heißt du? " und merke die Antwort als Name.
Zeige "Hallo, " und Name und "!".
Zeige "Schön, dass du da bist, " und Name und ".".
```
```eingabe
Anna
```
```ausgabe
Hallo, Anna!
Schön, dass du da bist, Anna.
```

Der Name steht jetzt an zwei Stellen, eingetippt wurde er einmal. **Das nennt man eine Variable:**
ein Platz mit einem Namen, in dem ein Wert liegt.

**Vorhersagen.** Was kommt bei diesem Programm heraus?

```klar
Merke 20 als Punkte.
Erhöhe Punkte um 5.
Zeige Punkte.
```
```ausgabe
25
```

`Merke 20 als Punkte` legt den Platz an. `Erhöhe Punkte um 5` ändert, was drinliegt. `Zeige Punkte`
schaut nach. Der Wert kann sich ändern — der Name bleibt.

**Verändern.** Probier der Reihe nach aus und sag jedes Mal vorher, was herauskommt:

* Setz `Erhöhe Punkte um 5.` zweimal untereinander.
* Schreib `Verringere Punkte um 3.` dazu.
* Was passiert bei `Erhöhe Punkte um -5.`?
* Vertausch die erste und die zweite Zeile. Warum beschwert sich Klarsatz?

Rechnen geht mit `plus`, `minus`, `mal` und `geteilt durch`:

```klar
Merke 7 als a.
Merke 3 als b.
Zeige a plus b.
Zeige a mal b.
```
```ausgabe
10
21
```

### Zahl oder Text?

Bisher waren die Antworten Namen — also Text. Wenn du mit einer Antwort **rechnen** willst, sag das
dazu: `als Zahl`.

```klar
Frage "Wie alt bist du? " als Zahl und merke die Antwort als Alter.
Zeige "In zehn Jahren bist du " und Alter plus 10 und ".".
```
```eingabe
40
```
```ausgabe
In zehn Jahren bist du 50.
```

**Warum muss man das dazusagen?** Weil `40` und `"40"` für einen Computer zwei verschiedene Dinge
sind: eine Zahl, mit der man rechnet, und ein Text aus zwei Ziffern. Bei einer Telefonnummer oder
einer Postleitzahl willst du gerade **nicht** rechnen — dafür gibt es `als Text`:

```klar
Frage "Postleitzahl? " als Text und merke die Antwort als PLZ.
Zeige "Du wohnst in " und PLZ und ".".
```
```eingabe
3100
```
```ausgabe
Du wohnst in 3100.
```

Und wenn jemand etwas eintippt, das keine Zahl ist? Dann sagt Klarsatz das — und gleich dazu, was
man stattdessen tun kann:

```klar
Frage "Wie alt bist du? " als Zahl und merke die Antwort als Alter.
Zeige Alter.
```
```eingabe
ungefähr vierzig
```
```fehler
Hier war eine Zahl gefragt, 'ungefähr vierzig' ist aber keine.
```

> **Und ohne Angabe?** Dann rät Klarsatz: Sieht die Antwort wie eine Zahl aus, wird sie zur Zahl.
> Das ist bequem und für kurze Programme völlig in Ordnung — du siehst es in den Beispielen der
> Spielwiese oft so. Für alles, was verlässlich sein soll, schreib lieber dazu, was du erwartest.

> **Was zählt als Zahl?** Klarsatz schaut sich die Antwort an. Als Zahl gelten `5`, `-5`, `3.5`
> **und** `3,5` (beim Eintippen darfst du das deutsche Komma benutzen), auch mit Leerzeichen
> drumherum; `007` wird zu `7`. Alles andere bleibt Text — auch `+5`, `1e3` und `5x`. Und eine
> leere Eingabe ist ein leerer Text, keine Null.
>
> Im **Quelltext** schreibst du Kommazahlen dagegen mit Punkt: `Merke 3.5 als x.` Ausgegeben wird
> dann wieder deutsch: `3,5`. Der Grund: Im Programm trennt das Komma Satzteile.

> **Eine Schreibweise, mehrere Formulierungen.** Klarsatz überliest Artikel und Füllwörter:
> `Merke 5 als Zahl.` und `Merke dir die 5 als Zahl.` sind dasselbe. In diesem Kurs schreiben wir
> immer die kurze Form. Du musst dir also **nichts** zusätzlich merken — es ist nur schön zu wissen,
> dass die Sprache mitdenkt, wenn du natürlicher schreibst.

**Deine Aufgabe:** Frage nach einem Preis und gib den Preis mit 20 % Aufschlag aus.

---

## Lektion 3 — Programme treffen Entscheidungen

**Das Problem:** Ein Programm soll je nach Alter etwas anderes sagen. Bisher läuft immer alles von
oben nach unten durch — das reicht dafür nicht.

**Vorhersagen.** Was gibt dieses Programm aus?

```klar
Merke 17 als Alter.

Wenn Alter mindestens 18 ist:
    Zeige "Erwachsen".
Sonst:
    Zeige "Noch nicht erwachsen".
Ende.
```
```ausgabe
Noch nicht erwachsen
```

Der Block beginnt mit einem Doppelpunkt und endet mit `Ende.` Dazwischen wird eingerückt — das ist
nicht Pflicht, aber es macht sichtbar, was zusammengehört.

**Verändern — und zwar nur eine einzige Zahl.** Probier `18`. Dann `25`. Dann `0`. Sag jedes Mal
*vorher*, was herauskommt.

Wenn du magst: Zeichne auf Papier zwei Pfeile, die sich gabeln. Genau das tut das Programm.

Das Wichtige an dieser Lektion ist nicht das Wort `Sonst`. Es ist die Erkenntnis:

> **Ein Programm kann abhängig von seinen Daten einen anderen Weg nehmen.**

### Womit man vergleicht

| Schreibweise | Bedeutung |
|---|---|
| `a gleich b` | gleich — **nicht** `a ist b` |
| `a nicht gleich b` | ungleich |
| `a größer als b`, `a kleiner als b` | größer, kleiner |
| `a mindestens b`, `a höchstens b` | größer-gleich, kleiner-gleich |
| `a durch 3 teilbar` | ohne Rest teilbar |

Das Wörtchen **`gleich` ist Pflicht.** `Wenn Name "Anna" ist:` versteht Klarsatz nicht.

```klar
Frage "Wie heißt du? " und merke die Antwort als Name.
Wenn Name gleich "Anna" ist:
    Zeige "Dich kenne ich!".
Sonst:
    Zeige "Freut mich, " und Name und ".".
Ende.
```
```eingabe
Ben
```
```ausgabe
Freut mich, Ben.
```

Mehr als zwei Wege gehen mit `Sonst wenn`:

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

**Vorhersagen:** Was passiert bei `Note` gleich 9? Bei 8? Bei 2? Warum wird bei 9 **nicht** auch
noch „Gut" ausgegeben?

**Deine Aufgabe:** Frage nach einer Zahl und sage, ob sie negativ, null oder positiv ist.

---

## Lektion 4 — Fehler sind normal

**Das Problem:** Früher oder später schreibst du etwas, das Klarsatz nicht versteht. Das passiert
jedem, jeden Tag. Die Frage ist nicht, wie du Fehler vermeidest — sondern wie du sie *liest*.

Diese Lektion ist die einzige, in der du absichtlich kaputte Programme ausprobierst.

### Fehler 1: Der vergessene Punkt

**Vorhersagen.** Was ist hier falsch?

```klar
Zeige "Hallo"
```
```fehler
Am Ende des Satzes fehlt ein Punkt
```

Klarsatz sagt nicht nur *dass* etwas fehlt, sondern **wo**: Zeile 1, Spalte 14, mit einem `^`
darunter. Das ist genau die Stelle, an der der Punkt hingehört.

### Fehler 2: Die Anführungszeichen vergessen

```klar
Zeige Hallo.
```
```fehler
Ich kenne 'Hallo' nicht. Lege es zuerst mit 'Merke ... als Hallo.' an.
```

Ohne Anführungszeichen ist `Hallo` kein Text, sondern ein **Name** — und einen Platz mit diesem
Namen gibt es nicht. Die Meldung sagt dir sogar, wie man ihn anlegen würde.

### Fehler 3: Der Tippfehler

Und jetzt kommt das Schönste, was Klarsatz kann:

```klar
Merke 5 als Summe.
Zeige Sume.
```
```fehler
Meintest du 'Summe'?
```

Klarsatz schaut nach, welche Namen es kennt, und schlägt den ähnlichsten vor. Wenn du einmal eine
halbe Stunde einen Tippfehler gesucht hast, weißt du, was das wert ist.

### Fehler 4: Rechnen, das nicht geht

```klar
Zeige 10 geteilt durch 0.
```
```fehler
Durch null kann man nicht teilen.
```

### Fehler 5: Ändern, was es nicht gibt

```klar
Setze Punkte auf 5.
```
```fehler
Ich kenne 'Punkte' noch nicht.
```

`Setze` ändert nur etwas, das schon da ist. Anlegen tut man mit `Merke`. Genau dieser Unterschied
ist der Grund für die Meldung — und übrigens die Antwort auf die Vertausch-Aufgabe aus Lektion 2.

### Das Wichtigste

> Ein Fehler heißt nicht „ich kann das nicht".
> Ein Fehler ist eine **Nachricht vom Programm an dich**.

Lies immer drei Dinge: **welche Zeile**, **welche Stelle**, **was Klarsatz erwartet hätte**. In
neunzehn von zwanzig Fällen steht die Lösung schon in der Meldung.

**Deine Aufgabe:** Bau in ein funktionierendes Programm absichtlich drei verschiedene Fehler ein —
einen pro Durchgang — und lies jedes Mal die Meldung, bevor du sie reparierst.

---

## Lektion 5 — Etwas mehrfach tun

**Das Problem:** Der Computer soll von 1 bis 10 zählen. Zehn Zeilen `Zeige` zu schreiben wäre
albern — und bei 1000 unmöglich.

```klar
Zähle von 1 bis 5 mit i:
    Zeige i.
Ende.
```
```ausgabe
1
2
3
4
5
```

`i` ist eine Variable, die die Schleife selbst füllt: beim ersten Durchlauf 1, dann 2, dann 3 …

> **Eine Schleife ist ein Programmteil, der wiederholt ausgeführt wird.** Mehr musst du dir aus
> dieser Lektion nicht merken.

**Verändern.** Der Reihe nach, jedes Mal erst vorhersagen:

* `von 1 bis 10`
* `Zeige i mal i.` statt `Zeige i.`
* `Zähle von 10 bis 1 rückwärts mit i:`

Das letzte sieht so aus:

```klar
Zähle von 3 bis 1 rückwärts mit i:
    Zeige i.
Ende.
Zeige "Los!".
```
```ausgabe
3
2
1
Los!
```

### Jetzt wird es interessant

**Das Problem:** Nur die **geraden** Zahlen ausgeben. Dafür brauchst du etwas aus Lektion 3 —
*innerhalb* der Schleife.

**Vorhersagen**, dann ausprobieren:

```klar
Zähle von 1 bis 10 mit i:
    Wenn i durch 2 teilbar ist:
        Zeige i.
    Ende.
Ende.
```
```ausgabe
2
4
6
8
10
```

Zwei Blöcke ineinander, jeder mit seinem eigenen `Ende.` Das ist der Moment, in dem Einrückung
aufhört, Dekoration zu sein.

### Wenn man vorher nicht weiß, wie oft

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

Die Bedingung wird **vor jedem Durchlauf** geprüft, auch vor dem allerersten. Ist sie gleich zu
Beginn falsch, läuft der Block **kein einziges Mal**. Probier es aus: Setz die erste Zeile auf
`Merke 500 als Zahl.` — dann passiert im Schleifenkörper nichts mehr.

Vorsicht andersherum: Wird die Bedingung nie falsch, läuft die Schleife ewig. In der Spielwiese
bricht Klarsatz dann von selbst ab.

**Deine Aufgabe:** Gib das Einmaleins der 7 aus — `1 mal 7 ist 7` bis `10 mal 7 ist 70`.

---

## Lektion 6 — Dein erstes Spiel

Du kannst jetzt Eingaben, Variablen, Entscheidungen und Schleifen. Das reicht für ein richtiges
Spiel — und zwar für ein bekanntes.

**Das Problem:** Der Computer denkt sich eine Zahl zwischen 1 und 100 aus. Du rätst. Er sagt
„höher" oder „tiefer", bis du sie hast, und zählt deine Versuche.

Bevor du weiterliest: Überleg, welche Teile du brauchst.

<details><summary>Meine Zerlegung — erst aufklappen, wenn du selbst überlegt hast</summary>

1. eine Zahl auswürfeln und merken
2. einen Zähler für die Versuche
3. eine Schleife, die läuft, bis geraten wurde
4. in der Schleife: fragen, vergleichen, Hinweis geben
5. am Ende: die Versuche ausgeben

</details>

```klar
Merke Zufallszahl von 1 bis 100 als Gesucht.
Merke 0 als Versuche.
Merke falsch als Gefunden.

Zeige "Ich denke mir eine Zahl zwischen 1 und 100.".

Wiederhole solange Gefunden gleich falsch ist:
    Frage "Dein Tipp: " und merke die Antwort als Tipp.
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
25
80
60
50
```
```ausgabe
Ich denke mir eine Zahl zwischen 1 und 100.
Höher!
Tiefer!
Tiefer!
Richtig! Du hast 4 Versuche gebraucht.
```

Das sind zwanzig Zeilen, und du verstehst jede davon. **Das ist der Punkt dieser Lektion.**

**Verändern.** Und zwar richtig:

* Ändere den Bereich auf 1 bis 10. Wie viele Versuche brauchst du höchstens?
* Gib nach jedem Tipp aus, der wievielte Versuch das war.
* Beende das Spiel nach fünf Versuchen mit „Schade!".

> **Eine Abkürzung — jetzt, wo du sicher bist.** Wenn nach `Wenn` nur *ein* Satz folgt, darf man ihn
> hinter ein Komma schreiben und spart sich das `Ende.`:
>
> `Wenn Tipp kleiner als Gesucht ist, zeige "Höher!".`
>
> Benutz das erst, wenn dir die lange Form in Fleisch und Blut übergegangen ist. Kurz ist nicht
> besser, kurz ist nur kürzer.

---

## Lektion 7 — Eigene Bausteine

**Das Problem:** Dein Ratespiel ist gewachsen. Wenn du jetzt noch eine zweite Runde einbaust, steht
die Frage-und-Prüf-Logik zweimal da — und beim nächsten Ändern vergisst du eine Stelle.

Die Lösung: Gib einem Stück Programm einen Namen. Das heißt in Klarsatz **Aufgabe**.

```klar
Definiere Aufgabe Begrüße mit Name:
    Zeige "Hallo, " und Name und "!".
Ende.

Führe Begrüße mit "Anna" aus.
Führe Begrüße mit "Ben" aus.
Führe Begrüße mit "Rocco" aus.
```
```ausgabe
Hallo, Anna!
Hallo, Ben!
Hallo, Rocco!
```

Einmal beschrieben, dreimal benutzt. Der Name einer Aufgabe ist **ein** Wort — `Begrüße`, nicht
`Begrüße den Gast`. Mehrere Wörter verbindest du mit Unterstrich: `Begrüße_Gast`.

### Aufgaben, die etwas zurückgeben

Bisher hat die Aufgabe etwas *getan*. Sie kann auch etwas *ausrechnen* und zurückgeben:

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

**Vorhersagen:** Warum kommt bei der zweiten Zeile 25 heraus und nicht 49?

Mehrere Werte übergibst du mit `und`:

```klar
Definiere Aufgabe Flaeche von Breite und Hoehe:
    Gib Breite mal Hoehe zurück.
Ende.

Zeige Flaeche von 3 und 4.
```
```ausgabe
12
```

### Warum das wichtig ist

Eine Aufgabe ist mehr als Tipparbeit sparen. Sie gibt einem Gedanken einen **Namen**. Wenn in deinem
Programm `Führe Runde_spielen aus.` steht, versteht man es, ohne die zwanzig Zeilen darunter zu
lesen.

**Deine Aufgabe:** Bau aus dem Ratespiel von Lektion 6 eine Aufgabe `Runde`, die eine komplette
Runde spielt. Ruf sie dreimal auf.

---

## Lektion 8 — Viele Werte auf einmal

**Das Problem:** Dein Spiel soll sich die Namen aller Mitspieler merken. Mit Variablen wird das
mühsam: `Spieler1`, `Spieler2`, `Spieler3` … und bei zehn Spielern?

Dafür gibt es die **Liste**:

```klar
Erstelle eine Liste namens Spieler mit "Anna" und "Ben" und "Rocco".
Zeige Spieler.
Zeige "Das sind " und die Länge von Spieler und " Mitspieler.".
```
```ausgabe
[Anna, Ben, Rocco]
Das sind 3 Mitspieler.
```

Eine Liste lässt sich durchgehen — und hier trifft sich alles, was du kannst:

```klar
Erstelle eine Liste namens Spieler mit "Anna" und "Ben" und "Rocco".
Für jeden Name in Spieler:
    Zeige "Willkommen, " und Name und "!".
Ende.
```
```ausgabe
Willkommen, Anna!
Willkommen, Ben!
Willkommen, Rocco!
```

Wächst eine Liste erst im Lauf des Programms, legst du sie leer an und füllst sie:

```klar
Erstelle eine Liste namens Einkauf.
Füge "Milch" zu Einkauf hinzu.
Füge "Brot" zu Einkauf hinzu.
Sortiere Einkauf.
Zeige Verkettet von Einkauf mit ", ".
```
```ausgabe
Brot, Milch
```

### Einzelne Plätze

```klar
Erstelle eine Liste namens Farben mit "rot" und "grün" und "blau".
Zeige das erste Element von Farben.
Zeige Element 2 von Farben.
Zeige das letzte Element von Farben.
```
```ausgabe
rot
grün
blau
```

**Gezählt wird ab 1** — das erste Element ist Element 1, so wie man es auf Deutsch sagen würde.
Merk dir das gut: In Lektion 11 wirst du sehen, dass Python das anders macht, und du wirst
verstehen, warum das kein Zufall ist.

### Einen Platz überschreiben

Dieselbe Stelle lässt sich auch beschreiben. Der Satz sieht aus wie beim Lesen — nur steht
`Setze` davor und `auf` dahinter:

```klar
Erstelle eine Liste namens Punkte mit 10 und 20 und 30.

Setze Element 2 von Punkte auf 25.
Erhöhe das letzte Element von Punkte um 5.

Zeige Punkte.
```
```ausgabe
[10, 25, 35]
```

Das brauchst du überall dort, wo sich etwas ändert statt dazuzukommen: ein Spielstand, ein
Spielfeld, eine Rangliste.

**Deine Aufgabe:** Lass drei Lieblingsessen eingeben, sammle sie in einer Liste und gib sie
sortiert und durchnummeriert aus.

---

## Lektion 9 — Daten ordnen (Kür)

> Diese Lektion ist **Kür**, kein Pflichtstoff. Wenn dir Listen gerade reichen, spring zu Lektion 10
> und komm später wieder. Wer wissen will, wie größere Programme ihre Daten ordnen, liest weiter.

**Das Problem:** Du baust einen Vokabeltrainer. Zu jedem deutschen Wort gehört ein englisches. Eine
Liste hilft nicht: Sie kennt nur *Plätze*, keine *Zuordnung*.

Dafür gibt es die **Tabelle** — zu jedem Schlüssel ein Wert:

```klar
Erstelle eine Tabelle namens Vokabeln mit "Hund" als "dog" und "Katze" als "cat".
Trage "Maus" mit "mouse" in Vokabeln ein.
Zeige Wert für "Hund" in Vokabeln.
```
```ausgabe
dog
```

Durchgehen kannst du sie auch — dabei bekommst du die Schlüssel:

```klar
Erstelle eine Tabelle namens Vokabeln mit "Hund" als "dog" und "Katze" als "cat".
Für jedes Wort in Vokabeln:
    Zeige Wort und " heißt " und Wert für Wort in Vokabeln und ".".
Ende.
```
```ausgabe
Hund heißt dog.
Katze heißt cat.
```

### Wenn mehrere Angaben zusammengehören

Ein Mitspieler hat einen Namen *und* Punkte *und* eine Farbe. Drei Listen nebeneinander zu führen,
die immer gleich sortiert sein müssen, geht schief. Dafür beschreibst du ein **Ding**:

```klar
Ein Hund hat einen Namen und ein Alter.

Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Rocco.
Erhöhe das Alter von Rocco um 1.
Zeige den Namen von Rocco und " ist " und Alter von Rocco und " Jahre alt.".
```
```ausgabe
Rocco ist 6 Jahre alt.
```

Und weil Dinge in Listen dürfen, lässt sich damit eine ganze Mannschaft führen:

```klar
Ein Hund hat einen Namen und ein Alter.

Erstelle eine Liste namens Rudel.
Erschaffe einen Hund mit Name "Rocco" und Alter 5 als Erster.
Erschaffe einen Hund mit Name "Bella" und Alter 2 als Zweiter.
Füge Erster zu Rudel hinzu.
Füge Zweiter zu Rudel hinzu.

Für jeden Hund in Rudel:
    Zeige Name von Hund und " (" und Alter von Hund und " Jahre)".
Ende.
```
```ausgabe
Rocco (5 Jahre)
Bella (2 Jahre)
```

**Deine Aufgabe:** Beschreibe ein Buch mit Titel, Autor und Seitenzahl. Leg drei Bücher in einer
Liste an und gib nur die aus, die mehr als 200 Seiten haben.

---

## Kür — Malen mit dem Stift

> Auch das hier ist **Kür**. Aber es macht Spaß, und es ist der schnellste Weg, ein Ergebnis zu
> sehen, auf das man zeigen kann.

**Das Problem:** Bisher kam alles als Text heraus. Jetzt soll ein Bild entstehen.

Stell dir einen Stift vor, der in der Mitte der Fläche steht und nach oben schaut. Du schickst ihn
los, und wo er langgeht, zieht er eine Linie.

```klar
Gehe 100 Schritte vor.
Drehe dich um 90 Grad nach rechts.
Gehe 100 Schritte vor.
```

**Vorhersagen:** Was entsteht hier? Zeichne es auf Papier, bevor du auf *Ausführen* drückst.

Ein Quadrat ist damit vier Sätze lang — und weil vier Mal dasselbe passiert, nimmst du das, was du
in Lektion 5 gelernt hast:

```klar
Nimm die Farbe "gold".
Wiederhole 4 Mal:
    Gehe 100 Schritte vor.
    Drehe dich um 90 Grad nach rechts.
Ende.
```

**Verändern.** Und jetzt wird es interessant:

* Mach `3 Mal` daraus und dreh um `120 Grad`. Was entsteht?
* `5 Mal` und `72 Grad`?
* Fällt dir die Regel auf? *(360 geteilt durch die Anzahl der Ecken.)*

Genau das ist ein Vieleck — und du hast es nicht auswendig gelernt, sondern hergeleitet:

```klar
Merke 6 als Ecken.
Nimm die Farbe "türkis".
Wiederhole Ecken Mal:
    Gehe 60 Schritte vor.
    Drehe dich um 360 geteilt durch Ecken Grad nach rechts.
Ende.
```

Mit `Hebe den Stift.` bewegst du dich, ohne zu malen, mit `Senke den Stift.` malst du wieder. Und
mit `Gehe zur Mitte.` fängst du von vorne an.

**Deine Aufgabe:** Zeichne eine Treppe aus fünf Stufen. Danach: Lass sie von einer Schleife
zeichnen statt von zehn einzelnen Sätzen.

Alles Weitere — Strichstärke, Farben, Spiralen, eine tickende Uhr — steht im Kapitel
[Zeichnen](https://www.ruthner.at/klarsatz/doku-zeichnen.html). Die Beispiele *Spirale*, *Wellen*
und *Baum* in der Spielwiese sind auch nur Schleifen mit Stift.

---

## Lektion 10 — Dein Abschlussprojekt

Hier bekommst du keine Lösung. Nur Anforderungen.

**Bau ein eigenes Programm.** Du darfst dir aussuchen, was:

* ein Quiz mit fünf Fragen
* ein Taschenrechner, der weiterfragt, bis man „ende" tippt
* ein Vokabeltrainer
* ein Einkaufsrechner mit Mehrwertsteuer
* ein winziges Textabenteuer mit drei Räumen
* etwas ganz anderes

**Dein Programm muss:**

- [ ] mindestens eine Eingabe entgegennehmen
- [ ] mindestens eine Variable benutzen und verändern
- [ ] mindestens eine Entscheidung treffen
- [ ] mindestens eine Schleife enthalten
- [ ] mindestens eine eigene Aufgabe haben
- [ ] verständlich reagieren, wenn jemand etwas Unerwartetes eintippt

**So gehst du vor.** Nicht von oben nach unten drauflosschreiben, sondern:

1. Schreib in **einem** deutschen Satz auf, was das Programm können soll.
2. Zerleg das in drei bis fünf Schritte. Auf Papier, nicht im Kopf.
3. Bau **einen** Schritt und lass ihn laufen. Erst wenn er tut, was er soll, kommt der nächste.
4. Wenn ein Fehler kommt: Lektion 4.

Der letzte Punkt ist der wichtigste, und er ist der Unterschied zwischen einem Anfänger und jemandem,
der programmieren kann: **kleine Schritte, jeden einzeln ausprobiert.**

Wenn dein Programm läuft, nimm dir vor, es um eine Sache zu erweitern, die du dir am Anfang nicht
zugetraut hättest.

---

## Lektion 11 — Dasselbe in Python

Und jetzt die Sache, auf die dieser ganze Kurs hinausläuft.

**Du hast nicht „Klarsatz gelernt". Du hast programmieren gelernt.** Klarsatz war die Schreibweise,
in der du es zum ersten Mal gesehen hast. Die Ideen dahinter — Variable, Bedingung, Schleife,
Aufgabe — sind in jeder Programmiersprache dieselben.

Klarsatz kann dir das zeigen: In der Spielwiese gibt es den Knopf **Als Python**. Auf der
Kommandozeile heißt er `--nach-python`. Probier das mit deinem Abschlussprojekt aus.

Hier dasselbe Programm zweimal:

```klar
Merke 10 als Punkte.
Wenn Punkte mindestens 10 ist:
    Zeige "Gewonnen!".
Sonst:
    Zeige "Noch nicht.".
Ende.
```
```python
Punkte = 10
if (Punkte >= 10):
    print('Gewonnen!')
else:
    print('Noch nicht.')
```

Zeile für Zeile:

| Klarsatz | Python | dieselbe Idee |
|---|---|---|
| `Merke 10 als Punkte.` | `Punkte = 10` | Variable anlegen |
| `Wenn … ist:` | `if …:` | Bedingung |
| `Punkte mindestens 10` | `Punkte >= 10` | vergleichen |
| `Sonst:` | `else:` | der andere Weg |
| `Zeige …` | `print(…)` | ausgeben |
| `Ende.` | *(Einrückung)* | Ende des Blocks |

**Nichts Neues.** Nur andere Zeichen.

Auch eine Schleife:

```klar
Zähle von 1 bis 5 mit i:
    Zeige i.
Ende.
```
```python
for i in range(1, 5 + 1):
    print(i)
```

**Vorhersagen:** Warum steht da `range(1, 5 + 1)` und nicht `range(1, 5)`?

<details><summary>Antwort</summary>

Weil `range` in Python die **obere Grenze nicht mitzählt**. `range(1, 5)` gäbe 1, 2, 3, 4 — die 5
fehlte. Klarsatz zählt `von 1 bis 5` so, wie man es auf Deutsch meint: die 5 gehört dazu. Der
Übersetzer schreibt darum `5 + 1` und macht den Unterschied damit sichtbar, statt ihn zu verstecken.

</details>

Auch ein eigener Baustein:

```klar
Definiere Aufgabe Begrüße mit Name:
    Zeige "Hallo, " und Name und "!".
Ende.

Führe Begrüße mit "Anna" aus.
```
```python
def Begrüße(Name):
    print('Hallo, ', Name, '!', sep='')

Begrüße('Anna')
```

| Klarsatz | Python |
|---|---|
| `Definiere Aufgabe Begrüße mit Name:` | `def Begrüße(Name):` |
| `Führe Begrüße mit "Anna" aus.` | `Begrüße('Anna')` |

Und eine Liste:

```klar
Erstelle eine Liste namens Farben mit "rot" und "grün" und "blau".
Zeige das erste Element von Farben.
Für jede Farbe in Farben:
    Zeige Farbe.
Ende.
```
```python
Farben = ['rot', 'grün', 'blau']
print(Farben[0])
for Farbe in Farben:
    print(Farbe)
```

Hier fällt etwas auf — und das ist der nächste Abschnitt.

### Und das mit dem Zählen ab 1

In Lektion 8 hast du gelernt: Das erste Element ist Element 1. In Python ist es Element 0:

| Klarsatz | Python |
|---|---|
| `das erste Element von Farben` | `Farben[0]` |
| `Element 2 von Farben` | `Farben[1]` |

Genau das steht oben in der Übersetzung: Aus `das erste Element` wird `Farben[0]`.

Das ist kein Fehler auf einer der beiden Seiten. Es ist eine **Entscheidung**, und die beiden
Sprachen haben sie verschieden getroffen: Klarsatz zählt wie Menschen, Python zählt wie die meisten
Programmiersprachen — nämlich den Abstand vom Anfang.

Genau das ist die letzte Lektion dieses Kurses:

> Programmiersprachen treffen unterschiedliche Entscheidungen.
> Wer die Idee dahinter verstanden hat, lernt die nächste Sprache als Schreibweise — nicht von vorn.

### Wo tippt man Python ein?

Dieselbe Frage wie am Anfang dieses Kurses — hier die Antworten, von einfach nach richtig:

| Womit | Wie du hinkommst |
|---|---|
| **Online, ohne Installation** | Auf [python.org](https://www.python.org/shell/) oder bei [Programiz](https://www.programiz.com/python-programming/online-compiler/) gibt es ein Eingabefeld im Browser — wie die Spielwiese, nur für Python. Zum Ausprobieren einzelner Zeilen ideal. |
| **Thonny** *(empfohlen zum Lernen)* | Ein kleiner Editor, eigens für Anfänger gemacht: [thonny.org](https://thonny.org). Python ist gleich mit dabei, man installiert nur eine Sache. Er zeigt beim Laufen Schritt für Schritt, was das Programm gerade tut. |
| **IDLE** | Ist bei jeder Python-Installation von [python.org](https://www.python.org/downloads/) dabei. Schlicht, aber genügt. |
| **Auf dem Raspberry Pi** | Python und Thonny sind schon installiert — einfach im Menü suchen. |

Ein Python-Programm ist eine Textdatei, die auf `.py` endet. Speichere sie als `meins.py` und
drück in Thonny auf *Run*.

> **Ein Unterschied, den du gleich merken wirst:** Python spricht Englisch, auch bei Fehlern.
> Statt „Hier fehlt ein Punkt am Satzende" steht dort `SyntaxError: invalid syntax`. Das ist
> gewöhnungsbedürftig, aber es ist dieselbe Art von Nachricht — und du weißt jetzt, dass man sie
> liest, statt zu erschrecken.

### Wie es weitergeht

* Übersetze dein Abschlussprojekt mit **Als Python** und lies es Zeile für Zeile.
* Tipp es in Thonny ein und lass es dort laufen. Ändere eine Zahl. Es tut, was du erwartest.
* Wenn dir dabei nichts wirklich fremd vorkommt: Dann hat dieser Kurs funktioniert.

---

## Häufige Stolperfallen

| Fehler | Richtig |
|---|---|
| `Zeige "Hallo"` | Der **Punkt** am Ende fehlt: `Zeige "Hallo".` |
| `Zeige Hallo.` | Ohne Anführungszeichen ist das ein Name, kein Text. |
| `Wenn Name "Anna" ist:` | `gleich` ist Pflicht: `Wenn Name gleich "Anna" ist:` |
| `Setze Punkte auf 0.` ohne vorheriges `Merke` | `Setze` ändert nur, was es schon gibt. |
| `Definiere Aufgabe Zeige Summe:` | Aufgabennamen sind **ein** Wort: `Zeige_Summe` |
| `Zeige Element 0 von Liste.` | Gezählt wird ab **1**. |
| `Merke 3,5 als x.` | In der Eingabe der **Punkt**: `Merke 3.5 als x.` Angezeigt wird `3,5`. |
| Ein Block ohne `Ende.` | Jeder `:`-Block braucht sein `Ende.` |
