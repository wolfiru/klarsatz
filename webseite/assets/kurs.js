/*
 * „Hier ausführen" in Kurs und Dokumentation.
 *
 * Bisher führte jeder Codeblock nur über einen Link in den Spielplatz — also aus der
 * Lektion heraus. Wer dort etwas ausprobierte, verlor den Text daneben und musste
 * zurückspringen. Jetzt gibt es eine Spielwiese, die zum Block kommt, statt umgekehrt:
 * Sie wird beim ersten Klick geladen und danach nur noch verschoben. Deshalb gibt es
 * sie genau einmal pro Seite — Pyodide sind 14 MB, die lädt man nicht je Block neu.
 *
 * Der Link in den Spielplatz bleibt: Er ist für die, die mit mehr Platz weitermachen.
 */
const STEMPEL = new URL(import.meta.url).search;

function stil(pfad) {
    return new Promise((fertig, schiefgegangen) => {
        const href = new URL(pfad + STEMPEL, document.baseURI).href;
        if (document.querySelector(`link[href="${href}"]`)) return fertig();
        const el = document.createElement('link');
        el.rel = 'stylesheet';
        el.href = href;
        el.onload = fertig;
        el.onerror = () => schiefgegangen(new Error('konnte ' + pfad + ' nicht laden'));
        document.head.append(el);
    });
}

const bloecke = [...document.querySelectorAll('pre.klar')]
    .filter((pre) => pre.dataset.probieren !== 'nein'
        && pre.previousElementSibling?.classList.contains('code-kopf'));

if (bloecke.length) {
    let buehne = null;          // der Kasten mit der Spielwiese
    let spielwiese = null;      // die Spielwiese selbst
    let laedt = false;

    const machBuehne = () => {
        const kasten = document.createElement('div');
        kasten.className = 'kurs-buehne';
        kasten.innerHTML = '<div class="kurs-buehne-kopf">'
            + '<span class="kurs-buehne-titel">Spielwiese — dein Programm läuft hier in der Seite</span>'
            + '<button type="button" class="kurs-buehne-zu">Schließen</button></div>'
            + '<div class="kurs-buehne-platz"></div>';
        kasten.querySelector('.kurs-buehne-zu').addEventListener('click', () => {
            kasten.hidden = true;
        });
        return kasten;
    };

    const oeffne = async (pre, knopf) => {
        if (laedt) return;
        const code = pre.dataset.quelle ?? pre.textContent.replace(/^\n+|\s+$/g, '');

        if (spielwiese) {
            pre.after(buehne);
            buehne.hidden = false;
            spielwiese.setzeCode(code);
            spielwiese.starte();
            buehne.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            return;
        }

        laedt = true;
        const beschriftung = knopf.textContent;
        knopf.textContent = 'Klarsatz wird geladen …';
        knopf.disabled = true;
        try {
            await Promise.all(['spielwiese/klarsatz-playground.css',
                               'assets/spielwiese-design.css'].map(stil));
            const { erstelle } = await import('./../spielwiese/klarsatz-playground.js' + STEMPEL);
            buehne = machBuehne();
            pre.after(buehne);
            spielwiese = await erstelle(buehne.querySelector('.kurs-buehne-platz'), {
                basis: new URL('spielwiese/', document.baseURI).href,
                pyodideUrl: new URL('pyodide/', document.baseURI).href,
                zeitlimitMs: 20000,
                code,
            });
            spielwiese.starte();
        } catch (fehler) {
            const notiz = document.createElement('p');
            notiz.className = 'kurs-fehler';
            notiz.textContent = 'Das hat nicht geklappt: ' + String(fehler.message || fehler)
                + ' — der Spielplatz funktioniert unabhängig davon.';
            pre.after(notiz);
        } finally {
            knopf.textContent = beschriftung;
            knopf.disabled = false;
            laedt = false;
        }
    };

    for (const pre of bloecke) {
        const kopf = pre.previousElementSibling;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'hier-aus';
        knopf.textContent = '▶ Hier ausführen';
        knopf.addEventListener('click', () => oeffne(pre, knopf));
        // Vor den Link „Im Spielplatz öffnen", den app.js angehängt hat.
        const link = kopf.querySelector('.probier');
        if (link) kopf.insertBefore(knopf, link);
        else kopf.appendChild(knopf);
    }
}
