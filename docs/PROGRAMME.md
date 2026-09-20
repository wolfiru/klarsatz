# Klarsatz-Programme zum Ausprobieren

Alle Programme liegen in `programme/` und laufen mit:

```
python3 -m klarsatz programme/03_taschenrechner.klar
```

Die Reihenfolge folgt dem Schwierigkeitsgrad: vorne genügen Eingabe, Rechnen und
Bedingungen, hinten kommen Tabellen, Dateien, Rekursion und Zeichnen zusammen.

Sie fragen mit `Frage` und geben mit `Zeige` aus – also einfach im Terminal mitspielen.
Für Zufallszahlen lässt sich mit `--seed 42` immer derselbe Ablauf erzeugen.

| Nr. | Datei | Was es macht | Zeigt vor allem |
|---|---|---|---|
| 01 | `01_zahlenraten_du_raetst.klar` | Der Computer denkt sich eine Zahl aus (1–10, 1–100 oder 1–1000), du rätst. | `Zufallszahl von … bis …`, Hinweise „zu klein/zu groß“ |
| 02 | `02_kopfrechnen.klar` | Zehn Kopfrechenaufgaben (plus, minus, mal), am Ende Punkte und Note. | `Zufallszahl`, `Verbinde`, `Zähle` |
| 03 | `03_taschenrechner.klar` | Zwei Zahlen und eine Rechenart eingeben (`+ - * / ^ %`), Ergebnis sehen. Division durch 0 wird abgefangen. | `Frage`, `Wenn … Sonst wenn`, `Versuche`, „keine Zahl“-Test |
| 04 | `04_umrechner.klar` | °C/°F, km/Meilen, Euro/Fremdwährung mit selbst eingegebenem Kurs. | Rechnen, `Formatiert von … auf 2 Stellen`, Eingabeprüfung |
| 05 | `05_primzahlen.klar` | Primzahltest, alle Primzahlen bis zu einer Grenze, alle Teiler einer Zahl. | Aufgaben mit `Gib … zurück`, Schleifen, `teilbar`, Listen |
| 06 | `06_notenrechner.klar` | Noten (1–5) eingeben; Durchschnitt, beste/schlechteste Note, Warnung bei „Nicht genügend“. | Listen, `Sortieren`, `Länge von`, leere Eingabe beendet |
| 07 | `07_schere_stein_papier.klar` | Gegen den Computer mit Punktestand; „ende“ beendet. | Zufall, Rest-Rechnung für die Spielregeln |
| 08 | `08_zahlenraten_computer_raet.klar` | Umgekehrt: **du** denkst dir eine Zahl von 1–10 aus, der Computer errät sie mit Halbieren. | `Frage` mit Antworten `h`, `n`, `r` |
| 09 | `09_palindrom.klar` | Ist mein Text ein Palindrom? Dazu Buchstaben, Vokale und Wörter zählen. | Texte, `Für jedes … in Text`, `Teile … bei`, `enthält` |
| 10 | `10_vokabeltrainer.klar` | Deutsch → Englisch abfragen (5 zufällige Fragen), eigene Wörter hinzufügen. | Dinge (`Wort hat Deutsch und Englisch`), Listen von Dingen, `Zufallszahl` |
| 11 | `11_galgenmaennchen.klar` | Gegen den Computer (zufälliges Wort) oder zu zweit; mit ASCII-Galgen. | Texte, Listen, mehrere Zustände, `enthält` |
| 12 | `12_vielecke.klar` | Zeichnet sechs Vielecke von drei bis acht Ecken, jedes in einer anderen Farbe. | Zeichnen, Aufgabe mit zwei Werten, `Für jedes` |
| 13 | `13_spirale.klar` | Eine sechseckige Spirale, die mit jeder Drehung länger und bunter wird. | Zeichnen, `Element n von`, Rest-Rechnung |
| 14 | `14_wellen.klar` | Sinus und Kosinus als Wellenlinien in zwei Farben, dazu eine Wertetabelle. | Winkelfunktionen, `LinieZu` mit Arkustangens, Achsen |
| 15 | `15_baum.klar` | Ein rekursiver Baum – jeder Ast trägt zwei kleinere Äste. | Zeichnen, Rekursion, Klammern bei Argumenten |
| 16 | `16_uhr.klar` | Eine Analoguhr mit Zifferblatt und drei Zeigern, die die Uhrzeit dieses Rechners zeigt. | Zeichnen, `die aktuelle Stunde`, Winkelrechnung |
| 17 | `17_warenkorb.klar` | Kleiner Shop: Preisliste, Artikel in den Warenkorb legen und entfernen, Summe. | Tabellen, Aufgaben ohne Rückgabe, Menü-Schleife |
| 18 | `18_todo_liste.klar` | Aufgaben anlegen, abhaken, löschen; wird in `todo.txt` gespeichert und beim Start wieder geladen. | Dateien, `Teile`, Dinge, Menü-Schleife |
| 19 | `19_textadventure.klar` | Ein verlassenes Haus mit fünf Räumen, Gegenständen und Inventar. | Tabellen als Weltmodell, `Teile`, Befehle auswerten |
| 20 | `20_grafisches_adventure.klar` | Dasselbe Haus, aber gezeichnet: Raum, Türen (gold = offen, rot = verschlossen) und Gegenstände. Finde das Marmeladenglas, öffne es, schließe die Küchentür auf. | Zeichnen + Spiellogik, `Lösche die Zeichnung`, Tabellen |
| 21 | `21_spiel_des_lebens.klar` | Conways Spiel des Lebens: 22 mal 16 Zellen, zufälliger Start, dreißig Generationen als bewegtes Bild. | `Nimm die Leinwand`, Liste als Gitter, toter Rand statt Kantenabfragen, Aufgabe gibt eine Liste zurück |
| 22 | `22_routenplaner.klar` | Zwölf Orte in Niederösterreich und Wien, neunzehn Straßen: Dijkstra sucht die kürzeste Verbindung zwischen zwei ausgewürfelten Orten und zeichnet sie in die Karte. | Tabellen als Graph, `Trage … ein`, `Beschrifte`, Arkustangens für die Linienrichtung |

Die Zeichenprogramme brauchen eine Zeichenfläche: im Browser die
[Spielwiese](../playground/), auf der Kommandozeile `--bild bild.svg`.

Getestet werden alle Programme mit einem simulierten Menschen: `python3 -m unittest -v tests.test_programme`.
