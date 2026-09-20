// Klarsatz-Spielwiese: Editor mit Hervorhebung, Ausführen, Prüfen, Formatieren – alles im Browser.
//
//   <link rel="stylesheet" href="klarsatz-playground.css">
//   <div id="spielwiese"></div>
//   <script type="module">
//     import { erstelle } from "./klarsatz-playground.js";
//     erstelle(document.getElementById("spielwiese"), { beispiel: "hallo" });
//   </script>
//
// Optionen: beispiel (Kennung des Startprogramms), code (eigener Startcode), basis (Ordner mit den Dateien),
//           zeitlimitMs (nach so vielen Millisekunden wird ein hängender Lauf abgebrochen),
//           pyodideUrl (Ordner mit der Pyodide-Laufzeit; ohne Angabe wird das CDN jsdelivr benutzt).
import { alsHtml, inZeilen, kompiliere, tokenisiere } from "./klarsatz-hervorhebung.js";

class ZeitFehler extends Error {}

class PythonWorker {
  constructor(workerUrl, zipUrl, zeitlimitMs) {
    this.workerUrl = workerUrl;
    this.zipUrl = zipUrl;
    this.zeitlimitMs = zeitlimitMs;
    this.neuStarten();
  }

  neuStarten() {
    // Wächter der alten Aufträge abstellen: Sonst beendet ein Zeitlimit von vorhin
    // später den frisch gestarteten Worker — mitten im Laden von Python.
    if (this.offen) {
      for (const auftrag of this.offen.values()) clearTimeout(auftrag.timer);
    }
    if (this.worker) this.worker.terminate();
    this.worker = new Worker(this.workerUrl);
    this.naechsteId = 1;
    this.offen = new Map();
    this.worker.onmessage = (e) => {
      const { id, ok, ergebnis, fehler, teil } = e.data;
      const a = this.offen.get(id);
      if (!a) return;
      if (teil !== undefined) {
        // Lebenszeichen: Das Zeitlimit zählt ab jetzt wieder von vorn. Ein Programm,
        // das laufend etwas meldet, gilt nicht als hängend — auch wenn es wartet.
        a.frisch();
        if (this.beiTeil) this.beiTeil(teil);
        return;
      }
      this.offen.delete(id);
      clearTimeout(a.timer);
      ok ? a.res(ergebnis) : a.rej(new Error(fehler));
    };
    this.bereit = this._senden("start", { zipUrl: this.zipUrl }, 120000);
    this.bereit.catch(() => {});
  }

  _senden(art, args, limit) {
    return new Promise((res, rej) => {
      const id = this.naechsteId++;
      const auftrag = { res, rej, timer: null };
      const stellen = () => setTimeout(() => {
        this.offen.delete(id);
        this.worker.terminate();
        rej(new ZeitFehler("Zeitlimit"));
      }, limit);
      auftrag.frisch = () => {
        clearTimeout(auftrag.timer);
        auftrag.timer = stellen();
      };
      auftrag.timer = stellen();
      this.offen.set(id, auftrag);
      this.worker.postMessage({ id, art, args });
    });
  }

  async aufruf(art, args) {
    await this.bereit;
    try {
      return await this._senden(art, args, this.zeitlimitMs);
    } catch (e) {
      if (e instanceof ZeitFehler) this.neuStarten();
      throw e;
    }
  }

  beenden() {
    this.worker.terminate();
  }
}

const holeJson = async (url) => {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
};

