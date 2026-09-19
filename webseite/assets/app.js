/*
 * Gemeinsames Seitenskript: Navigation, Reveal-Animationen,
 * Syntaxfärbung für Klarsatz-Codeblöcke, Übergabe an den Spielplatz.
 */
(function (global) {
    'use strict';

    var sparsam = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    /* ---------- Hilfen ---------- */

    function esc(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    /* ---------- Code-Transfer an den Spielplatz ---------- */

    function kodiere(text) {
        var bytes = new TextEncoder().encode(text), bin = '';
        for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }

    function dekodiere(s) {
        try {
            s = s.replace(/-/g, '+').replace(/_/g, '/');
            while (s.length % 4) s += '=';
            var bin = atob(s), bytes = new Uint8Array(bin.length);
            for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
            return new TextDecoder().decode(bytes);
        } catch (e) {
            return null;
        }
    }

    /* ---------- Initialisierung ---------- */

    function navInit() {
        var nav = document.querySelector('.nav');
        if (!nav) return;
        var beiScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 24); };
        beiScroll();
        window.addEventListener('scroll', beiScroll, { passive: true });
    }

    var beobachter = null;

    function revealsBeobachten(elemente) {
        if (sparsam || !('IntersectionObserver' in window)) {
            Array.prototype.forEach.call(elemente, function (el) { el.classList.add('in'); });
            return;
        }
        if (!beobachter) {
            beobachter = new IntersectionObserver(function (eintraege) {
                eintraege.forEach(function (e) {
                    if (e.isIntersecting) {
                        e.target.classList.add('in');
                        beobachter.unobserve(e.target);
                    }
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        }
        Array.prototype.forEach.call(elemente, function (el) { beobachter.observe(el); });
    }

    /* Quelltext sichern und "Im Spielplatz öffnen"-Link anhängen.
       Die Einfärbung übernimmt assets/code-hervorhebung.js mit den echten
       Sprachregeln aus der Spielwiese. */
    function codeInit() {
        var bloecke = document.querySelectorAll('pre.klar');
        Array.prototype.forEach.call(bloecke, function (pre) {
            var quelle = pre.textContent.replace(/^\n+|\s+$/g, '');
            pre.dataset.quelle = quelle;

            if (pre.dataset.probieren === 'nein') return;
            var kopf = pre.previousElementSibling;
            if (kopf && kopf.classList.contains('code-kopf') && !kopf.querySelector('.probier')) {
                var a = document.createElement('a');
                a.className = 'probier';
                a.href = 'spielplatz.html#code=' + kodiere(quelle);
                a.textContent = 'Im Spielplatz öffnen';
                kopf.appendChild(a);
            }
        });
    }

    /* Markiert in der Doku-Seitenleiste den Abschnitt, der gerade sichtbar ist. */
    function seitenleisteInit() {
        var links = document.querySelectorAll('.doku-seitenleiste a[href^="#"]');
        if (!links.length || !('IntersectionObserver' in window)) return;

        var nachId = {};
        Array.prototype.forEach.call(links, function (a) {
            nachId[a.getAttribute('href').slice(1)] = a;
        });

        var ziele = Object.keys(nachId)
            .map(function (id) { return document.getElementById(id); })
            .filter(Boolean);
        if (!ziele.length) return;

        var sichtbar = {};
        var spion = new IntersectionObserver(function (eintraege) {
            eintraege.forEach(function (e) { sichtbar[e.target.id] = e.isIntersecting; });
            var erster = ziele.filter(function (z) { return sichtbar[z.id]; })[0];
            if (!erster) return;
            Array.prototype.forEach.call(links, function (a) { a.classList.remove('aktiv'); });
            if (nachId[erster.id]) nachId[erster.id].classList.add('aktiv');
        }, { rootMargin: '-90px 0px -65% 0px', threshold: 0 });

        ziele.forEach(function (z) { spion.observe(z); });
    }

    function jahrInit() {
        var el = document.getElementById('jahr');
        if (el) el.textContent = new Date().getFullYear();
    }

    /* Aktuellen Menüpunkt markieren. */
    function menueInit() {
        var datei = location.pathname.split('/').pop() || 'index.html';
        Array.prototype.forEach.call(document.querySelectorAll('.nav-links a'), function (a) {
            var ziel = a.getAttribute('href');
            if (!ziel || ziel.charAt(0) === '#') return;
            /* Der hervorgehobene Knopf behält seine eigene Farbgebung. */
            if (a.classList.contains('nav-cta')) return;
            if (ziel.split('#')[0] === datei) a.classList.add('aktiv');
        });
    }

    global.Seite = {
        kodiere: kodiere,
        dekodiere: dekodiere,
        reveals: revealsBeobachten,
        sparsam: sparsam
    };

    navInit();
    menueInit();
    codeInit();
    seitenleisteInit();
    jahrInit();
    revealsBeobachten(document.querySelectorAll('.reveal'));
})(window);
