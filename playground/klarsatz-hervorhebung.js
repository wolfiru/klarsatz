// Syntax-Hervorhebung für Klarsatz – ohne DOM, damit sie auch in Node und in Tests läuft.
// Die Regeln kommen aus hervorhebung.json (erzeugt aus dem Parser, siehe tools/baue_editor.py).

/** Regeln aus der JSON-Datei in reguläre Ausdrücke übersetzen. */
export function kompiliere(regelDatei) {
  return regelDatei.regeln.map((r) => ({ re: new RegExp(r.regex, "imuy"), bereiche: r.bereiche }));
}

const istWortzeichen = (c) => c !== undefined && /[\p{L}\p{N}_]/u.test(c);

/**
 * Zerlegt Text in [Text, Name]-Paare. Name ist null für Text ohne Hervorhebung, sonst z. B. "steuerung".
 * Fügt man alle Texte wieder zusammen, entsteht genau der Eingabetext.
 */
export function tokenisiere(text, regeln) {
  const tokens = [];
  const schlicht = (t) => {
    if (!t) return;
    const letzter = tokens[tokens.length - 1];
    if (letzter && letzter[1] === null) letzter[0] += t;
    else tokens.push([t, null]);
  };
  let pos = 0;
  while (pos < text.length) {
    const c = text[pos];
    const mittenImWort = istWortzeichen(c) && istWortzeichen(text[pos - 1]);
    let treffer = null;
    if (!mittenImWort) {
      for (const r of regeln) {
        r.re.lastIndex = pos;
        const m = r.re.exec(text);
        if (m && m[0].length) {
          treffer = [r, m];
          break;
        }
      }
    }
    if (treffer) {
      const [r, m] = treffer;
      if (typeof r.bereiche === "string") {
        tokens.push([m[0], r.bereiche]);
      } else {
        const teile = r.bereiche.map((b, i) => [m[i + 1] ?? "", b]);
        if (teile.map((t) => t[0]).join("") === m[0]) {
          for (const [t, b] of teile) if (t) (b ? tokens.push([t, b]) : schlicht(t));
        } else {
          schlicht(m[0]);
        }
      }
      pos += m[0].length;
    } else if (istWortzeichen(c)) {
      let ende = pos;
      while (ende < text.length && istWortzeichen(text[ende])) ende++;
      schlicht(text.slice(pos, ende));
      pos = ende;
    } else {
      schlicht(c);
      pos++;
    }
  }
  return tokens;
}

/** Tokens in Zeilen aufteilen: [[ [Text, Name], … ], …] – nützlich, um einzelne Zeilen zu markieren. */
export function inZeilen(tokens) {
  const zeilen = [[]];
  for (const [text, name] of tokens) {
    const teile = text.split("\n");
    teile.forEach((t, i) => {
      if (i > 0) zeilen.push([]);
      if (t) zeilen[zeilen.length - 1].push([t, name]);
    });
  }
  return zeilen;
}

export function alsHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