const HTML = `
<div class="kp">
  <div class="kp-leiste">
    <label class="kp-beispiel">Beispiel <select class="kp-auswahl" aria-label="Beispielprogramm wählen"></select></label>
    <button type="button" class="kp-knopf kp-neu" title="Leeres Blatt – selbst programmieren">✎ Neu</button>
    <label class="kp-stufe" title="Nur für eigene Programme: höhere Sätze werden gesperrt. Ein geladenes Beispiel setzt die Stufe zurück.">Stufe <select class="kp-stufenwahl" aria-label="Lernstufe wählen">
      <option value="">alle</option>
      <option value="1">1 · Zeigen, fragen, merken</option>
      <option value="2">2 · Rechnen</option>
      <option value="3">3 · Entscheiden</option>
      <option value="4">4 · Wiederholen</option>
      <option value="5">5 · Eigene Bausteine</option>
      <option value="6">6 · Listen und Tabellen</option>
    </select></label>
    <button type="button" class="kp-knopf kp-lauf" disabled title="Strg+Enter">▶ Ausführen</button>
    <button type="button" class="kp-knopf kp-pruefen" disabled>Prüfen</button>
    <button type="button" class="kp-knopf kp-format" disabled>Formatieren</button>
    <button type="button" class="kp-knopf kp-python" disabled title="Dasselbe Programm in Python">Als Python</button>
    <span class="kp-status" role="status" aria-live="polite">Klarsatz wird geladen …</span>
  </div>
  <div class="kp-haelften">
    <div class="kp-editor">
      <pre class="kp-nummern" aria-hidden="true"></pre>
      <div class="kp-eingabebereich">
        <pre class="kp-hervor" aria-hidden="true"></pre>
        <textarea class="kp-text" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off"
                  wrap="off" aria-label="Klarsatz-Programm"></textarea>
      </div>
    </div>
    <div class="kp-rechts">
      <canvas class="kp-leinwand" aria-label="Zeichnung des Programms" hidden></canvas>
      <div class="kp-ausgabe" role="log" aria-live="polite" aria-label="Ausgabe des Programms"></div>
      <ul class="kp-befunde" aria-label="Ergebnis der Prüfung"></ul>
    </div>
  </div>
</div>`;

