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
* Keine Prüfung durch Dritte, kein Fuzzing über die mitgelieferten Tests hinaus (siehe ÜBERGABE.md, „Offen“).

## Melden
Probleme bitte mit einem kleinen Programm, das sie zeigt.
