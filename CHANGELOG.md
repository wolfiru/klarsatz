# Änderungen

## 0.10.3 — Im Kurs selbst tippen
- **Unter jeder Aufgabe liegt jetzt eine Fläche zum Lösen.** „Deine Aufgabe: …" stand bisher da,
  ohne dass man ihr nachkommen konnte, ohne die Seite zu verlassen. Ein Klick auf „Leeres Blatt
  öffnen" holt dieselbe Spielwiese hierher, die auch die Beispiele ausführt — mit der Angabe als
  `Anmerkung` schon im Editor, damit beim Tippen niemand nach oben scrollen muss.
- **Aufgaben können ein lauffähiges Programm mitbringen.** „Bau absichtlich drei Fehler ein" ergibt
  auf einem leeren Blatt keinen Sinn. Ein `vorlage`-Block in `docs/TUTORIAL.md` steht jetzt in der
  Aufgabenfläche und landet beim Klick mit im Editor; `tests/test_tutorial.py` führt ihn wie jedes
  andere Beispiel aus, `tools/pruefe_webseite.py` prüft ihn auf der fertigen Seite mit.
- **Der Knopf am Codeblock heißt „Hier ausführen/editieren".** Dass man den Text im Kasten auch
  ändern kann, stand nirgends.
- **Schulnoten in Lektion 3 korrigiert:** Dort galt „Note 7 ist gut" — eine Skala, die es hier nicht
  gibt. Jetzt 1 bis 5, wie in Österreich, und damit `höchstens` statt `mindestens`.

## 0.10.2 — WebAnalyzer-Durchgang
- **Eigene Datenschutzseite** (`/datenschutz.html`) statt eines Ankers im Impressum, im Stil der
  Hauptseite. Sie sagt, was der Klarsatz-Bereich im Browser speichert (Aufgaben-Fortschritt in
  `localStorage`), dass Cloudflare ein technisches Cookie zur Bot-Abwehr setzen kann, und dass die
  Schriften von diesem Server kommen. Der alte Anker `/impressum.html#datenschutz` funktioniert
  weiter und verweist dorthin.
- **Inhaltsrichtlinie durchgesetzt:** Die CSP lief als Report-Only über alle Seiten samt Spielplatz
  und Aufgaben, ohne einen einzigen Verstoß — jetzt ist sie scharf, und zwar ohne `'unsafe-inline'`
  bei Skripten (es gibt kein einziges Inline-Skript). Danach nochmals mit leerem Zwischenspeicher
  geprüft: Spielplatz läuft, zwölf von zwölf Aufgaben bestanden.
- **`/.well-known/security.txt`** und **`/llms.txt`** angelegt, eine gestaltete **404-Seite auch im
  Wurzelverzeichnis** (vorher nur unter `/klarsatz/`).
- **Metadaten:** Beschreibung der Startseite von 227 auf 145 Zeichen, Titel um Suchbegriffe
  ergänzt, vollständige Twitter-Angaben und `og:site_name`/`og:locale`/`og:image:*` auf allen
  Seiten, **JSON-LD** (WebSite, SoftwareSourceCode mit Version und Repository, FAQPage aus den
  echten acht Fragen) und Brotkrumen auf den Unterseiten.
- **Sichtbarer Stand** in jeder Fußzeile: Datum als `<time>`, Version, Lizenz und Autor.
- **Ein Zahlenblock** auf der Startseite mit Werten, die im Repository nachzählbar sind — ein Test
  zählt sie nach.
- **Performance:** Das Kopfbild lädt nicht mehr `lazy`, sondern mit `fetchpriority="high"`; alle
  eigenen Skripte mit `defer`; Web-App-Manifest samt Symbolen (192/512); `color-scheme`; das
  92-kB-Favicon der Hauptseite auf 7 kB.
- `tests/test_metadaten.py` hält all das fest — inklusive der Prüfung, dass die FAQ-Daten Wort für
  Wort von der Seite stammen und nichts erfunden ist.

