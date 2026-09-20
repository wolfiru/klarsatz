/*
 * Die Aufgabenseite: Angabe links, Spielwiese rechts, „Abgeben" darunter.
 *
 * Geprüft wird im selben Worker, in dem das Programm auch läuft — die Regeln
 * kommen aus docs/AUFGABEN.md und sind über spielwiese/aufgaben.json hier
 * gelandet. Es gibt also keine zweite Wahrheit darüber, was ein Programm tut.
 *
 * Gemerkt wird nur, welche Aufgaben geschafft sind, und nur im Browser des
 * Besuchers (localStorage). Nichts davon verlässt diesen Rechner.
 */
import { erstelle } from '../spielwiese/klarsatz-playground.js';

const STEMPEL = new URL(import.meta.url).search;
const SPEICHER = 'klarsatz-aufgaben-geschafft';

const el = (id) => document.getElementById(id);
const liste = el('auf-liste');

function geschafft() {
    try {
        return new Set(JSON.parse(localStorage.getItem(SPEICHER) || '[]'));
    } catch {
        return new Set();
    }
}

function merkeGeschafft(nummer) {
    try {
        const alle = geschafft();
        alle.add(nummer);
        localStorage.setItem(SPEICHER, JSON.stringify([...alle]));
    } catch { /* Privates Fenster: dann eben ohne Gedächtnis. */ }
}

const antwort = await fetch(new URL('spielwiese/aufgaben.json' + STEMPEL, document.baseURI));
const aufgaben = await antwort.json();

let spielwiese = null;
let aktuell = null;

function zeichneListe() {
    const fertig = geschafft();
    liste.replaceChildren();
    for (const a of aufgaben) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'auf-eintrag' + (a === aktuell ? ' ist-aktuell' : '')
            + (fertig.has(a.nummer) ? ' ist-fertig' : '');
        knopf.innerHTML = `<span class="auf-eintrag-nr">${a.nummer}</span>`
            + `<span class="auf-eintrag-titel">${a.titel}</span>`
            + `<span class="auf-eintrag-stufe">Stufe ${a.stufe}</span>`;
        knopf.addEventListener('click', () => waehle(a));
        liste.append(knopf);
    }
    const anzahl = aufgaben.filter((a) => fertig.has(a.nummer)).length;
    el('auf-fortschritt').textContent = anzahl
        ? `${anzahl} von ${aufgaben.length} geschafft`
        : '';
}

function waehle(a) {
    aktuell = a;
    el('auf-nummer').textContent = `Aufgabe ${a.nummer} · Stufe ${a.stufe} · ${a.lektion}`;
    el('auf-titel').textContent = a.titel;
    el('auf-text').textContent = a.angabe;
    el('auf-befund').hidden = true;
    el('auf-loesung').textContent = 'Musterlösung zeigen';

    const regeln = el('auf-regeln');
    regeln.replaceChildren();
    a.proben.forEach((probe, i) => {
        const block = document.createElement('div');
        block.className = 'auf-probe';
        const kopf = document.createElement('p');
        kopf.className = 'auf-probe-kopf';
        kopf.textContent = probe.eingaben.length
            ? `Durchlauf ${i + 1} — eingetippt wird: ${probe.eingaben.join(', ')}`
            : `Durchlauf ${i + 1} — ohne Eingaben`;
        const ul = document.createElement('ul');
        for (const text of probe.texte) {
            const li = document.createElement('li');
            li.textContent = text;
            ul.append(li);
        }
        block.append(kopf, ul);
        regeln.append(block);
    });

    if (spielwiese) spielwiese.setzeCode(`Anmerkung: Aufgabe ${a.nummer} — ${a.titel}\n\n`);
    history.replaceState(null, '', '#' + a.nummer);
    zeichneListe();
}

