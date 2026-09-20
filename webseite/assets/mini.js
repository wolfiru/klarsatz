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
function stil(pfad) {
    return new Promise((fertig, schiefgegangen) => {
        const href = new URL(pfad, document.baseURI).href;
        if (document.querySelector(`link[href="${href}"]`)) return fertig();
        const el = document.createElement('link');
        el.rel = 'stylesheet';
        el.href = href;
        el.onload = fertig;
        el.onerror = () => schiefgegangen(new Error('konnte ' + pfad + ' nicht laden'));
        document.head.append(el);
    });
}

/* Der Quelltext steht entweder im Block selbst oder — bei langen Programmen, von denen
   die Seite nur einen Ausschnitt zeigt — in der Beispielliste der Spielwiese. Dann wird er
   von dort geholt, und die Seite kann gar nicht erst eine veraltete Fassung zeigen. */
async function hole(wurzel) {
    const beispiel = wurzel.dataset.beispiel;
    if (!beispiel) {
        const pre = wurzel.querySelector('pre.klar');
        return pre?.dataset.quelle ?? pre?.textContent.replace(/^\n+|\s+$/g, '') ?? '';
    }
    const antwort = await fetch(new URL('spielwiese/beispiele.json', document.baseURI));
    if (!antwort.ok) throw new Error('Beispiel ' + beispiel + ' nicht gefunden');
    const treffer = (await antwort.json()).find((e) => e.id === beispiel);
    if (!treffer) throw new Error('Beispiel ' + beispiel + ' steht nicht in der Liste');
    return treffer.code;
}

for (const wurzel of document.querySelectorAll('.mini')) {
    const knopf = wurzel.querySelector('.mini-start');
    const buehne = wurzel.querySelector('.mini-buehne');

    knopf?.addEventListener('click', async () => {
        knopf.disabled = true;
        knopf.textContent = 'Klarsatz wird geladen …';

        try {
            const code = await hole(wurzel);
            // Die Spielwiese bringt ihr eigenes Aussehen mit. Ohne diese beiden
            // Stylesheets erscheint sie roh — mit Systemknöpfen und ohne Raster.
            // Auch sie werden erst jetzt geholt, nicht beim Laden der Seite.
            await Promise.all(['spielwiese/klarsatz-playground.css', 'assets/spielwiese-design.css'].map(stil));

            const { erstelle } = await import('./../spielwiese/klarsatz-playground.js');
            const spielwiese = await erstelle(buehne, {
                basis: new URL('spielwiese/', document.baseURI).href,
                pyodideUrl: new URL('pyodide/', document.baseURI).href,
                zeitlimitMs: 20000,
                code,
            });
            wurzel.classList.add('laeuft');
            buehne.hidden = false;

            // Sagen, wo man gelandet ist — sonst steht plötzlich ein Editor da,
            // und niemand weiß, ob die Seite gewechselt hat.
            const hinweis = wurzel.querySelector('.mini-hinweis');
            if (hinweis) hinweis.hidden = false;

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