## 0.10.1 — QA-Durchgang vom 20.09.2026
Aus einer externen Prüfung, vollständig abgearbeitet.
- **Weiterleitung ohne Schrägstrich** (kritisch): `/klarsatz` endete in einer Kette, weil Apaches
  DirectorySlash die Adresse aus dem Serverport bildete — und Cloudflare den Ursprung über http
  anfragt. Jetzt beantwortet eine `RedirectMatch` den Fall selbst: genau ein 301 nach
  `https://www.ruthner.at/klarsatz/`.
- **Impressum und Datenschutz** stehen jetzt in der Fußzeile aller elf Seiten, dazu die MIT-Lizenz;
  das Impressum hat einen Anker `#datenschutz` bekommen.
- **Schriften kommen von hier** statt von Google: `tools/hole_schriften.py` lädt Fraunces, Manrope
  und JetBrains Mono (alle OFL) nach `assets/fonts/` und schreibt die `@font-face`-Regeln in
  `style.css`. Als Gewichtsbereich statt Einzelschnitten — sonst liefert Google die ganze variable
  Datei pro Gewicht (480 statt 200 kB). Keine Anfrage verlässt mehr die Seite.
- **Kein Seitwärtsscrollen mehr** bei 320, 375 und 414 Pixeln (zwölf Seiten geprüft). Ursachen
  waren Inline-Code mit `white-space: nowrap`, der Kopf über Codeblöcken und die Beispielauswahl.
- **Metadaten:** doppelte og-Angaben auf der Startseite entfernt, vollständige og/twitter-Angaben
  auf allen Seiten und in beiden Seitenbauern, Kurse und Aufgaben in der Sitemap, `robots.txt`
  angelegt, `favicon.ico` erzeugt und verlinkt, `canonical` überall.
- **Ladezustand:** Der Ausführen-Knopf heißt jetzt „⏳ Klarsatz lädt …", bis Python bereit ist; die
  Aufgabenseite hält Abgeben und Musterlösung so lange zurück.
- **Monogramm:** 322 kB für ein Bild, das 21 Pixel breit erscheint — jetzt 4,9 kB in doppelter
  Auflösung, und die Klarsatz-Seiten benutzen ihre eigene Fassung.
- **Sicherheitskopfzeilen** (X-Content-Type-Options, Referrer-Policy, X-Frame-Options,
  Permissions-Policy, CSP zunächst als Report-Only mit `wasm-unsafe-eval`), Haltbarkeit für
  gestempelte Dateien (ein Jahr, immutable) und für Schriften (30 Tage).
- **Barrierefreiheit:** „Zum Inhalt springen", sichtbarer Tastaturfokus über `:focus-visible`,
  `aria-hidden` für die Hintergrundgrafik, `aria-label` für die Navigation, und im Editor führt
  Escape wieder heraus (Tab rückt dort ein, sonst käme man beim Programmieren nicht voran).
- **Korrekturgelesen:** Startseite und Kurs waren bisher nur maschinell geprüft. Gefunden und
  berichtigt: „ein Programm, das sich selbst überlässt" (es wird überlassen), zweimal „entwickelt"
  im selben Atemzug bei Robot Karol, eine verdrehte Satzstellung im Zeichenkurs-Absatz — und vor
  allem **17 Anführungszeichen**, die mit einem geraden `"` statt mit `“` schlossen (Kurse,
  Startseite, Doku-Kapitel, Aufgaben, Sprach- und Sicherheitsdoku). Der Wegweiser am Kursanfang
  nennt jetzt „Hier ausführen" als ersten Weg in die Spielwiese.
- **Eigene 404-Seite** mit Wegweisern, **Druckansicht** für Kurs und Doku (heller Grund, ohne
  Navigation, Linkziele ausgeschrieben), **noscript-Hinweise** auf Aufgaben-, Kurs- und Doku-Seiten.

## 0.10.0
- **Nach einem kritischen Review nachgeschärft:** Die Punkte in der Eignungstabelle heißen jetzt
  **„Meine Einschätzung"**, und darüber steht, dass sie vom Autor stammen und kein Messergebnis
  sind. Die Zahlen bleiben — gerade die 1/10 für das, wofür Klarsatz nichts taugt, macht die
  Tabelle glaubwürdig; was störte, war der Anschein von Objektivität. Bei den Fuzz-Zahlen steht
  jetzt „in diesen Läufen" und ein Satz zum Unterschied zwischen *ist nicht passiert* und *kann
  nicht passieren*. Die These im Abschnitt „Die Idee" ist auf den Punkt gebracht: Klarsatz will
  das Programmieren nicht einfacher machen, sondern **zwei Lernprobleme zeitlich auseinanderziehen**.
