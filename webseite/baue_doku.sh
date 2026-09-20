#!/bin/bash
# Baut die Doku-Seiten der Klarsatz-Webseite.
#
# Die sechs Kapitel liegen als HTML-Abschnitte in kapitel/ und werden hier in eine
# gemeinsame Hülle gesetzt (Navigation, Seitenleiste mit Kapitelliste und den
# Sprungmarken der Seite, Blättern, Fußzeile). Dadurch bleiben diese Teile über alle
# Kapitel gleich, obwohl das Ergebnis ganz normale statische HTML-Dateien sind.
#
#   bash webseite/baue_doku.sh
#   python3 tools/pruefe_webseite.py        # danach: laufen alle Beispiele noch?
#
# Wer nur Text ändert, kann auch direkt die erzeugten Dateien bearbeiten — dann aber
# die Änderung nach kapitel/ zurückschreiben, sonst überschreibt der nächste Lauf sie.
set -eu
# Zielordner als erstes Argument, sonst der Webordner. So kann man die Seiten
# auch versuchsweise woandershin bauen, ohne die veröffentlichte Seite anzufassen.
ZIEL=${1:-/var/www/html/klarsatz}
FRAG="$(dirname "$0")/kapitel"

# Kapitel: id|datei|Nummer|Titel|Untertitel(meta description)
KAPITEL=(
"grundlagen|doku-grundlagen.html|01|Grundlagen|Sätze, Werte und Variablen: die Grundregeln der Sprache Klarsatz."
"rechnen|doku-rechnen.html|02|Rechnen und Vergleichen|Rechenarten, Umwandlungen, Vergleiche und logische Verknüpfungen in Klarsatz."
"ablauf|doku-ablauf.html|03|Entscheiden und Wiederholen|Bedingungen in Block- und Kurzform sowie alle Schleifenarten von Klarsatz."
"zeichnen|doku-zeichnen.html|04|Zeichnen|Mit Gehe, Drehe und dem Stift Figuren malen — Quadrate, Vielecke, Spiralen, Farben."
"listen|doku-listen.html|05|Listen, Tabellen und Dinge|Listen und Tabellen anlegen und durchgehen, Texte zerlegen und verbinden, eigene Strukturen mit Feldern."
"aufgaben|doku-aufgaben.html|06|Aufgaben und Fehler|Eigene Aufgaben definieren, Rückgabewerte, Rekursion, Fehlerbehandlung und Dateien."
"referenz|doku-referenz.html|07|Referenz|Reservierte Wörter, Aufruf des Interpreters, Sicherheitsvorkehrungen und bekannte Grenzen."
)

nav_links() {
  local aktiv="$1" eintrag id datei nr titel
  for eintrag in "${KAPITEL[@]}"; do
    IFS='|' read -r id datei nr titel _ <<< "$eintrag"
    if [ "$id" = "$aktiv" ]; then
      printf '            <li><a href="%s" class="aktiv">%s &nbsp;%s</a></li>\n' "$datei" "$nr" "$titel"
    else
      printf '            <li><a href="%s">%s &nbsp;%s</a></li>\n' "$datei" "$nr" "$titel"
    fi
  done
}

# Sammelt die <h2 id="..."> der Inhaltsdatei für "Auf dieser Seite".
anker() {
  sed -n 's@.*<h2 id="\([^"]*\)">\(.*\)</h2>.*@            <li><a href="#\1">\2</a></li>@p' "$1" \
    | sed 's@<em>@@g; s@</em>@@g'
}

