// Tokenisiert Klarsatz-Dateien mit der TextMate-Grammatik – so wie es VS Code tut.
// Aufruf:  node tools/tokenisiere_textmate.js datei.klar [weitere.klar …]   → JSON auf der Standardausgabe
// Einmalig vorher:  cd tools && npm install
const fs = require("fs");
const path = require("path");
const vsctm = require("vscode-textmate");
const oniguruma = require("vscode-oniguruma");

const grammatik = path.join(__dirname, "..", "editor", "vscode-klarsatz", "syntaxes", "klarsatz.tmLanguage.json");
const wasm = fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm")).buffer;
const onigLib = oniguruma.loadWASM(wasm).then(() => ({
  createOnigScanner: (muster) => new oniguruma.OnigScanner(muster),
  createOnigString: (s) => new oniguruma.OnigString(s),
}));
const registry = new vsctm.Registry({
  onigLib,
  loadGrammar: async (scope) => scope === "source.klarsatz"
    ? vsctm.parseRawGrammar(fs.readFileSync(grammatik, "utf8"), grammatik) : null,
});

registry.loadGrammar("source.klarsatz").then((g) => {
  const ergebnis = {};
  for (const datei of process.argv.slice(2)) {
    const text = fs.readFileSync(datei, "utf8");
    let stapel = vsctm.INITIAL;
    const tokens = [];
    for (const zeile of text.split("\n")) {
      const r = g.tokenizeLine(zeile, stapel);
      for (const t of r.tokens) tokens.push([zeile.substring(t.startIndex, t.endIndex), t.scopes[t.scopes.length - 1]]);
      stapel = r.ruleStack;
    }
    ergebnis[datei] = tokens;
  }
  process.stdout.write(JSON.stringify(ergebnis));
});