- **Canonical-Adressen** auf allen Seiten, auch in den beiden Seitenbauern.
- **Logo vervollständigt:** eine einfarbige Fassung (`currentColor`, für Ausdruck und Stempel) und
  das Symbol der VS-Code-Erweiterung, das `tools/baue_logo.py` gleich mit in den Editor-Ordner legt.
- **„Hier ausführen" in Kurs und Dokumentation.** Bisher führte jeder Codeblock nur über einen Link
  in den Spielplatz — also aus der Lektion heraus, mit dem Text daneben verloren. Jetzt kommt die
  Spielwiese zum Block: Sie erscheint direkt darunter, lädt beim ersten Klick und **wandert**
  danach nur noch, statt sich zu vermehren. Es gibt sie genau einmal pro Seite, denn Pyodide sind
  14 MB. Der Link in den Spielplatz bleibt für alle, die mit mehr Platz weitermachen wollen.
- **Ein Logo** — und zwar keines, das neu erfunden wurde: Der goldene Punkt stand schon im
  Seitenkopf, und das alte Favicon zeigte Textzeilen, deren letzte mit einem Punkt endet. Der
  **Punkt am Satzende** ist ja die eine Regel, über die bei Klarsatz jeder stolpert.
  `tools/baue_logo.py` erzeugt daraus das **Signet** (drei Zeilen, goldener Punkt; dazu eine
  vereinfachte Fassung für 16 Pixel, eine ohne Kachel und eine für hellen Grund) und die
  **Wortmarke** „Klarsatz" in Fraunces — deren Buchstaben werden zu Pfaden umgerechnet, damit sie
  auch dort stimmt, wo die Schrift fehlt. Dazu Avatar (512), Touch-Symbol (180) und ein
  Vorschaubild (1200×630) für geteilte Links.
- **Überschriften kleiner:** Die Kopfzeile der Startseite war bei 1280 Pixeln 102 Pixel hoch; jetzt
  sind es 78. Abschnittsüberschriften und die Kopfzeilen der übrigen Seiten ziehen mit.
- **Übungsaufgaben, die sich selbst prüfen** — der letzte offene Punkt der Ausbaustufen.
  `docs/AUFGABEN.md` enthält zwölf Aufgaben von Stufe 1 bis 7, jede mit der Lektion, nach der sie
  zu schaffen ist. Geprüft wird **nicht auf wortgleiche Ausgabe** — das würde jede Lösung ablehnen,
  die dasselbe tut und es anders sagt. Stattdessen läuft das Programm mit festen Antworten, und
  dann zählen Regeln: `enthält`, `enthält nicht`, `letzte Zeile`, `zeilen`, `fragt`, `striche`,
  `benutzt`, `benutzt nicht`. *„Die Fläche ist 12"* und *„12 Quadratmeter"* sind beide richtig.
