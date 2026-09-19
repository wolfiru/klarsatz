# Sicherheit

Klarsatz ist ein **Lern- und Hobbyprojekt**, keine geprüfte Sandbox. Der Interpreter ist bewusst auf
Schadensbegrenzung gebaut — was abgesichert ist und was ausdrücklich **nicht**, steht offen in
[`docs/SICHERHEIT.md`](docs/SICHERHEIT.md). Wer fremde, nicht vertrauenswürdige Programme ausführt,
sollte das zusätzlich in einem Container oder als Benutzer mit wenigen Rechten tun.

## Eine Lücke melden

Wenn du einen Weg findest, mit einem Klarsatz-Programm aus dem Interpreter auszubrechen — etwa an
ein Python-Objekt zu kommen, den Dateischutz zu umgehen, die Grenzen auszuhebeln oder einen
Python-Traceback nach außen zu bringen —, dann ist das ein Fehler, über den ich mich (mit gemischten
Gefühlen) freue.

Melde ihn bitte über [Security Advisories](../../security/advisories/new), nicht als öffentliches
Issue. Ich schaue in meiner Freizeit hinein; eine Antwortfrist kann ich nicht zusagen.

Nicht als Lücke gelten: Endlosschleifen oder Speicherhunger **innerhalb** der eingestellten Grenzen,
und alles, was `docs/SICHERHEIT.md` bereits als nicht abgesichert benennt.
