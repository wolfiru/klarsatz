# Klarsatz für Visual Studio Code

Hervorhebung, automatisches Einrücken und Snippets für `.klar`-Dateien.

## Installieren (ohne Marktplatz)

Den ganzen Ordner `vscode-klarsatz` in das Erweiterungsverzeichnis kopieren und VS Code neu starten:

* Linux / macOS: `~/.vscode/extensions/klarsatz-0.2.0/`
* Windows: `%USERPROFILE%\.vscode\extensions\klarsatz-0.2.0\`

Oder als `.vsix` verpacken: `npx @vscode/vsce package` im Ordner, dann in VS Code
„Aus VSIX installieren …“.

## Was du bekommst

* Farben für Satzanfänge (`Zeige`, `Merke` …), Steuerwörter (`Wenn`, `Ende`, `Wiederhole` …), Bindewörter
  (`und`, `plus`, `größer als` …), eingebaute Funktionen, Texte, Zahlen und Kommentare.
* Einrücken nach jedem `:` und Ausrücken bei `Ende.`, `Sonst`, `Bei Fehler`.
* Kommentar umschalten mit Strg+# (fügt `Anmerkung:` ein).
* Snippets: `wenn`, `wennsonst`, `wiederhole`, `solange`, `zaehle`, `fuer`, `aufgabe`, `versuche`, `ding`, `liste`,
  `tabelle`, `programm` … – Tab drücken zum Ausfüllen.

Tipp: `python3 -m klarsatz --formatiere --ersetzen datei.klar` rückt ein Programm komplett neu ein, und
`python3 -m klarsatz --pruefe datei.klar` findet Tippfehler, ohne das Programm auszuführen.

Die Dateien in diesem Ordner werden mit `python3 tools/baue_editor.py` aus dem Parser erzeugt –
bitte nicht von Hand ändern.