- **Drei Wege hin:** die Seite [Übungsaufgaben](https://www.ruthner.at/klarsatz/aufgaben.html) mit
  Angabe, Editor und Abgeben-Knopf; `klarsatz --aufgabe 3 meine_loesung.klar` auf der
  Kommandozeile; und `web.pruefe_aufgabe_json` für alles andere. Geprüft wird überall von
  `klarsatz/aufgaben.py` — es gibt keine zweite Wahrheit darüber, ob eine Lösung reicht.
- **Jede Aufgabe bringt eine Gegenprobe mit:** eine absichtlich unzureichende Lösung, die
  durchfallen *muss*. Ohne sie merkt niemand, wenn eine Regel zu lasch ist. Ein Test verlangt
  zusätzlich, dass die Gegenprobe an einer Regel scheitert und nicht an einem Syntaxfehler — sonst
  prüft man den Parser statt der Regeln. Und ein weiterer führt jede Musterlösung mit der Lernstufe
  ihrer Aufgabe aus: Die Stufe ist ein Versprechen, dass nichts vorkommt, was noch nicht dran war.

## 0.9.0
- **Abschnitt „Harte Fragen"** auf der Startseite (`#fragen`): acht Einwände, die gegen ein Projekt
  wie dieses auf der Hand liegen — neue Programmiersprache? für wen? warum nicht gleich Python?
  warum nicht Scratch? ist Deutsch nicht ein Nachteil? und wenn jemand dabei bleibt? didaktisch
  erprobt? im Unterricht erlaubt? — jeweils mit der ehrlichsten Antwort, nicht der günstigsten.
  Auf die Frage nach der Erprobung steht „Nein" als erstes Wort, und `tests/test_fragen.py` sorgt
  dafür, dass das so bleibt: Es prüft, dass die unbequemen Fragen gestellt werden, dass die
  Antworten die Grenzen benennen („Bewiesen ist sie nicht", „keine Studie", „Hobbyprojekt") und
  dass kein anderer Ansatz abgewertet wird.
- **Mitmachen sichtbar gemacht:** drei Wege (im Unterricht ausprobieren, Fehler melden, Quelltext
  lesen oder forken) mit Links dorthin, „Fehlerberichte und Pull Requests sind willkommen", dazu
  ein Verweis auf das Repository schon im Seitenkopf.
- **Stellen in Listen und Tabellen lassen sich jetzt beschreiben.** Gelesen wurden sie immer schon,
  geschrieben nicht — wer ein Spielfeld, eine Rangliste oder einen Spielstand führen wollte, musste
  die Liste jedes Mal neu aufbauen. Und der Versuch endete in einer Meldung, die nicht einmal sagte,
  dass es den Satz nicht gibt („Hier erwarte ich 'auf', gefunden habe ich aber die Zahl 2").

  ```
  Setze Element 2 von Punkte auf 25.
  Setze das letzte Element von Punkte auf 0.
  Erhöhe Element 1 von Punkte um 5.          (ebenso Verringere, Verdopple, Halbiere)
  Setze Wert für "Apfel" in Preise auf 4.    (legt den Eintrag an, wenn es ihn nicht gibt)
  Erhöhe Wert für "Apfel" in Preise um 1.    (setzt ihn voraus)
  ```

  Geprüft wird beim Schreiben dasselbe wie beim Lesen: Eine Nummer außerhalb der Liste ist ein
  Fehler mit derselben Meldung, nie ein stiller Fehlgriff. Ein Text lässt sich nicht an einer
  Stelle ändern — dafür gibt es `Ersetze "alt" durch "neu" in Text.`, und die Meldung sagt das auch.
  „Element" bleibt ein erlaubter Variablenname.
- **`tools/hebe_version.py`** hebt die Nummer an allen zehn Stellen zugleich. Von Hand ist das
  einmal schiefgegangen.

## 0.8.3
Eine Aufräumversion: Die Doku sagt jetzt überall dasselbe wie der Code.
- **Drei falsche Aussagen berichtigt.** `docs/SPRACHE.md` behauptete unter „Bekannte Grenzen", dass
  sich Bedingungen nicht klammern lassen (sie lassen sich), dass es keine Möglichkeit gebe, eine
  Liste zu einem Text zusammenzufügen (`Verkettet von Liste mit ", "` gibt es seit Langem) und dass
  es kein Dezimalkomma in Zahleneingaben gebe (in **Antworten** ist es erlaubt, nur im Quelltext
  trennt das Komma Satzteile). `tests/test_doku_konsistenz.py` führt diese Sätze jetzt aus, statt
  sie zu glauben.
- **Gliederung der Sprachdefinition:** Die angehängten Kapitel hießen „Neu ab Version 0.2",
  „Zeichnen (neu)" und „Uhrzeit und Datum (neu)" — Zeitmarken aus einer Zeit, in der das neu war.
  Jetzt sind es die Kapitel 14 bis 16, „Bekannte Grenzen" steht als 17 am Ende, und die Kopfzeile
  nennt nicht mehr „Prototyp 0.1".
- **Konsistenz wird geprüft, nicht gehofft:** Version (sieben Dateien), Programmzahlen (vier
  Stellen), Vollständigkeit der Befehlstabellen und die Kapitelnummerierung.
- Nachgezogen: `Nimm die Leinwand` und `Beschrifte` im Referenzkapitel und in der Kapitelübersicht,
  Beschriftungen mit eigenem Beispiel im Zeichenkapitel, aktuelle Zahlen in `ÜBERGABE.md`
  (Tests, Programme, GitHub) und das Versionsrezept in den Arbeitsregeln.
- **Tabellen und Diagramme stehen auf einer eigenen Fläche.** Sie lagen unmittelbar auf dem
  Seitenhintergrund und liefen dadurch optisch mit dem Fließtext zusammen; jetzt tragen sie
  dieselbe hellere Fläche wie Hinweiskästen und Werkstücke. Der innere Rahmen der Lernsprachen-Karte
  tritt dafür zurück — zwei gleich kräftige Rahmen ineinander sahen aus wie ein Versehen.

## 0.8.2
- **`Für jeden Ort`, `Für jede Strecke`, `Für jedes Element`** — der Parser ließ alle drei Formen
  schon immer zu, die Programme und die Doku schrieben aber überall „jedes". „Für jedes Ort" ist
  falsches Deutsch, und eine Sprache, die wie Deutsch aussehen will, sollte das nicht vormachen.
  18 Stellen in Programmen, Kursen und Doku berichtigt; die Fehlermeldung nennt jetzt alle drei
  Formen, und ein Test hält die Beispielprogramme beim richtigen Geschlecht.
- **`Beschrifte` nimmt mehrere Teile** — `Beschrifte Ecken und " Ecken".` statt erst mühsam einen
  Text zusammenbauen. Genau wie bei `Zeige`.
- **Doku auf 0.8 nachgezogen:** `Nimm die Leinwand` und `Beschrifte` stehen jetzt auch im
  Referenzkapitel der Webseite und in der Kapitelübersicht; Lektion 8 des Zeichenkurses zeigt
  beides an ihrem eigenen Beispiel (das wachsende Vieleck zappelte ohne feste Leinwand).
  Die README nennt die richtigen Zahlen — und ein Test zählt sie künftig nach, so wie es ihn für
  die Webseite längst gibt.

## 0.8.1
- **Der Versionsstempel erreicht jetzt jede nachgeladene Datei.** Die Demos auf der Startseite
  holen die Spielwiese über `await import('./../spielwiese/klarsatz-playground.js')` — und genau
  diese Form kannte `tools/stempel_webseite.py` nicht; es stempelte nur feste Einbindungen
  (`import … from`). Ohne Stempel nahm der Browser den Interpreter aus dem Zwischenspeicher: eine
  alte Fassung, die `Beschrifte` noch nicht kannte, während die Seite schon ein Programm damit
  anbot („Ich verstehe den Satz nicht: er beginnt mit 'Beschrifte'."). Gestempelt werden jetzt
  auch nachgeladene Module und schlichte Pfade in Zeichenketten; die Spielwiese reicht ihren
  Stempel an ihre eigene Hervorhebung weiter. `tests/test_stempel.py` prüft alle Formen einzeln.

## 0.8.0
- **`Beschrifte "Wien".`** — Text an der Stelle des Stifts, in seiner Farbe; `mit 20` setzt die
  Größe (4 bis 400). Eine Karte ohne Ortsnamen ist eine halbe Karte. Im SVG wird daraus ein
  `<text>`, im Browser `fillText`, in Python `stift.write(…)`; eine Beschriftung zählt wie ein
  Strich gegen die Grenze.
- **`programme/22_routenplaner.klar`** — zwölf Orte in Niederösterreich und Wien, neunzehn Straßen,
  der Algorithmus von Dijkstra. Zwei Orte werden ausgewürfelt (nie zwei benachbarte, sonst gäbe es
  nichts zu planen), die kürzeste Verbindung wird gesucht, aufgezählt und in die beschriftete Karte
  gezeichnet. Das Straßennetz liegt als Tabelle vor (`"Krems|Tulln"` → 34), das Gedächtnis des
  Algorithmus in drei weiteren. `tests/test_programme.py` liest das Netz aus der Programmdatei,
  rechnet in Python ein zweites Dijkstra und vergleicht — die kürzeste Strecke ist eine Behauptung,
  die man prüfen kann.
- **`Nimm die Leinwand 600 mal 400.`** — eine feste Zeichenfläche. Ohne sie sucht sich die
  Oberfläche den Ausschnitt selbst und passt ihn an das an, was gerade gezeichnet ist; für ein
  Standbild ist das bequem, für ein bewegtes Bild springt dadurch alles, sobald in einem Durchlauf
  etwas fehlt. Mit ihr liegt der Rahmen fest (−Breite/2 bis +Breite/2), die Fläche behält das
  angegebene Seitenverhältnis und darf deutlich höher werden als der flache Streifen von früher.
  Sie überlebt `Lösche die Zeichnung.` — sie ist keine Zeichnung, sondern der Rahmen. Maße von 20
  bis 4000, in `--bild bild.svg` wird daraus der viewBox, in Python `turtle.setup(…)`.
- **`Gehe 1 Schritt vor.`** — der Singular ist erlaubt. Nur an dieser einen Stelle: „Schritt" bleibt
  ein gewöhnlicher Name, in `14_wellen.klar` heißt eine Variable so.
- **`programme/21_spiel_des_lebens.klar`** — Conways Spiel des Lebens, 22 mal 16 Zellen, dreißig
  Generationen als bewegtes Bild. Das Gitter liegt flach in einer Liste, ringsum ein toter Rand,
  damit das Nachbarzählen ohne Kantenabfragen auskommt; jede Generation entsteht als neue Liste.
  Auf der Startseite gibt es dafür einen eigenen Abschnitt („Die Sprache ist einfach. Die Programme
  müssen es nicht sein.") samt Demo, die hier in der Seite läuft. `tests/test_programme.py` rechnet
  die Regeln am echten Programm nach: Blinker kippt, Block bleibt, Gleiter wandert.
- **Abschnitt „Wo Klarsatz steht"** auf der Startseite (`#einordnung`): eine Vergleichstabelle mit
  Logo, Niki, Robot Karol, Scratch, Guido van Robot, Python und Klarsatz, danach vier Karten zu der
  Frage, **welche Einstiegshürde ein Ansatz jeweils wegnimmt** — Blöcke statt Syntax, kleine Welt,
  vollständige Sprache, vertraute Sprachform. Dazu eine schematische Karte als Inline-SVG
  (waagrecht visuell ↔ textbasiert, senkrecht geführte Lernwelt ↔ allgemeine Programmierwelt), auf
  schmalen Bildschirmen durch eine Liste ersetzt, damit keine Beschriftung unlesbar klein wird.
  Der Abschnitt wertet nicht: Klarsatz wird als Ansatz gezeigt, die Annahme dahinter ausdrücklich
  als Annahme benannt, und die Angaben zu den anderen Projekten sind belegt und verlinkt.
  `tests/test_einordnung.py` prüft das mit — samt einer Liste von Sätzen, die dort nicht stehen dürfen.
- **Einordnung geschärft** — an den Stellen, an denen die Erwartung entsteht (Seitenkopf, README,
  Sprachreferenz, Lektion 1):
  * *Klarsatz ist keine natürliche Sprache*, sondern eine Programmiersprache, deren Syntax sich an
    deutscher Alltagssprache orientiert. Der Parser versteht nicht, was man meint — er erkennt,
    welchem festen Satzmuster ein Satz entspricht. Das Tutorial zeigt die Grenze an einem echten
    Beispiel: `Zeige mir bitte "Hallo".` läuft, `Sag Hallo.` nicht.
  * *Und sie will keine Zielsprache sein.* Treffender als „neue Programmiersprache" ist:
    eine **didaktische Notation für das Erlernen von Programmierdenken**. Der Ausgang zu Python
    ist kein Nebenfeature, sondern vorgesehen.
- **`Frage "…" als Zahl` und `als Text`**: Man kann jetzt ausdrücklich sagen, was man erwartet.
  `als Zahl` bricht mit einer deutschen Meldung ab, wenn etwas anderes kommt — und die Meldung
  sagt gleich, wie man stattdessen so lange fragt, bis es passt. `als Text` verhindert die
  Umwandlung, damit eine Postleitzahl `"3100"` bleibt. Ohne Angabe ändert sich **nichts**.
  Die Typangabe steht vor `und merke`; dadurch bleiben `Zahl` und `Text` weiterhin erlaubte
  Variablennamen (`… und merke die Antwort als Zahl.` tut, was es immer tat). Das Tutorial zeigt
  jetzt die ausdrückliche Form zuerst — „Daten haben einen Typ" ist ein Konzept, keine Formalie.
- **Grafikkurs** (`docs/TUTORIAL-ZEICHNEN.md`, `tutorial-zeichnen.html`): acht Lektionen vom
  ersten Strich über Vielecke, Farben, Muster und Zufall bis zum bewegten Bild. **Auch die
  Zeichnungen werden nachgerechnet** — ein ```zeichnung-Block kündigt Strichzahl, Farben und
  geschlossene Figuren an, der Test prüft es am gemeldeten Strichverlauf nach. Dabei kamen zwei
  falsche Behauptungen des Kurses ans Licht: `Gehe zur Mitte` malt **nicht** mit.
- **Der Weg vom Kurs in die Spielwiese.** Über jedem Beispiel steht jetzt „Im Spielplatz öffnen",
  und das Programm landet mit einem Klick im Editor; für die Übungsaufgaben gibt es einen Link
  auf ein leeres Blatt. Vorher sagte das Tutorial „probier das aus", ohne zu verraten, wo.
- **Tutorial neu gebaut — vom Sprachkurs zum Programmierkurs.** Jede Lektion beginnt jetzt mit
  einem Problem statt mit einem Befehl, und jede folgt dem Muster *vorhersagen → ausprobieren →
  verändern*. Neu: eine eigene Lektion **„Fehler sind normal"** mit absichtlich kaputten
  Programmen (auch deren Meldungen werden nachgerechnet), das erste Spiel schon in der Mitte
  statt am Ende, Funktionen direkt danach mit echtem Anlass, Kurzformen erst nach den
  Grundformen, Dinge und Tabellen als Kür, eine Kür übers Zeichnen, ein **Abschlussprojekt ohne
  Musterlösung** und als Schluss **„Dasselbe in Python"** mit Zeile-für-Zeile-Gegenüberstellung.
- **Zielgruppen** in README und auf der Webseite: elf Gruppen mit einer ehrlichen Einschätzung
  von 1 bis 10 — auch die, für die Klarsatz nichts bringt. Ein Test hält beide Fassungen gleich.
- **Behoben:** `tools/baue_tutorial.py` lief in eine Endlosschleife, sobald eine Zeile nur aus
  `>` bestand — das blockierte das Veröffentlichen, ohne einen Fehler zu melden. Jetzt gibt es
  ein Sicherheitsnetz und einen Test mit zwölf sperrigen Zeilen.
- **Behoben:** Die Lernstufen sperrten `Versuche` auch dort, wo es ein Variablenname ist.
  Satzanfangswörter zählen jetzt nur noch am Satzanfang.
- **Lernstufen** (`--stufe N`, `--stufen`, Auswahl in der Spielwiese): sieben Stufen entlang der
  Lektionen des Tutorials. Wer zu früh nach einem Wort greift, liest „Das kommt später: 'Wenn'
  lernst du in Stufe 3 (Entscheiden)". Gesperrt wird nur, was eindeutig ist — eine Variable darf
  weiterhin `Wurzel` heißen. Ein geladenes Beispiel setzt die Stufe zurück.
- **Behoben:** Das Textadventure und das Grafikadventure stürzten ab, wenn man eine **Zahl**
  eintippte (`Kleinbuchstaben von 5`). Jetzt wird die Eingabe erst zu Text gemacht.
- **Behoben:** Der Browser-Test tippte Antworten in ein bereits abgelöstes Eingabefeld und verlor
  sie dabei. Er wartet jetzt, bis das benutzte Feld verschwunden ist.
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
