// Web-Worker: lädt Pyodide (Python im Browser) und das Klarsatz-Paket und führt Programme abseits der Oberfläche aus.
// So bleibt die Seite bedienbar, und eine Endlosschleife lässt sich durch Neustart des Workers beenden.
// Woher Pyodide geladen wird: "?pyodide=…" an der Worker-Adresse gewinnt, sonst das CDN.
// So kann eine Webseite die Laufzeit selbst ausliefern (Datenschutz, keine Abhängigkeit von fremden Diensten).
const PYODIDE = new URL(self.location.href).searchParams.get("pyodide")
  || "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
importScripts(PYODIDE + "pyodide.js");

let web = null;

async function start(zipUrl) {
  const pyodide = await loadPyodide({ indexURL: PYODIDE });
  const paket = await (await fetch(zipUrl)).arrayBuffer();
  pyodide.unpackArchive(paket, "zip", { extractDir: "/klarsatz_paket" });
  pyodide.runPython('import sys\nsys.path.insert(0, "/klarsatz_paket")');
  web = pyodide.pyimport("klarsatz.web");
}

self.onmessage = async (e) => {
  const { id, art, args } = e.data;
  try {
    if (art === "start") {
      await start(args.zipUrl);
      self.postMessage({ id, ok: true, ergebnis: null });
      return;
    }
    let text;
    if (art === "laufe") {
      // Jeder Verlaufseintrag geht sofort hinaus, noch während das Programm läuft.
      // So sieht man Ausgaben und Striche in dem Moment, in dem sie entstehen —
      // und ein Programm mit "Warte" darf endlos laufen, ohne stumm zu bleiben.
      const melde = (eintragJson) => self.postMessage({ id, teil: JSON.parse(eintragJson) });
      text = web.laufe_json(args.quelltext, JSON.stringify(args.antworten), args.seed, melde,
                            args.stufe ?? null);
    }
    else if (art === "pruefe") text = web.pruefe_json(args.quelltext);
    else if (art === "formatiere") text = web.formatiere_json(args.quelltext);
    else if (art === "nach_python") text = web.nach_python_json(args.quelltext);
    else throw new Error("Unbekannter Auftrag: " + art);
    self.postMessage({ id, ok: true, ergebnis: JSON.parse(text) });
  } catch (fehler) {
    self.postMessage({ id, ok: false, fehler: String(fehler) });
  }
};
