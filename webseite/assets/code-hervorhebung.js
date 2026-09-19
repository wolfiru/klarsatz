/*
 * Färbt die Klarsatz-Codeblöcke der Webseite ein.
 *
 * Benutzt dieselben Regeln wie der Editor der Spielwiese, die VS-Code-
 * Erweiterung und der Pygments-Lexer — sie stammen alle aus einer einzigen
 * Regelliste im Projekt (hervorhebung.py / sprachdaten.py). Dadurch sieht ein
 * Beispiel in der Dokumentation genauso aus wie im Editor, und beides kann
 * nicht auseinanderlaufen.
 *
 * Schlägt das Laden fehl, bleiben die Blöcke schlicht uneingefärbt lesbar.
 */
import { alsHtml, inZeilen, kompiliere, tokenisiere } from '../spielwiese/klarsatz-hervorhebung.js';

const bloecke = document.querySelectorAll('pre.klar');
if (bloecke.length) {
    try {
        const antwort = await fetch(new URL('spielwiese/hervorhebung.json', document.baseURI));
        if (!antwort.ok) throw new Error(antwort.status);
        const regeln = kompiliere(await antwort.json());

        bloecke.forEach((pre) => {
            const quelle = pre.dataset.quelle ?? pre.textContent.replace(/^\n+|\s+$/g, '');
            const html = inZeilen(tokenisiere(quelle, regeln))
                .map((zeile) => zeile
                    .map(([text, name]) => (name ? `<span class="kp-t-${name}">${alsHtml(text)}</span>` : alsHtml(text)))
                    .join(''))
                .join('\n');
            pre.innerHTML = `<code>${html}</code>`;
        });
    } catch (fehler) {
        console.warn('Hervorhebung nicht geladen:', fehler);
    }
}
