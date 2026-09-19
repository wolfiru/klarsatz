// Tokenisiert Klarsatz-Dateien mit dem JavaScript-Hervorhebungscode der Spielwiese (Ausgabe: JSON).
// Aufruf:  node tools/tokenisiere_js.mjs datei.klar [weitere …]
import fs from "node:fs";
import { kompiliere, tokenisiere } from "../playground/klarsatz-hervorhebung.js";

const regelDatei = JSON.parse(fs.readFileSync(new URL("../editor/hervorhebung.json", import.meta.url), "utf8"));
const regeln = kompiliere(regelDatei);
const ergebnis = {};
for (const datei of process.argv.slice(2)) {
  ergebnis[datei] = tokenisiere(fs.readFileSync(datei, "utf8"), regeln);
}
process.stdout.write(JSON.stringify(ergebnis));
