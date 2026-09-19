/*
 * Manuskript-Hintergrund für Klarsatz
 * ------------------------------------
 * Erzeugt prozedural (Canvas 2D, kein Bild-Asset) eine Schreibmaschinen-Anmutung:
 * langsam aufsteigende Satzfragmente in Klarsatz-Syntax, dazu ein Satz, der
 * Zeichen für Zeichen "getippt" wird. Respektiert prefers-reduced-motion und
 * pausiert, sobald der Tab im Hintergrund liegt.
 */
(function () {
    'use strict';

    var canvas = document.getElementById('manuskript');
    if (!canvas || !canvas.getContext) return;

    var ctx = canvas.getContext('2d', { alpha: false });
    var sparsam = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var INK = '#0c0e0b';
    var GOLD = '217, 180, 90';
    var PAPER = '243, 239, 230';
    var MOSS = '127, 176, 105';

    /* Satzfragmente, die im Hintergrund treiben — echte Klarsatz-Syntax. */
    var FRAGMENTE = [
        'Zeige "Hallo Welt".',
        'Merke 5 als Zahl.',
        'Wiederhole 3 Mal:',
        'Ende.',
        'Wenn die Zahl größer als 10 ist:',
        'Sonst zeige "klein".',
        'Zähle von 1 bis 10 mit i:',
        'Füge "Milch" zur Einkauf hinzu.',
        'Definiere Aufgabe Summe von a und b:',
        'Gib a plus b zurück.',
        'Für jedes Element in Einkauf:',
        'Erhöhe die Zahl um 1.',
        'Ein Hund hat einen Namen und ein Alter.',
        'Sortiere Einkauf.',
        'Frage "Wie heißt du?" und merke die Antwort als Name.',
        'Anmerkung: erklärt etwas.',
        'Stelle sicher, dass die Zahl größer als 0 ist.',
        'Wiederhole solange n kleiner als 10 ist:',
        'Verbinde "Hallo, " und Name zu Gruss.',
        'Teile Satz bei " " zu Woerter.',
        'die Wurzel von x',
        'a durch 3 teilbar',
        'Höre auf.',
        'Versuche:',
        'Bei Fehler:',
        'Erschaffe einen Hund mit Name "Bello" und Alter 5 als Waldi.'
    ];

    /* Sätze für den Tipp-Effekt — kurz genug, um lesbar zu bleiben. */
    var TIPPSAETZE = [
        'Zeige "Hallo Welt".',
        'Merke 3 mal 7 als Ergebnis.',
        'Wiederhole 3 Mal: Zeige "Klarsatz". Ende.',
        'Wenn Alter mindestens 18 ist, zeige "willkommen".',
        'Zähle von 1 bis 5 mit i: Zeige i. Ende.',
        'Gib die Wurzel von 144 zurück.'
    ];

    var B = 0, H = 0, dpr = 1;
    var zeilen = [];
    var tipp = null;
    var letzteZeit = 0;
    var laeuft = true;

    function zufall(min, max) { return min + Math.random() * (max - min); }

    function neueZeile(yStart) {
        var groesse = zufall(11, 20);
        return {
            text: FRAGMENTE[(Math.random() * FRAGMENTE.length) | 0],
            x: zufall(-0.06, 0.92) * B,
            y: yStart,
            groesse: groesse,
            tempo: zufall(3, 9) / groesse * 8,   /* kleinere Schrift = langsamer (Tiefenwirkung) */
            deckkraft: zufall(0.05, 0.16) * (groesse / 20),
            gold: Math.random() < 0.22,
            neigung: zufall(-0.012, 0.012)
        };
    }

    function neuerTipp() {
        return {
            text: TIPPSAETZE[(Math.random() * TIPPSAETZE.length) | 0],
            zeichen: 0,
            x: zufall(0.08, 0.34) * B,
            y: zufall(0.3, 0.72) * H,
            groesse: Math.max(15, Math.min(27, B / 52)),
            phase: 'tippen',   /* tippen -> halten -> verblassen */
            warten: 0,
            deckkraft: 0
        };
    }

    function aufbauen() {
        dpr = Math.min(window.devicePixelRatio || 1, 1.6);
        B = canvas.clientWidth;
        H = canvas.clientHeight;
        canvas.width = Math.round(B * dpr);
        canvas.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        var anzahl = Math.max(10, Math.min(26, Math.round(B * H / 62000)));
        zeilen = [];
        for (var i = 0; i < anzahl; i++) zeilen.push(neueZeile(zufall(-0.1, 1.1) * H));
        tipp = neuerTipp();
        if (sparsam) zeichnen(0);
    }

    function papierlinien() {
        /* Sehr feine waagrechte Linien wie auf Manuskriptpapier. */
        ctx.strokeStyle = 'rgba(' + PAPER + ', 0.022)';
        ctx.lineWidth = 1;
        var abstand = 34;
        ctx.beginPath();
        for (var y = abstand; y < H; y += abstand) {
            ctx.moveTo(0, y + 0.5);
            ctx.lineTo(B, y + 0.5);
        }
        ctx.stroke();

        /* Randlinie links, wie der Heftrand. */
        var rand = Math.min(120, B * 0.12);
        ctx.strokeStyle = 'rgba(' + GOLD + ', 0.07)';
        ctx.beginPath();
        ctx.moveTo(rand + 0.5, 0);
        ctx.lineTo(rand + 0.5, H);
        ctx.stroke();
    }

    function zeichnen(dt) {
        ctx.fillStyle = INK;
        ctx.fillRect(0, 0, B, H);
        papierlinien();

        ctx.textBaseline = 'alphabetic';

        for (var i = 0; i < zeilen.length; i++) {
            var z = zeilen[i];
            if (!sparsam) {
                z.y -= z.tempo * dt;
                if (z.y < -40) {
                    zeilen[i] = neueZeile(H + zufall(20, 160));
                    continue;
                }
            }
            ctx.save();
            ctx.translate(z.x, z.y);
            ctx.rotate(z.neigung);
            ctx.font = z.groesse + 'px "JetBrains Mono", "Cascadia Code", Consolas, monospace';
            ctx.fillStyle = 'rgba(' + (z.gold ? GOLD : PAPER) + ', ' + z.deckkraft.toFixed(3) + ')';
            ctx.fillText(z.text, 0, 0);
            ctx.restore();
        }

        if (tipp) tippZeichnen(dt);
    }

    function tippZeichnen(dt) {
        var t = tipp;

        if (!sparsam) {
            if (t.phase === 'tippen') {
                t.deckkraft = Math.min(1, t.deckkraft + dt * 3);
                t.zeichen += dt * 13;
                if (t.zeichen >= t.text.length) {
                    t.zeichen = t.text.length;
                    t.phase = 'halten';
                    t.warten = 2.6;
                }
            } else if (t.phase === 'halten') {
                t.warten -= dt;
                if (t.warten <= 0) t.phase = 'verblassen';
            } else {
                t.deckkraft -= dt * 0.5;
                if (t.deckkraft <= 0) { tipp = neuerTipp(); return; }
            }
        } else {
            t.zeichen = t.text.length;
            t.deckkraft = 1;
        }

        var sichtbar = t.text.slice(0, Math.floor(t.zeichen));
        ctx.font = t.groesse + 'px "JetBrains Mono", "Cascadia Code", Consolas, monospace';

        /* Der Satz selbst, dezent in Papierweiß. */
        ctx.fillStyle = 'rgba(' + PAPER + ', ' + (0.3 * t.deckkraft).toFixed(3) + ')';
        ctx.fillText(sichtbar, t.x, t.y);

        /* Anführungszeichen-Inhalte in Moosgrün nachzeichnen, wie im Editor. */
        var auf = sichtbar.indexOf('"');
        if (auf !== -1) {
            var zu = sichtbar.indexOf('"', auf + 1);
            var text = sichtbar.slice(auf, zu === -1 ? sichtbar.length : zu + 1);
            ctx.fillStyle = 'rgba(' + MOSS + ', ' + (0.42 * t.deckkraft).toFixed(3) + ')';
            ctx.fillText(text, t.x + ctx.measureText(sichtbar.slice(0, auf)).width, t.y);
        }

        /* Schreibmarke. */
        if (t.phase !== 'verblassen') {
            var breite = ctx.measureText(sichtbar).width;
            var blink = t.phase === 'halten' ? (Math.sin(performance.now() / 260) > 0 ? 1 : 0.15) : 1;
            ctx.fillStyle = 'rgba(' + GOLD + ', ' + (0.75 * t.deckkraft * blink).toFixed(3) + ')';
            ctx.fillRect(t.x + breite + 2, t.y - t.groesse * 0.78, 2, t.groesse * 0.95);
        }

        /* Unterstreichung als Schreiblinie. */
        ctx.strokeStyle = 'rgba(' + GOLD + ', ' + (0.16 * t.deckkraft).toFixed(3) + ')';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(t.x, t.y + t.groesse * 0.42);
        ctx.lineTo(t.x + t.groesse * 22, t.y + t.groesse * 0.42);
        ctx.stroke();
    }

    function schleife(zeit) {
        if (!laeuft) return;
        var dt = Math.min((zeit - letzteZeit) / 1000, 0.05);
        letzteZeit = zeit;
        zeichnen(dt);
        requestAnimationFrame(schleife);
    }

    var neuAufbauTimer = null;
    window.addEventListener('resize', function () {
        clearTimeout(neuAufbauTimer);
        neuAufbauTimer = setTimeout(aufbauen, 180);
    });

    document.addEventListener('visibilitychange', function () {
        if (sparsam) return;
        if (document.hidden) {
            laeuft = false;
        } else if (!laeuft) {
            laeuft = true;
            letzteZeit = performance.now();
            requestAnimationFrame(schleife);
        }
    });

    aufbauen();
    if (!sparsam) {
        letzteZeit = performance.now();
        requestAnimationFrame(schleife);
    }
})();
