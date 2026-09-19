/*
 * Bindet die Klarsatz-Spielwiese aus spielwiese/ in die Seite ein.
 *
 * Die Spielwiese selbst stammt unverändert aus dem Klarsatz-Projekt
 * (playground/, veröffentlicht mit tools/veroeffentliche_spielwiese.py).
 * Hier kommt nur dazu, was diese Seite zusätzlich kann:
 *   - Programme aus der Adresszeile laden (#code=… und #beispiel=…)
 *   - einen Link zum aktuellen Programm erzeugen
 */
import { erstelle } from '../spielwiese/klarsatz-playground.js';

const wurzel = document.getElementById('spielwiese');
const knopfTeilen = document.getElementById('knopf-teilen');

/* Pyodide liegt auf dieser Seite selbst — absolute Adresse, damit der
   Worker sie unabhängig von seinem eigenen Ordner findet. */
const pyodideUrl = new URL('pyodide/', document.baseURI).href;

function ausHash() {
    const hash = location.hash.slice(1);
    if (hash.startsWith('code=')) {
        const code = window.Seite.dekodiere(hash.slice(5));
        if (code) return { code };
    } else if (hash.startsWith('beispiel=')) {
        return { beispiel: hash.slice(9) };
    }
    return {};
}

let spielwiese = null;

try {
    spielwiese = await erstelle(wurzel, {
        basis: new URL('spielwiese/', document.baseURI).href,
        pyodideUrl,
        zeitlimitMs: 20000,
        ...ausHash(),
    });
} catch (fehler) {
    wurzel.innerHTML = '<div class="notiz warnung"><span class="notiz-titel">Die Spielwiese konnte nicht geladen werden</span>'
        + '<p>' + String(fehler.message || fehler) + '</p>'
        + '<p>Die <a href="doku.html">Dokumentation</a> funktioniert unabhängig davon.</p></div>';
}

if (knopfTeilen && spielwiese) {
    knopfTeilen.addEventListener('click', async () => {
        const hash = '#code=' + window.Seite.kodiere(spielwiese.holeCode());
        history.replaceState(null, '', hash);
        const url = location.origin + location.pathname + hash;
        const alt = knopfTeilen.textContent;
        try {
            await navigator.clipboard.writeText(url);
            knopfTeilen.textContent = 'Link kopiert';
        } catch {
            knopfTeilen.textContent = 'Link steht in der Adresszeile';
        }
        setTimeout(() => { knopfTeilen.textContent = alt; }, 1800);
    });
}

/* Ein geteilter Link, der nachträglich eingefügt wird, lädt das Programm nach. */
window.addEventListener('hashchange', () => {
    if (!spielwiese) return;
    const { code } = ausHash();
    if (code) spielwiese.setzeCode(code);
});
