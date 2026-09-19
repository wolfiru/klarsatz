/*
 * Die Sofort-Demo auf der Startseite.
 *
 * Klarsatz im Browser heißt Pyodide, und das sind 14 MB. Die dürfen eine
 * Startseite nicht beim Laden ausbremsen — also passiert hier zunächst gar
 * nichts: Zu sehen ist ein Programm und ein Knopf. Erst beim Klick wird die
 * echte Spielwiese nachgeladen, an die Stelle gesetzt und sofort gestartet.
 *
 * Wer nie klickt, zahlt nichts. Wer klickt, ist nach ein paar Sekunden mitten
 * in einem laufenden Programm — ohne Installation, ohne Konto, ohne Seitenwechsel.
 */
const wurzel = document.getElementById('mini');

if (wurzel) {
    const knopf = wurzel.querySelector('.mini-start');
    const buehne = wurzel.querySelector('.mini-buehne');
    const quelle = wurzel.querySelector('pre.klar');

    knopf?.addEventListener('click', async () => {
        const code = quelle?.dataset.quelle ?? quelle?.textContent.replace(/^\n+|\s+$/g, '') ?? '';
        knopf.disabled = true;
        knopf.textContent = 'Klarsatz wird geladen …';

        try {
            const { erstelle } = await import('./../spielwiese/klarsatz-playground.js');
            const spielwiese = await erstelle(buehne, {
                basis: new URL('spielwiese/', document.baseURI).href,
                pyodideUrl: new URL('pyodide/', document.baseURI).href,
                zeitlimitMs: 20000,
                code,
            });
            wurzel.classList.add('laeuft');
            buehne.hidden = false;
            spielwiese.starte();
        } catch (fehler) {
            knopf.disabled = false;
            knopf.textContent = '▶ Noch einmal versuchen';
            const notiz = document.createElement('p');
            notiz.className = 'mini-fehler';
            notiz.textContent = 'Das hat nicht geklappt: ' + String(fehler.message || fehler)
                + ' — der ' ;
            const a = document.createElement('a');
            a.href = 'spielplatz.html';
            a.textContent = 'Spielplatz';
            notiz.append(a, document.createTextNode(' funktioniert unabhängig davon.'));
            wurzel.append(notiz);
        }
    });
}
