# Sicherheit und Grenzen

Klarsatz ist ein **Lern- und Hobbyprojekt**. Der Interpreter ist so gebaut, dass ein Programm möglichst wenig
Schaden anrichten kann – er ist aber **keine geprüfte Sandbox**. Fremde, nicht vertrauenswürdige Programme sollten
zusätzlich in einem Container oder als eigener Benutzer mit wenigen Rechten laufen.

## Was der Interpreter absichert
| Gefahr | Maßnahme |
|---|---|
| Endlosschleife | `--limit` (Schritte), `--zeit` (Sekunden); nicht mit `Versuche` abfangbar |
| Speicherfresser | Grenzen für Text, Liste/Tabelle, Zahlengröße, Ausgabe, Eingabezeile, Programmgröße |
| Absturz durch Verschachtelung | Tiefengrenze im Parser, Rekursionsgrenze für Aufgaben, kein Python-Traceback |
| Dateien | Standard: nur Arbeitsordner und darunter (kein `..`, keine absoluten Pfade, keine Symlink-Ausbrüche); `--ohne-dateien`; im Browser nur Arbeitsspeicher |
| Code-Einschleusung | kein `eval`/`exec`, kein Nachladen, kein Zugriff auf Python-Objekte |
| Netzwerk, Prozesse | gibt es in der Sprache nicht |

Für fremde Programme: `--streng-grenzen` (bzw. `Grenzen.streng()`), `--ohne-dateien`, und die Web-Schnittstelle
(`klarsatz/web.py`) verwendet diese strengen Grenzen und ein Dateisystem im Arbeitsspeicher.

## Was NICHT abgesichert ist
* Der Interpreter läuft im selben Python-Prozess: ein Fehler im Interpreter selbst (Bug) könnte Grenzen umgehen.
* Die Zeitgrenze wird nur zwischen Schritten geprüft; eine einzelne, sehr teure Rechnung (z. B. riesige Zahl mal
  riesige Zahl) läuft bis zum Ende – begrenzt durch die Zahlengröße.
* `--dateien-ueberall` hebt den Ordnerschutz auf.
* Keine Prüfung durch Dritte. Gefuzzt wird (siehe unten), aber von niemandem außerhalb des Projekts.

## Was der Fuzz-Test zeigt

Die Zusage „ein Programm kann den Interpreter nicht aus der Bahn werfen“ war lange nur mit *gültigen*
Programmen geprüft. Seit 19.09.2026 gibt es einen Fuzz-Test, der sie angreift: Er nimmt die
mitgelieferten Programme und zerhackt sie zufällig — Zeichen löschen, einfügen, ersetzen; Wörter
löschen, doppeln, vertauschen; Zeilen löschen und vertauschen; Einrückung verbiegen; Punkte und
Doppelpunkte entfernen; abschneiden; Zahlen durch Grenzfälle ersetzen (0, −1, sehr groß); Texte
austauschen. Das Ergebnis geht an alles, was Quelltext entgegennimmt: `laufe()`, `pruefe()`,
`formatiere()` und `nach_python()`.

**Erlaubt ist genau ein Ausgang: ein `KlarsatzFehler`.** Jede andere Python-Ausnahme gilt als Fund,
und wer länger als die Zeitgrenze braucht, gilt als Hänger — beides wird gemeldet, nicht verschluckt.

Damit der Test nicht bloß freundlich aussieht, prüft er sich selbst mit: Ein untergeschobener
Python-Fehler und ein untergeschobener Hänger *müssen* erkannt werden, und ein nennenswerter Teil
der Mutanten muss wirklich bis in den Interpreter vordringen statt schon am Parser abzuprallen
(derzeit rund ein Fünftel). Dazu kommen handverlesene Gemeinheiten, die der Zufall selten trifft:
leerer Quelltext, 5000 ineinandergeschachtelte Klammern, 500 verschachtelte Blöcke, 20 000 Zeilen,
Zahlen mit 400 Stellen, Nullbytes, Emojis, unvollständige Sätze.

**Stand 19.09.2026:** 60 000 Beschüsse (Saat 4711, 446 Sekunden auf einem Raspberry Pi 4) —
**keine einzige Panne**. Kein Python-Traceback, kein Hänger, alles endete als Klarsatz-Fehler.
Wiederholbar mit `python3 tools/fuzze.py --laeufe 60000 --saat 4711`. Einmal pro Woche läuft in
der CI eine noch längere Fassung mit wechselnder Saat.

Was der Test **nicht** zeigt: dass es keine Lücke gibt. Er zeigt, dass eine große Zahl zufälliger
Angriffe keine gefunden hat. Das ist ein Beleg, kein Beweis.

    python3 tools/fuzze.py --laeufe 200000      # lange Dauerbeschießung
    python3 tools/fuzze.py --wiederhole SAAT    # einen einzelnen Fund nachstellen

## Melden
Probleme bitte mit einem kleinen Programm, das sie zeigt.