function zeigeBefund(befund) {
    const kasten = el('auf-befund');
    kasten.hidden = false;
    kasten.className = 'auf-befund ' + (befund.bestanden ? 'ist-gut' : 'ist-offen');
    kasten.replaceChildren();

    const kopf = document.createElement('p');
    kopf.className = 'auf-befund-kopf';
    kopf.textContent = befund.bestanden
        ? 'Geschafft — alle Regeln erfüllt.'
        : 'Noch nicht. Das hier fehlt:';
    kasten.append(kopf);

    befund.proben.forEach((probe, i) => {
        const block = document.createElement('div');
        block.className = 'auf-probe';
        const titel = document.createElement('p');
        titel.className = 'auf-probe-kopf';
        const eingaben = aktuell.proben[i].eingaben;
        titel.textContent = `Durchlauf ${i + 1}` + (eingaben.length ? ` mit ${eingaben.join(', ')}` : '');
        block.append(titel);

        if (probe.fehler) {
            const pre = document.createElement('pre');
            pre.className = 'auf-fehler';
            pre.textContent = probe.fehler;
            block.append(pre);
        }
        const ul = document.createElement('ul');
        for (const regel of probe.regeln) {
            const li = document.createElement('li');
            li.className = regel.erfuellt ? 'ist-erfuellt' : 'ist-offen';
            li.textContent = regel.text;
            ul.append(li);
        }
        block.append(ul);
        kasten.append(block);
    });

    if (befund.bestanden) {
        merkeGeschafft(aktuell.nummer);
        zeichneListe();
    }
    kasten.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

el('auf-abgeben').addEventListener('click', async () => {
    if (!spielwiese || !aktuell) return;
    const knopf = el('auf-abgeben');
    knopf.disabled = true;
    knopf.textContent = 'Wird geprüft …';
    try {
        zeigeBefund(await spielwiese.pruefeAufgabe({
            nummer: aktuell.nummer, titel: aktuell.titel, stufe: aktuell.stufe,
            proben: aktuell.proben.map((p) => ({ eingaben: p.eingaben, regeln: p.regeln })),
        }));
    } catch (fehler) {
        const kasten = el('auf-befund');
        kasten.hidden = false;
        kasten.className = 'auf-befund ist-offen';
        kasten.textContent = 'Die Prüfung hat nicht geklappt: ' + String(fehler.message || fehler);
    } finally {
        knopf.disabled = false;
        knopf.textContent = 'Abgeben';
    }
});

el('auf-loesung').addEventListener('click', () => {
    if (!spielwiese || !aktuell) return;
    const knopf = el('auf-loesung');
    if (knopf.textContent.startsWith('Musterlösung')) {
        spielwiese.setzeCode(aktuell.loesung);
        knopf.textContent = 'Das war eine von vielen Lösungen';
    }
});

const abgeben = el('auf-abgeben');
const loesungKnopf = el('auf-loesung');
abgeben.disabled = true;
loesungKnopf.disabled = true;
const wartetext = abgeben.textContent;
abgeben.textContent = 'Klarsatz lädt …';

try {
    spielwiese = await erstelle(el('spielwiese'), {
        basis: new URL('spielwiese/', document.baseURI).href,
        pyodideUrl: new URL('pyodide/', document.baseURI).href,
        zeitlimitMs: 20000,
        code: '',
    });
} catch (fehler) {
    el('spielwiese').innerHTML =
        '<div class="notiz warnung"><span class="notiz-titel">Die Spielwiese konnte nicht geladen werden</span>'
        + '<p>' + String(fehler.message || fehler) + '</p>'
        + '<p>Die Aufgaben stehen auch in <a href="https://github.com/wolfiru/klarsatz/blob/main/docs/AUFGABEN.md" rel="noopener">docs/AUFGABEN.md</a>;'
        + ' auf der Kommandozeile prüft <code>klarsatz --aufgabe NR datei.klar</code>.</p></div>';
}

const gewuenscht = aufgaben.find((a) => a.nummer === location.hash.slice(1));
waehle(gewuenscht || aufgaben[0]);

/* Erst wenn Python im Hintergrund steht, lässt sich etwas abgeben. Vorher wäre der
   Klick wirkungslos — und nichts ist ärgerlicher als ein Knopf, der nichts tut. */
spielwiese?.bereit.then(() => {
    abgeben.disabled = false;
    loesungKnopf.disabled = false;
    abgeben.textContent = wartetext;
}).catch(() => {
    abgeben.textContent = 'Prüfen geht gerade nicht';
});