i=0
for eintrag in "${KAPITEL[@]}"; do
  IFS='|' read -r id datei nr titel beschr <<< "$eintrag"
  inhalt="$FRAG/$id.html"
  [ -f "$inhalt" ] || { echo "fehlt: $inhalt" >&2; continue; }

  # Blättern: vorheriges / nächstes Kapitel
  zurueck_html=""
  weiter_html=""
  if [ "$i" -gt 0 ]; then
    IFS='|' read -r _ pdatei pnr ptitel _ <<< "${KAPITEL[$((i-1))]}"
    zurueck_html=$(printf '    <a href="%s"><span class="bl-label">Zurück</span>%s &nbsp;%s</a>\n' "$pdatei" "$pnr" "$ptitel")
  else
    zurueck_html='    <a href="doku.html"><span class="bl-label">Zurück</span>Übersicht</a>'
  fi
  if [ "$i" -lt $(( ${#KAPITEL[@]} - 1 )) ]; then
    IFS='|' read -r _ ndatei nnr ntitel _ <<< "${KAPITEL[$((i+1))]}"
    weiter_html=$(printf '    <a class="bl-weiter" href="%s"><span class="bl-label">Weiter</span>%s &nbsp;%s</a>\n' "$ndatei" "$nnr" "$ntitel")
  else
    weiter_html='    <a class="bl-weiter" href="spielplatz.html"><span class="bl-label">Weiter</span>Spielplatz</a>'
  fi

  {
  cat <<HEAD
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="$beschr">
<meta name="theme-color" content="#0c0e0b">
<title>$titel — Klarsatz-Dokumentation</title>
<meta property="og:type" content="article">
<meta property="og:title" content="$titel — Klarsatz">
<meta property="og:description" content="$beschr">
<meta property="og:url" content="https://www.ruthner.at/klarsatz/$datei">
<meta property="og:image" content="https://www.ruthner.at/klarsatz/assets/klarsatz-vorschau.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://www.ruthner.at/klarsatz/$datei">
<link rel="icon" href="assets/klarsatz-signet-klein.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="stylesheet" href="assets/style.css?v=2">
</head>
<body>
<a class="zum-inhalt" href="#inhalt">Zum Inhalt springen</a>

<canvas id="manuskript" aria-hidden="true"></canvas>
<div class="bg-overlay" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>

<nav class="nav" aria-label="Hauptnavigation">
    <div class="nav-start">
        <a class="heim" href="/" aria-label="Zur Startseite von ruthner.at">
            <img src="assets/monogram.png" alt="" width="51" height="64" decoding="async" loading="lazy">
            <span>ruthner<em>.at</em></span>
        </a>
        <span class="nav-teiler" aria-hidden="true"></span>
        <a class="brand" href="index.html"><span class="brand-mark"></span><span>Klar<em>satz</em></span></a>
    </div>
    <div class="nav-links">
        <a href="index.html">Sprache</a>
        <a href="tutorial.html">Tutorial</a>
        <a href="doku.html">Dokumentation</a>
        <a href="doku-referenz.html">Referenz</a>
        <a href="spielplatz.html" class="nav-cta">Spielplatz</a>
    </div>
</nav>

<header class="seitenkopf">
    <p class="kicker">Dokumentation · Kapitel $nr</p>
    <h1>$titel</h1>
</header>

<main id="inhalt">
<noscript>
<div class="notiz warnung" style="margin:20px auto;max-width:760px">
<span class="notiz-titel">JavaScript ist abgeschaltet</span>
<p>Die Dokumentation lässt sich vollständig lesen. Nur <em>Hier ausführen</em> und die Einfärbung
der Beispiele brauchen JavaScript.</p>
</div>
</noscript>
<div class="doku-layout">

    <aside class="doku-seitenleiste">
        <span class="sl-titel">Kapitel</span>
        <ol>
HEAD
  nav_links "$id"
  cat <<'MITTE'
        </ol>
        <span class="sl-titel">Auf dieser Seite</span>
        <ol>
MITTE
  anker "$inhalt"
  cat <<'MITTE2'
        </ol>
    </aside>

    <article class="doku-inhalt">
MITTE2
  cat "$inhalt"
  cat <<FUSS

<nav class="blaettern">
$zurueck_html
$weiter_html
</nav>

    </article>

</div>
</main>

<footer>
    <div class="foot-inner">
        <span>© <span id="jahr"></span> ruthner.at · Klarsatz <span data-download="version">0.10.1</span></span>
        <span><a href="/">ruthner.at</a> &nbsp;·&nbsp; <a href="index.html">Sprache</a> &nbsp;·&nbsp; <a href="tutorial.html">Tutorial</a> &nbsp;·&nbsp; <a href="doku.html">Dokumentation</a> &nbsp;·&nbsp; <a href="spielplatz.html">Spielplatz</a> &nbsp;·&nbsp; <a href="https://github.com/wolfiru/klarsatz" rel="noopener">GitHub</a> &nbsp;·&nbsp; <a href="mailto:wolfgang@ruthner.at">wolfgang@ruthner.at</a> &nbsp;·&nbsp; <a href="/impressum.html">Impressum</a> &nbsp;·&nbsp; <a href="/impressum.html#datenschutz">Datenschutz</a> &nbsp;·&nbsp; <a href="https://github.com/wolfiru/klarsatz/blob/main/LICENSE" rel="noopener">MIT-Lizenz</a></span>
    </div>
</footer>

<script src="assets/manuskript-bg.js?v=2"></script>
<script src="assets/app.js?v=2"></script>
<script type="module" src="assets/code-hervorhebung.js?v=2"></script>
<script type="module" src="assets/kurs.js?v=2"></script>
</body>
</html>
FUSS
  } > "$ZIEL/$datei"
  echo "gebaut: $datei ($(wc -c < "$ZIEL/$datei") Bytes)"
  i=$((i+1))
done

# Versionsstempel auffrischen, damit Browser geänderte CSS/JS sofort neu holen.
python3 "$(dirname "$0")/../tools/stempel_webseite.py" "$ZIEL"