export async function erstelle(wurzel, opt = {}) {
  const basis = opt.basis ?? new URL(".", import.meta.url).href;
  // Wird dieses Modul mit "?v=…" geladen, bekommen seine Dateien denselben Stempel.
  // So holt ein Browser nach einer Änderung auch beispiele.json und klarsatz-py.zip neu,
  // statt eine alte Fassung aus dem Zwischenspeicher zu nehmen.
  const stempel = new URL(import.meta.url).search;
  wurzel.innerHTML = HTML;
  const q = (s) => wurzel.querySelector(s);
  const [auswahl, ta, hervor, nummern, ausgabe, befundeListe, status] =
    [".kp-auswahl", ".kp-text", ".kp-hervor", ".kp-nummern", ".kp-ausgabe", ".kp-befunde", ".kp-status"].map(q);
  const knopfLauf = q(".kp-lauf"), knopfPruefen = q(".kp-pruefen"), knopfFormat = q(".kp-format");
  const knopfPython = q(".kp-python"), knopfNeu = q(".kp-neu");
  const leinwand = q(".kp-leinwand");

  const [beispiele, regelDatei] = await Promise.all([holeJson(basis + "beispiele.json" + stempel),
                                                    holeJson(basis + "hervorhebung.json" + stempel)]);
  const regeln = kompiliere(regelDatei);
  const teile = new URLSearchParams(stempel);
  if (opt.pyodideUrl) teile.set("pyodide", opt.pyodideUrl);
  const workerUrl = basis + "klarsatz-worker.js" + (teile.toString() ? "?" + teile : "");
  const python = new PythonWorker(workerUrl, basis + "klarsatz-py.zip" + stempel, opt.zeitlimitMs ?? 15000);

  const setzeStatus = (text, art = "") => {
    status.textContent = text;
    status.className = "kp-status" + (art ? " kp-status-" + art : "");
  };

  // ── Editor ────────────────────────────────────────────────────────
  let marken = new Map();            // Zeile -> "fehler" | "warnung" | "hinweis"
  const rangfolge = { fehler: 3, warnung: 2, hinweis: 1 };

  function zeichne() {
    const zeilen = inZeilen(tokenisiere(ta.value, regeln));
    hervor.innerHTML = zeilen.map((z, i) => {
      const marke = marken.get(i + 1);
      const inhalt = z.map(([t, n]) => (n ? `<span class="kp-t-${n}">${alsHtml(t)}</span>` : alsHtml(t))).join("");
      return `<span class="kp-zeile${marke ? " kp-marke-" + marke : ""}">${inhalt}</span>`;
    }).join("\n") + "\n ";
    nummern.textContent = zeilen.map((_, i) => i + 1).join("\n") + "\n ";
    gleicheScrollAn();
  }

  function gleicheScrollAn() {
    hervor.scrollTop = ta.scrollTop;
    hervor.scrollLeft = ta.scrollLeft;
    nummern.scrollTop = ta.scrollTop;
  }

  function fuegeEin(text) {
    ta.focus();
    if (!document.execCommand("insertText", false, text)) ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, "end");
    zeichne();
  }

  function markiere(zeile, art) {
    if (!zeile) return;
    if ((rangfolge[marken.get(zeile)] ?? 0) < rangfolge[art]) marken.set(zeile, art);
  }

  function springeZu(zeile) {
    const zeilen = ta.value.split("\n");
    let pos = 0;
    for (let i = 0; i < zeile - 1 && i < zeilen.length; i++) pos += zeilen[i].length + 1;
    ta.focus();
    ta.setSelectionRange(pos, pos + (zeilen[zeile - 1]?.length ?? 0));
    const hoehe = parseFloat(getComputedStyle(ta).lineHeight) || 20;
    ta.scrollTop = Math.max(0, (zeile - 3) * hoehe);
    gleicheScrollAn();
  }

  ta.addEventListener("input", () => { marken = new Map(); zeichne(); });
  ta.addEventListener("scroll", gleicheScrollAn);
  ta.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      starte();
    } else if (e.key === "Tab" && !e.shiftKey) {
      e.preventDefault();
      fuegeEin("    ");
    } else if (e.key === "Enter" && !e.shiftKey && !e.altKey) {
      e.preventDefault();
      const davor = ta.value.slice(0, ta.selectionStart);
      const zeile = davor.slice(davor.lastIndexOf("\n") + 1);
      const einzug = zeile.match(/^ */)[0];
      fuegeEin("\n" + einzug + (/:\s*$/.test(zeile) ? "    " : ""));
    }
  });

  function setzeCode(text) {
    ta.value = text;
    marken = new Map();
    zeichne();
  }

  // ── Ausführen ─────────────────────────────────────────────────────
  let antworten = [];
  let seed = 0;
  let laufNummer = 0;

  const el = (tag, klasse, text) => {
    const e = document.createElement(tag);
    if (klasse) e.className = klasse;
    if (text !== undefined) e.textContent = text;
    return e;
  };

  // Malt die Striche eines Laufs. Der Interpreter liefert sie in einem
  // Koordinatensystem mit Ursprung in der Mitte und y nach oben; hier wird
  // gespiegelt und so skaliert, dass die ganze Zeichnung hineinpasst.
  function maleBild(striche, gewuenscht) {
    const rahmen = wurzel.querySelector(".kp");
    if (!striche.length && !gewuenscht) {
      leinwand.hidden = true;
      rahmen.classList.remove("kp-mit-bild");
      return;
    }
    leinwand.hidden = false;
    rahmen.classList.add("kp-mit-bild");     // macht Platz: die Fläche wächst, siehe CSS

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const breite = leinwand.clientWidth || 400;
    // Ohne Angabe bleibt es beim flachen Streifen von früher. Wer "Nimm die Leinwand
    // 600 mal 400." sagt, bekommt das Seitenverhältnis und darf deutlich höher werden.
    const hoehe = gewuenscht
      ? Math.round(Math.min(620, Math.max(180, breite * (gewuenscht[2] / gewuenscht[1]))))
      : Math.round(Math.min(260, Math.max(180, breite * 0.55)));
    leinwand.width = Math.round(breite * dpr);
    leinwand.height = Math.round(hoehe * dpr);
    leinwand.style.height = hoehe + "px";

    const ctx = leinwand.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, breite, hoehe);

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, dickste = 1;
    for (const [, x1, y1, x2, y2, , dicke] of striche) {
      minX = Math.min(minX, x1, x2); maxX = Math.max(maxX, x1, x2);
      minY = Math.min(minY, y1, y2); maxY = Math.max(maxY, y1, y2);
      dickste = Math.max(dickste, dicke);
    }

    let faktor, versatzX, versatzY;
    if (gewuenscht) {
      // Fester Rahmen: -Breite/2 bis +Breite/2. Entscheidend für bewegte Bilder — der
      // automatische Ausschnitt richtet sich nach dem, was gerade da ist, und lässt
      // alles springen, sobald in einem Durchlauf etwas fehlt.
      faktor = Math.min(breite / gewuenscht[1], hoehe / gewuenscht[2]);
      versatzX = breite / 2;
      versatzY = hoehe / 2;
    } else {
      const rand = 12 + dickste;
      faktor = Math.min((breite - 2 * rand) / Math.max(maxX - minX, 1),
                        (hoehe - 2 * rand) / Math.max(maxY - minY, 1), 4);
      versatzX = (breite - (maxX - minX) * faktor) / 2 - minX * faktor;
      versatzY = (hoehe - (maxY - minY) * faktor) / 2 + maxY * faktor;
    }

    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    for (const [, x1, y1, x2, y2, farbe, dicke] of striche) {
      ctx.beginPath();
      ctx.strokeStyle = farbe;
      ctx.lineWidth = Math.max(dicke * faktor, 1);
      ctx.moveTo(x1 * faktor + versatzX, versatzY - y1 * faktor);
      ctx.lineTo(x2 * faktor + versatzX, versatzY - y2 * faktor);
      ctx.stroke();
    }
  }

  // Takt: Ein Programm kann darum bitten, regelmäßig neu zu laufen ("Wiederhole dieses
  // Programm jede Sekunde."). Jeder Lauf zeichnet ein frisches Bild — so tickt eine Uhr,
  // ohne dass der Interpreter mitten im Programm warten müsste.
  let taktTimer = null;

  function taktStoppen() {
    if (taktTimer) {
      clearTimeout(taktTimer);
      taktTimer = null;
    }
    knopfLauf.textContent = "▶ Ausführen";
  }

  let letzteStriche = [];
  let letzteLeinwand = null;       // ("leinwand", Breite, Höhe), falls das Programm eine will
  let laeuft = false;              // ein Programm ist gerade im Worker unterwegs
  let malGeplant = false;

  function planeMalen() {
    if (malGeplant) return;
    malGeplant = true;
    requestAnimationFrame(() => {
      malGeplant = false;
      maleBild(letzteStriche, letzteLeinwand);
    });
  }

  // Zwischenstände: Der Worker meldet jeden Eintrag, sobald er entsteht. Dadurch sieht
  // man Ausgaben und Striche schon während des Laufs — und ein Programm mit "Warte"
  // muss nicht erst enden, um etwas zu zeigen.
  const beiTeil = (eintrag) => {
    const art = eintrag[0];
    if (art === "aus") {
      ausgabe.append(el("div", "kp-aus", eintrag[1] || " "));
      // Ein endlos laufendes Programm darf die Seite nicht zuschütten: Wir zeigen
      // die jüngsten Zeilen und werfen die ältesten weg.
      while (ausgabe.childElementCount > 4000) ausgabe.firstElementChild.remove();
      ausgabe.scrollTop = ausgabe.scrollHeight;
    } else if (art === "linie") {
      letzteStriche.push(eintrag);
      planeMalen();
    } else if (art === "loeschen") {
      letzteStriche = [];
      planeMalen();
    } else if (art === "leinwand") {
      letzteLeinwand = eintrag;
      planeMalen();
    }
  };
  python.beiTeil = beiTeil;

  addEventListener("resize", () => {
    if (letzteStriche.length || letzteLeinwand) maleBild(letzteStriche, letzteLeinwand);
  });

  function zeigeErgebnis(erg) {
    ausgabe.replaceChildren();
    letzteStriche = [];
    letzteLeinwand = null;
    for (const eintrag of erg.verlauf) {
      if (eintrag[0] === "linie") letzteStriche.push(eintrag);
      else if (eintrag[0] === "loeschen") letzteStriche = [];
      else if (eintrag[0] === "leinwand") letzteLeinwand = eintrag;
    }
    maleBild(letzteStriche, letzteLeinwand);
    let frageZeile = null;
    for (const [art, text] of erg.verlauf) {
      if (art === "aus") {
        ausgabe.append(el("div", "kp-aus", text || " "));
        frageZeile = null;
      } else if (art === "frage") {
        frageZeile = el("div", "kp-frage");
        frageZeile.append(el("span", "kp-prompt", text));
        ausgabe.append(frageZeile);
      } else if (art === "antwort" && frageZeile) {
        frageZeile.append(el("span", "kp-antwort", text));
      }
    }
    if (erg.zustand === "wartet" && frageZeile) {
      const feld = el("input", "kp-antwortfeld");
      feld.type = "text";
      feld.setAttribute("aria-label", erg.frage || "Antwort");
      feld.autocomplete = "off";
      feld.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          antworten.push(feld.value);
          fuehreAus();
        }
      });
      frageZeile.append(feld);
      feld.focus();
      setzeStatus("Das Programm wartet auf deine Eingabe.", "wartet");
    } else if (erg.zustand === "fertig") {
      if (erg.wiederholung) {
        const nummer = laufNummer;
        knopfLauf.textContent = "■ Anhalten";
        setzeStatus(`Läuft weiter — neu alle ${erg.wiederholung} s.`, "ok");
        taktTimer = setTimeout(() => {
          taktTimer = null;
          if (nummer === laufNummer) starte();
        }, erg.wiederholung * 1000);
      } else {
        ausgabe.append(el("div", "kp-ende", "— Programm beendet —"));
        setzeStatus("Fertig.", "ok");
      }
    } else if (erg.zustand === "fehler") {
      ausgabe.append(el("pre", "kp-fehlertext", erg.fehler));
      marken = new Map();
      markiere(erg.fehler_zeile, "fehler");
      zeichne();
      setzeStatus(erg.fehlerart === "limit" ? "Abgebrochen (Limit erreicht)." : "Ein Fehler ist aufgetreten.", "fehler");
    }
    ausgabe.scrollTop = ausgabe.scrollHeight;
  }

  async function fuehreAus() {
    const nr = ++laufNummer;
    laeuft = true;
    knopfLauf.textContent = "■ Anhalten";
    setzeStatus("Läuft …");
    try {
      const stufe = q(".kp-stufenwahl").value || null;
      const erg = await python.aufruf("laufe", { quelltext: ta.value, antworten, seed, stufe });
      laeuft = false;
      if (nr === laufNummer) zeigeErgebnis(erg);
      if (!taktTimer) knopfLauf.textContent = "▶ Ausführen";
    } catch (e) {
      laeuft = false;
      knopfLauf.textContent = "▶ Ausführen";
      if (nr !== laufNummer) return;
      ausgabe.append(el("pre", "kp-fehlertext", e instanceof ZeitFehler
        ? "Das Programm hat zu lange gebraucht und wurde abgebrochen. (Endlosschleife?)"
        : "Interner Fehler: " + e.message));
      setzeStatus("Abgebrochen.", "fehler");
    }
  }

  function starte() {
    antworten = [];
    seed = Math.floor(Math.random() * 2 ** 31);
    befundeListe.replaceChildren();
    ausgabe.replaceChildren();
    marken = new Map();
    zeichne();
    return fuehreAus();
  }

  // ── Nach Python übersetzen ────────────────────────────────────────
  async function nachPython() {
    setzeStatus("Übersetze …");
    const erg = await python.aufruf("nach_python", { quelltext: ta.value });
    ausgabe.replaceChildren();
    befundeListe.replaceChildren();
    if (!erg.ok) {
      ausgabe.append(el("pre", "kp-fehlertext", erg.fehler));
      markiere(erg.zeile, "fehler");
      zeichne();
      setzeStatus("Das ließ sich nicht übersetzen.", "fehler");
      return;
    }
    ausgabe.append(el("div", "kp-aus", "# Dasselbe Programm in Python:"));
    for (const zeile of erg.text.split("\n")) ausgabe.append(el("div", "kp-aus", zeile || " "));
    setzeStatus("Übersetzt. Zum Vergleichen gedacht — nicht jede Feinheit ist gleich.", "ok");
  }

  // ── Prüfen und Formatieren ────────────────────────────────────────
  async function pruefen() {
    setzeStatus("Prüfe …");
    const befunde = await python.aufruf("pruefe", { quelltext: ta.value });
    befundeListe.replaceChildren();
    marken = new Map();
    for (const b of befunde) {
      markiere(b.zeile, b.schwere.toLowerCase());
      const punkt = el("li", "kp-b kp-b-" + b.schwere.toLowerCase());
      const knopf = el("button", "kp-b-knopf", `Zeile ${b.zeile} · ${b.schwere}`);
      knopf.type = "button";
      knopf.addEventListener("click", () => springeZu(b.zeile));
      punkt.append(knopf, el("span", "kp-b-text", " " + b.meldung));
      befundeListe.append(punkt);
    }
    zeichne();
    if (!befunde.length) {
      befundeListe.append(el("li", "kp-b kp-b-ok", "Keine Probleme gefunden."));
      setzeStatus("Prüfung: alles in Ordnung.", "ok");
    } else {
      const f = befunde.filter((b) => b.schwere === "Fehler").length;
      setzeStatus(`Prüfung: ${f} Fehler, ${befunde.length - f} Warnungen/Hinweise.`, f ? "fehler" : "");
    }
  }

  async function formatieren() {
    const r = await python.aufruf("formatiere", { quelltext: ta.value });
    if (r.ok) {
      if (r.text !== ta.value) setzeCode(r.text);
      setzeStatus("Sauber eingerückt.", "ok");
    } else {
      ausgabe.replaceChildren(el("pre", "kp-fehlertext", r.fehler));
      setzeStatus("Formatieren geht erst, wenn alle Texte geschlossen sind.", "fehler");
    }
  }

  // ── Verdrahten ────────────────────────────────────────────────────
  const gruppen = {};
  for (const b of beispiele) {
    const g = gruppen[b.gruppe] ??= Object.assign(document.createElement("optgroup"), { label: b.gruppe });
    g.append(Object.assign(document.createElement("option"), { value: b.id, textContent: b.titel }));
  }
  // Ganz oben ein leeres Blatt zum Selberschreiben.
  const LEER = { id: "", titel: "Leeres Blatt", code: "" };
  auswahl.append(Object.assign(document.createElement("option"),
                               { value: LEER.id, textContent: "✎ " + LEER.titel }),
                 ...Object.values(gruppen));
  const nachId = (id) => (id === "" ? LEER : beispiele.find((b) => b.id === id));
  auswahl.addEventListener("change", () => {
    laufNummer++;
    taktStoppen();
    antworten = [];
    ausgabe.replaceChildren();
    befundeListe.replaceChildren();
    letzteStriche = [];
    maleBild(letzteStriche);
    setzeCode((nachId(auswahl.value) ?? LEER).code);
    // Die Lernstufe gilt fürs eigene Üben. Ein geladenes Beispiel soll man immer
    // ansehen und laufen lassen können — sonst stünde man vor "Das kommt später",
    // ohne etwas falsch gemacht zu haben.
    if (auswahl.value !== "") q(".kp-stufenwahl").value = "";
    setzeStatus(auswahl.value === "" ? "Leeres Blatt – schreib etwas und drücke Strg+Enter." : "Bereit.");
    if (auswahl.value === "") ta.focus();
  });
  function abbrechen() {
    laufNummer++;                          // ein noch kommendes Ergebnis zählt nicht mehr
    taktStoppen();
    if (!laeuft) {
      setzeStatus("Angehalten.");
      return;
    }
    // Ein laufendes Programm lässt sich nur beenden, indem der Hintergrundprozess
    // beendet und neu aufgesetzt wird — das dauert, weil Python neu geladen wird.
    laeuft = false;
    python.neuStarten();
    python.beiTeil = beiTeil;
    ausgabe.append(el("div", "kp-ende", "— abgebrochen —"));
    for (const k of [knopfLauf, knopfPruefen, knopfFormat, knopfPython]) k.disabled = true;
    setzeStatus("Abgebrochen – Klarsatz wird neu geladen …");
    python.bereit.then(() => {
      for (const k of [knopfLauf, knopfPruefen, knopfFormat, knopfPython]) k.disabled = false;
      setzeStatus("Bereit.");
    }).catch(() => setzeStatus("Neustart fehlgeschlagen.", "fehler"));
  }

  knopfLauf.addEventListener("click", () => {
    if (laeuft || taktTimer) abbrechen();
    else starte();
  });
  knopfPruefen.addEventListener("click", () => pruefen().catch((e) => setzeStatus("Fehler: " + e.message, "fehler")));
  knopfFormat.addEventListener("click", () => formatieren().catch((e) => setzeStatus("Fehler: " + e.message, "fehler")));
  knopfNeu.addEventListener("click", () => {
    auswahl.value = "";
    auswahl.dispatchEvent(new Event("change"));
  });
  knopfPython.addEventListener("click", () => nachPython().catch((e) => setzeStatus("Fehler: " + e.message, "fehler")));

  const start = nachId(opt.beispiel) ?? (opt.code !== undefined ? LEER : beispiele[0]);
  auswahl.value = start.id;
  setzeCode(opt.code ?? start.code);

  python.bereit.then(() => {
    for (const k of [knopfLauf, knopfPruefen, knopfFormat, knopfPython]) k.disabled = false;
    setzeStatus("Bereit. Drücke Strg+Enter zum Ausführen.");
    wurzel.dataset.bereit = "ja";
  }).catch((e) => setzeStatus("Klarsatz konnte nicht geladen werden: " + e.message, "fehler"));

  return {
    holeCode: () => ta.value,
    setzeCode,
    starte,
    zerstoere() { laufNummer++; taktStoppen(); python.beenden(); wurzel.replaceChildren(); },
  };
}
