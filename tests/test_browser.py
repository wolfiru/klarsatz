"""Ende-zu-Ende-Test der Spielwiese in einem echten Chromium (Pyodide wird vom CDN geladen).

Wird übersprungen, wenn Playwright/Chromium fehlt, kein Netz da ist oder KLARSATZ_KEIN_BROWSER gesetzt ist."""
import functools
import http.server
import os
import subprocess
import sys
import threading
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
try:
    from playwright.sync_api import sync_playwright
    HAT_PLAYWRIGHT = True
except ImportError:
    HAT_PLAYWRIGHT = False


class _Still(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@unittest.skipUnless(HAT_PLAYWRIGHT and not os.environ.get("KLARSATZ_KEIN_BROWSER"),
                     "Playwright fehlt oder KLARSATZ_KEIN_BROWSER ist gesetzt")
class Spielwiese(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(WURZEL / "tools/baue_playground.py")], check=True, capture_output=True)
        handler = functools.partial(_Still, directory=str(WURZEL / "playground"))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/index.html"
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch()
            cls.seite = cls.browser.new_page(viewport={"width": 1280, "height": 900})
            cls.konsole = []
            cls.seite.on("console", lambda m: cls.konsole.append((m.type, m.text)))
            cls.seite.on("pageerror", lambda e: cls.konsole.append(("pageerror", str(e))))
            cls.seite.goto(cls.url)
            cls.seite.wait_for_selector("#spielwiese[data-bereit=ja]", timeout=120000)
        except Exception as e:                       # kein Browser, kein Netz zum CDN …
            cls._aufraeumen()
            raise unittest.SkipTest(f"Browser oder Pyodide nicht verfügbar: {str(e)[:120]}")

    @classmethod
    def _aufraeumen(cls):
        for name, f in (("browser", lambda: cls.browser.close()), ("pw", lambda: cls.pw.stop()),
                        ("server", lambda: cls.server.shutdown())):
            try:
                f()
            except Exception:
                pass

    @classmethod
    def tearDownClass(cls):
        cls._aufraeumen()

    # ── Hilfen ──
    def setUp(self):
        self.s = self.seite
        # Sauber anfangen: Läuft noch etwas (Dauerprogramm, Takt), erst anhalten; hat ein
        # vorheriger Test den Worker neu gestartet, warten bis Python wieder geladen ist.
        if "Anhalten" in self.s.inner_text(".kp-lauf"):
            self.s.click(".kp-lauf")
        self.s.wait_for_function("() => !document.querySelector('.kp-lauf').disabled", timeout=180000)
        self.s.select_option(".kp-auswahl", "hallo")             # zurücksetzen (löst 'change' aus)
        self.s.evaluate("document.querySelector('.kp-ausgabe').replaceChildren()")

    def code(self, text):
        self.s.fill(".kp-text", text)

    def lauf(self):
        self.s.click(".kp-lauf")

    def ausgabe(self):
        return self.s.inner_text(".kp-ausgabe")

    def antworte(self, *antworten):
        """Antworten der Reihe nach eintippen.

        Jede Frage bekommt ein **neues** Eingabefeld — das alte wird beim nächsten
        Durchlauf weggeräumt. Wer nur auf '.kp-antwortfeld' wartet, erwischt sonst
        noch das alte, abgelöste Feld, und die Antwort geht verloren. Darum wird nach
        jedem Enter gewartet, bis das benutzte Feld wirklich verschwunden ist."""
        for antwort in antworten:
            feld = self.s.wait_for_selector(".kp-antwortfeld", timeout=30000)
            feld.fill(antwort)
            feld.press("Enter")
            feld.wait_for_element_state("hidden")

    def warte_auf_ende(self, timeout=30000):
        self.s.wait_for_selector(".kp-ende, .kp-fehlertext", timeout=timeout)

    # ── Tests ──
    def test_startet_ohne_fehler_in_der_konsole(self):
        schlimm = [k for k in self.konsole if k[0] in ("pageerror", "error")]
        self.assertEqual(schlimm, [])

    def test_hallo_welt(self):
        self.lauf()
        self.warte_auf_ende()
        self.assertIn("Hallo Welt", self.ausgabe())
        self.assertIn("Hallo, Wolfgang!", self.ausgabe())
        self.assertIn("Programm beendet", self.ausgabe())
        self.assertEqual(self.s.inner_text(".kp-status"), "Fertig.")

    def test_lernstufe_sperrt_und_gibt_wieder_frei(self):
        """Die Stufenwahl ist reine JavaScript-Verdrahtung — nur hier wird sie wirklich geprüft."""
        self.code("Merke 5 als Zahl.\nZeige Zahl plus 1.")

        self.s.select_option(".kp-stufenwahl", "1")
        self.lauf()
        self.warte_auf_ende()
        self.assertIn("Das kommt später", self.ausgabe())
        self.assertIn("Stufe 2 (Rechnen)", self.ausgabe())

        self.s.evaluate("document.querySelector('.kp-ausgabe').replaceChildren()")
        self.s.select_option(".kp-stufenwahl", "2")
        self.lauf()
        self.warte_auf_ende()
        self.assertIn("6", self.ausgabe())
        self.assertNotIn("Das kommt später", self.ausgabe())

    def test_hervorhebung(self):
        self.assertGreater(self.s.locator(".kp-hervor .kp-t-anweisung").count(), 0)      # Zeige, Merke …
        self.assertGreater(self.s.locator(".kp-hervor .kp-t-text").count(), 0)
        self.assertGreater(self.s.locator(".kp-hervor .kp-t-kommentar").count(), 0)
        self.code("Wenn x größer als 3 ist:\n    Zeige x.\nEnde.")
        self.assertIn("Wenn", self.s.inner_text(".kp-hervor .kp-t-steuerung >> nth=0"))
        self.assertEqual(self.s.inner_text(".kp-nummern").split(), ["1", "2", "3"])

    def test_eingaben_im_taschenrechner(self):
        self.s.select_option(".kp-auswahl", "03_taschenrechner")
        self.lauf()
        self.antworte("+", "2", "3", "ende")
        self.warte_auf_ende()
        text = self.ausgabe()
        self.assertIn("2 + 3 = 5", text)
        self.assertIn("Tschüss!", text)
        zeilen = self.s.evaluate("[...document.querySelectorAll('.kp-frage')].map(e => e.textContent)")
        self.assertIn("Rechenart (oder ende): +", [z.replace("  ", " ") for z in zeilen])   # Frage und Antwort in einer Zeile
        self.assertEqual(self.s.locator(".kp-antwortfeld").count(), 0)

    def test_zufall_bleibt_beim_nachfragen_gleich(self):
        self.code('Zeige Zufallszahl von 1 bis 1000000.\nFrage "Weiter?" und merke die Antwort als A.\nZeige "danke".')
        self.lauf()
        self.s.wait_for_selector(".kp-antwortfeld", timeout=30000)
        erste = self.s.inner_text(".kp-aus")
        self.s.fill(".kp-antwortfeld", "ja")
        self.s.press(".kp-antwortfeld", "Enter")
        self.warte_auf_ende()
        self.assertEqual(self.s.inner_text(".kp-aus >> nth=0"), erste)
        self.assertIn("danke", self.ausgabe())

    def test_strg_enter_fuehrt_aus(self):
        self.code('Zeige "per Tastatur".')
        self.s.focus(".kp-text")
        self.s.keyboard.press("Control+Enter")
        self.warte_auf_ende()
        self.assertIn("per Tastatur", self.ausgabe())

    def test_syntaxfehler_wird_angezeigt_und_markiert(self):
        self.code("Merke 5 als Zahl.\nZeigee Zahl.")
        self.lauf()
        self.warte_auf_ende()
        self.assertIn("Meintest du 'Zeige'?", self.s.inner_text(".kp-fehlertext"))
        self.assertEqual(self.s.locator(".kp-marke-fehler").count(), 1)
        self.assertIn("Zeigee", self.s.inner_text(".kp-marke-fehler"))

    def test_laufzeitfehler_behaelt_die_ausgabe(self):
        self.code('Zeige "vorher".\nZeige 1 geteilt durch 0.')
        self.lauf()
        self.warte_auf_ende()
        self.assertIn("vorher", self.ausgabe())
        self.assertIn("Durch null kann man nicht teilen.", self.s.inner_text(".kp-fehlertext"))

    def test_pruefen_markiert_zeilen_und_springt(self):
        self.s.select_option(".kp-auswahl", "fehler")
        self.s.click(".kp-pruefen")
        self.s.wait_for_selector(".kp-b", timeout=30000)
        self.assertIn("Summme", self.s.inner_text(".kp-befunde"))
        self.assertGreater(self.s.locator(".kp-marke-fehler").count(), 0)
        self.s.click(".kp-b-fehler .kp-b-knopf")
        markiert = self.s.evaluate("(() => { const t = document.querySelector('.kp-text');"
                                   "return t.value.slice(t.selectionStart, t.selectionEnd); })()")
        self.assertIn("Summme", markiert)

    def test_pruefen_ohne_probleme(self):
        self.s.select_option(".kp-auswahl", "fizzbuzz")
        self.s.click(".kp-pruefen")
        self.s.wait_for_selector(".kp-b-ok", timeout=30000)
        self.assertIn("alles in Ordnung", self.s.inner_text(".kp-status"))

    def test_formatieren(self):
        self.code("Wenn wahr ist:\nZeige 1.\nWiederhole 2 Mal:\nZeige 2.\nEnde.\nEnde.")
        self.s.click(".kp-format")
        self.s.wait_for_function("document.querySelector('.kp-text').value.includes('    Zeige 1.')")
        self.assertEqual(self.s.input_value(".kp-text"),
                         "Wenn wahr ist:\n    Zeige 1.\n    Wiederhole 2 Mal:\n        Zeige 2.\n    Ende.\nEnde.\n")

    def test_formatieren_meldet_unfertige_texte(self):
        self.code('Zeige "offen.')
        self.s.click(".kp-format")
        self.s.wait_for_selector(".kp-fehlertext", timeout=30000)
        self.assertIn("nicht mit Anführungszeichen geschlossen", self.s.inner_text(".kp-fehlertext"))

    def test_automatisches_einruecken_und_tab(self):
        self.code("")
        self.s.focus(".kp-text")
        self.s.keyboard.type("Wenn wahr ist:")
        self.s.keyboard.press("Enter")
        self.s.keyboard.type("Zeige 1.")
        self.s.keyboard.press("Enter")
        self.s.keyboard.type("Zeige 2.")
        self.s.keyboard.press("Enter")
        self.s.keyboard.press("Tab")
        self.s.keyboard.type("x")
        self.assertEqual(self.s.input_value(".kp-text"), "Wenn wahr ist:\n    Zeige 1.\n    Zeige 2.\n        x")

    def test_endlosschleife_wird_gestoppt_und_es_geht_weiter(self):
        self.code("Wiederhole solange wahr ist:\n    Merke 1 als a.\nEnde.")
        self.lauf()
        self.s.wait_for_selector(".kp-fehlertext", timeout=60000)
        self.assertRegex(self.s.inner_text(".kp-fehlertext"), r"(Schrittlimit|Zeitlimit)")
        self.assertIn("Abgebrochen", self.s.inner_text(".kp-status"))
        self.code('Zeige "wieder da".')
        self.lauf()
        self.s.wait_for_selector(".kp-ende", timeout=30000)
        self.assertIn("wieder da", self.ausgabe())
        self.assertNotIn("Schrittlimit", self.ausgabe())

    def test_dateien_liegen_im_arbeitsspeicher(self):
        self.s.select_option(".kp-auswahl", "18_todo_liste")
        self.lauf()
        self.antworte("1", "Milch", "0")
        self.warte_auf_ende()
        self.assertIn("Bis bald!", self.ausgabe())

    def test_beispielwechsel_leert_die_ausgabe(self):
        self.lauf()
        self.warte_auf_ende()
        self.s.select_option(".kp-auswahl", "fizzbuzz")
        self.s.wait_for_function("document.querySelector('.kp-ausgabe').children.length === 0")
        self.assertIn("FizzBuzz", self.s.input_value(".kp-text").split("\n")[1] + "FizzBuzz")

    def test_alle_beispiele_laufen_bis_zur_ersten_frage_oder_zum_ende(self):
        ids = self.s.evaluate("[...document.querySelectorAll('.kp-auswahl option')].map(o => o.value)")
        # Nicht "mindestens ein paar", sondern genau die Liste: Sonst fällt es nicht auf,
        # wenn ein Beispiel aus der Auswahl verschwindet.
        import json
        erwartet = {b["id"] for b in json.loads(
            (Path(__file__).resolve().parent.parent / "playground" / "beispiele.json").read_text(encoding="utf-8"))}
        self.assertEqual(set(ids) - {""}, erwartet)
        for i in ids:
            with self.subTest(beispiel=i):
                self.s.select_option(".kp-auswahl", i)
                self.lauf()
                # Getaktete Programme ("Wiederhole dieses Programm jede Sekunde.") enden nie von
                # selbst — bei ihnen wird der Knopf zum Anhalten. Das gilt hier als Erfolg.
                self.s.wait_for_function(
                    "() => document.querySelector('.kp-antwortfeld') "
                    "|| document.querySelector('.kp-ende') "
                    "|| document.querySelector('.kp-fehlertext') "
                    "|| document.querySelector('.kp-lauf').textContent.includes('Anhalten')",
                    timeout=30000)
                fehler = self.s.locator(".kp-fehlertext")
                if fehler.count():
                    self.assertEqual(i, "fehler", fehler.first.inner_text())          # nur dieses Beispiel ist absichtlich fehlerhaft
                if "Anhalten" in self.s.inner_text(".kp-lauf"):
                    self.s.click(".kp-lauf")                                          # sonst tickt es in den nächsten Test hinein

    def test_zeichnung_erscheint_auf_der_leinwand(self):
        self.s.select_option(".kp-auswahl", "zeichnen")
        self.s.click(".kp-lauf")
        self.s.wait_for_selector(".kp-ende", timeout=60000)
        leinwand = self.s.locator(".kp-leinwand")
        self.assertTrue(leinwand.is_visible(), "Die Leinwand muss erscheinen, sobald gezeichnet wurde.")
        # Die Fläche darf nicht leer bleiben: irgendein Pixel muss sich vom Hintergrund abheben.
        gemalt = self.s.evaluate("""() => {
          const c = document.querySelector('.kp-leinwand');
          const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
          for (let i = 3; i < d.length; i += 4) if (d[i] > 0) return true;
          return false;
        }""")
        self.assertTrue(gemalt, "Auf der Leinwand ist nichts zu sehen.")

    def test_leinwand_bleibt_weg_wenn_nichts_gezeichnet_wird(self):
        self.code('Zeige "nur Text".')
        self.s.click(".kp-lauf")
        self.s.wait_for_selector(".kp-ende", timeout=60000)
        self.assertFalse(self.s.locator(".kp-leinwand").is_visible())

    def test_eigene_pyodide_adresse_wird_durchgereicht(self):
        """Die Webseite liefert Pyodide selbst aus; die Option darf den Lauf nicht stören."""
        adresse = self.s.evaluate("""async () => {
          const m = await import('./klarsatz-playground.js');
          const d = document.createElement('div'); d.id = 'dritte'; document.body.append(d);
          window.dritte = await m.erstelle(d, { pyodideUrl: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/',
                                                code: 'Zeige 6 mal 7.' });
          return document.querySelector('#dritte') ? 'erstellt' : 'fehlt';
        }""")
        self.assertEqual(adresse, "erstellt")
        self.s.wait_for_selector("#dritte[data-bereit=ja]", timeout=180000)
        self.s.click("#dritte .kp-lauf")
        self.s.wait_for_selector("#dritte .kp-ende", timeout=60000)
        self.assertIn("42", self.s.inner_text("#dritte .kp-ausgabe"))
        self.s.evaluate("window.dritte.zerstoere()")

    def test_als_python_zeigt_die_uebersetzung(self):
        self.code("Merke 5 als Zahl.\nZähle von 1 bis 3 mit i:\n    Zeige i mal Zahl.\nEnde.")
        self.s.click(".kp-python")
        self.s.wait_for_function(
            "() => document.querySelector('.kp-ausgabe').innerText.includes('for i in range')", timeout=60000)
        text = self.s.inner_text(".kp-ausgabe")
        self.assertIn("Zahl = 5", text)
        self.assertIn("print((i * Zahl))", text)

    def test_neu_knopf_leert_das_blatt(self):
        self.s.select_option(".kp-auswahl", "fizzbuzz")
        self.assertNotEqual(self.s.input_value(".kp-text"), "")
        self.s.click(".kp-neu")
        self.assertEqual(self.s.input_value(".kp-text"), "")
        self.assertEqual(self.s.input_value(".kp-auswahl"), "")

    def test_leeres_blatt_zum_selberschreiben(self):
        self.s.select_option(".kp-auswahl", "")
        self.assertEqual(self.s.input_value(".kp-text"), "")
        self.assertIn("Leeres Blatt", self.s.inner_text(".kp-status"))
        self.code('Zeige 6 mal 7.')
        self.s.click(".kp-lauf")
        self.s.wait_for_selector(".kp-ende", timeout=60000)
        self.assertIn("42", self.s.inner_text(".kp-ausgabe"))

    def test_ausgabe_erscheint_schon_waehrend_des_laufs(self):
        """Der Kern des Mitlesens: Ohne ihn bliebe ein wartendes Programm stumm."""
        self.code('Zeige "erste Zeile".\nWarte 3 Sekunden.\nZeige "zweite Zeile".')
        self.s.click(".kp-lauf")
        self.s.wait_for_function(
            "() => document.querySelector('.kp-ausgabe').innerText.includes('erste Zeile')", timeout=20000)
        # Das Programm ist hier noch mitten im Warten.
        self.assertNotIn("zweite Zeile", self.s.inner_text(".kp-ausgabe"))
        self.s.wait_for_selector(".kp-ende", timeout=30000)
        self.assertIn("zweite Zeile", self.s.inner_text(".kp-ausgabe"))

    def test_laufendes_programm_laesst_sich_abbrechen(self):
        self.code("Wiederhole solange wahr ist:\n    Warte 1 Sekunde.\nEnde.")
        self.s.click(".kp-lauf")
        self.s.wait_for_function(
            "() => document.querySelector('.kp-lauf').textContent.includes('Anhalten')", timeout=20000)
        self.s.click(".kp-lauf")
        self.s.wait_for_selector(".kp-ende", timeout=10000)
        self.assertIn("abgebrochen", self.s.inner_text(".kp-ausgabe"))
        # Danach lädt Klarsatz neu und ist wieder einsatzbereit.
        self.s.wait_for_function(
            "() => !document.querySelector('.kp-lauf').disabled", timeout=180000)

    def test_getaktetes_programm_laeuft_neu_und_laesst_sich_anhalten(self):
        self.code('Zeige die aktuelle Sekunde.\nWiederhole dieses Programm jede Sekunde.')
        self.s.click(".kp-lauf")
        self.s.wait_for_function(
            "() => document.querySelector('.kp-lauf').textContent.includes('Anhalten')", timeout=60000)

        # Ein zweiter Lauf muss von allein kommen: die angezeigte Sekunde ändert sich.
        erste = self.s.inner_text(".kp-ausgabe").strip()
        self.s.wait_for_function(
            f"() => document.querySelector('.kp-ausgabe').innerText.trim() !== {erste!r}", timeout=15000)

        # Anhalten: Knopf zurück, und danach kommt kein weiterer Lauf mehr.
        self.s.click(".kp-lauf")
        self.assertIn("Ausführen", self.s.inner_text(".kp-lauf"))
        stand = self.s.inner_text(".kp-ausgabe")
        self.s.wait_for_timeout(2500)
        self.assertEqual(stand, self.s.inner_text(".kp-ausgabe"), "Nach dem Anhalten darf nichts mehr laufen.")

    def test_hangender_lauf_wird_abgebrochen_und_der_worker_neu_gestartet(self):
        self.s.evaluate("""async () => {
          const m = await import('./klarsatz-playground.js');
          const d = document.createElement('div'); d.id = 'zweite'; document.body.append(d);
          window.zweite = await m.erstelle(d, { zeitlimitMs: 400, code: 'Wiederhole solange wahr ist:\\n    Merke 1 als a.\\nEnde.' });
        }""")
        self.s.wait_for_selector("#zweite[data-bereit=ja]", timeout=60000)
        self.s.click("#zweite .kp-lauf")
        self.s.wait_for_selector("#zweite .kp-fehlertext", timeout=30000)
        self.assertIn("zu lange gebraucht", self.s.inner_text("#zweite .kp-fehlertext"))

        # Danach startet der Worker neu, und ein zweiter Lauf muss wieder gehen. Das dauert,
        # weil Pyodide dabei noch einmal geladen wird — daher das großzügige Zeitlimit.
        self.assertFalse(self.s.locator("#zweite .kp-lauf").is_disabled())
        self.s.evaluate("window.zweite.setzeCode('Zeige 1 plus 1.')")
        self.s.click("#zweite .kp-lauf")
        self.s.wait_for_selector("#zweite .kp-ende", timeout=180000)
        self.assertIn("2", self.s.inner_text("#zweite .kp-ausgabe"))

        self.s.evaluate("window.zweite.zerstoere()")


if __name__ == "__main__":
    unittest.main()


WEBORDNER = Path("/var/www/html/klarsatz")


@unittest.skipUnless(HAT_PLAYWRIGHT and not os.environ.get("KLARSATZ_KEIN_BROWSER"),
                     "Playwright fehlt oder KLARSATZ_KEIN_BROWSER ist gesetzt")
@unittest.skipUnless((WEBORDNER / "tutorial.html").exists() and (WEBORDNER / "pyodide").is_dir(),
                     "Die veröffentlichte Webseite liegt hier nicht")
class WegInDieSpielwiese(unittest.TestCase):
    """Vom Kurs in den Editor.

    Das Tutorial sagt "probier das aus" — also muss es auch einen Weg dorthin geben. Der
    entsteht erst im Browser: assets/app.js hängt an jeden Codeblock mit Kopf den Link
    "Im Spielplatz öffnen" und packt das Programm kodiert in die Adresse. Nur hier lässt
    sich prüfen, dass diese Kette hält.

    Geprüft wird gegen die **veröffentlichte** Seite; wo die nicht liegt, wird übersprungen.
    """

    @classmethod
    def setUpClass(cls):
        handler = functools.partial(_Still, directory=str(WEBORDNER))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.basis = f"http://127.0.0.1:{cls.server.server_address[1]}/"
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch()
            cls.s = cls.browser.new_page(viewport={"width": 1280, "height": 900})
        except Exception as e:
            cls.pw.stop()
            cls.server.shutdown()
            raise unittest.SkipTest(f"Browser nicht verfügbar: {str(e)[:120]}")

    @classmethod
    def tearDownClass(cls):
        for schliesse in (getattr(cls, "browser", None), getattr(cls, "pw", None)):
            try:
                (schliesse.close if hasattr(schliesse, "close") else schliesse.stop)()
            except Exception:
                pass
        cls.server.shutdown()

    def test_jeder_codeblock_der_kurse_laesst_sich_oeffnen(self):
        for seite in ("tutorial.html", "tutorial-zeichnen.html"):
            with self.subTest(seite=seite):
                self.s.goto(self.basis + seite)
                self.s.wait_for_selector("a.probier", timeout=30000)
                bloecke = self.s.locator("pre.klar").count()
                links = self.s.locator("a.probier").count()
                self.assertEqual(links, bloecke,
                                 f"{seite}: {bloecke} Beispiele, aber nur {links} zum Öffnen.")

    def test_das_programm_landet_wirklich_im_editor(self):
        self.s.goto(self.basis + "tutorial.html")
        self.s.wait_for_selector("a.probier", timeout=30000)
        ziel = self.s.get_attribute("a.probier", "href")
        self.assertTrue(ziel.startswith("spielplatz.html#code="), ziel[:40])

        self.s.goto(self.basis + ziel)
        self.s.wait_for_function("() => !document.querySelector('.kp-lauf').disabled", timeout=180000)
        self.assertIn("Zeige", self.s.input_value(".kp-text"))

    def test_die_spielwiese_traegt_das_design_der_seite(self):
        """Die Spielwiese bringt helle Farben mit und bekommt dunkle von der Seite.

        Das ging still kaputt: Die Spielwiese setzt ihre Variablen auf `.kp`, die
        Anpassung der Seite setzte sie nur auf `:root` — und was näher am Element
        steht, gewinnt. Ergebnis war ein weißer Editor auf schwarzer Seite. Von außen
        sieht man so etwas nur, wenn man wirklich hinschaut."""
        self.s.goto(self.basis + "spielplatz.html")
        self.s.wait_for_selector(".kp", timeout=180000)
        farbe = self.s.evaluate("getComputedStyle(document.querySelector('.kp')).backgroundColor")
        werte = [int(x) for x in farbe.replace("rgb(", "").replace(")", "").split(",")[:3]]
        self.assertLess(sum(werte) / 3, 80,
                        f"Die Spielwiese ist hell ({farbe}) — das Design der Seite greift nicht.")

    def test_die_sofort_demo_laedt_erst_auf_klick(self):
        """Der ganze Sinn der Demo: Sie kostet nichts, bis jemand sie will.

        Klarsatz im Browser heißt Pyodide, und das sind 14 MB. Würden die beim Laden der
        Startseite mitkommen, wäre die Demo ein Schaden statt eines Gewinns."""
        self.s.goto(self.basis)
        self.s.wait_for_selector(".mini-start")
        vorher = self.s.evaluate(
            "performance.getEntriesByType('resource').filter(r => r.name.includes('pyodide')).length")
        self.assertEqual(vorher, 0, "Pyodide wird schon beim Laden der Startseite geholt.")

        self.s.click(".mini-start")
        self.s.wait_for_selector("#mini .kp-ende, #mini .kp-fehlertext", timeout=180000)
        self.assertIn("Fünf plus drei ist 8.", self.s.inner_text("#mini .kp-ausgabe"))
        nachher = self.s.evaluate(
            "performance.getEntriesByType('resource').filter(r => r.name.includes('pyodide')).length")
        self.assertGreater(nachher, 0, "Nach dem Klick muss Pyodide geladen worden sein.")

    def sichtbare_absaetze(self, seite):
        return seite.evaluate("""() => {
            const ist = (e) => {
                const s = getComputedStyle(e);
                return s.opacity !== '0' && s.visibility !== 'hidden' && s.display !== 'none';
            };
            return [...document.querySelectorAll('h1, h2, p')].filter(ist).length;
        }""")

    def test_der_inhalt_verschwindet_nicht_wieder(self):
        """Einmal sichtbar, immer sichtbar.

        Es gab hier eine Einblend-Animation: erst alles unsichtbar, dann beim Scrollen
        eingeblendet. In manchen Browsern war die Seite dadurch kurz zu sehen und dann
        weg. Deshalb darf kein Skript mehr Inhalt verstecken — dieser Test schaut zweimal
        nach, direkt nach dem Laden und ein paar Sekunden später."""
        for datei in ("", "tutorial.html", "doku.html"):
            with self.subTest(seite=datei or "index.html"):
                self.s.goto(self.basis + datei)
                self.s.wait_for_selector("h1, h2")
                sofort = self.sichtbare_absaetze(self.s)
                self.assertGreater(sofort, 10, f"{datei or 'index.html'} ist beim Laden leer.")
                self.s.wait_for_timeout(3000)
                self.assertGreaterEqual(
                    self.sichtbare_absaetze(self.s), sofort,
                    f"{datei or 'index.html'}: Inhalt ist nach dem Laden wieder verschwunden.")

    def test_kein_text_verschwindet_hinter_dem_hintergrund(self):
        """Das Hintergrund-Bild darf keinen Text übermalen.

        #manuskript ist ein Canvas mit position: fixed und z-index: 0. Es liegt damit
        über jedem Textblock, der keine eigene Stapelebene aufmacht. Der Kontaktblock
        hatte keine und war unsichtbar, obwohl er im Quelltext stand und jede Messung
        ihn als sichtbar meldete — auffallen kann das nur, wenn man nachsieht, was an
        der Stelle tatsächlich obenauf liegt."""
        sucht = """() => {
            const verdeckt = [];
            for (const e of document.querySelectorAll('h1,h2,h3,p,li,td,th,a')) {
                const r = e.getBoundingClientRect();
                if (r.width < 5 || r.height < 5) continue;
                if (r.top < 80 || r.bottom > window.innerHeight) continue;
                const oben = document.elementFromPoint(
                    r.left + Math.min(r.width / 2, 40), r.top + r.height / 2);
                if (oben && oben.tagName === 'CANVAS') {
                    const s = e.closest('section');
                    verdeckt.push((s ? '#' + (s.id || s.className) : '?') + ': '
                                  + e.textContent.trim().slice(0, 40));
                }
            }
            return verdeckt;
        }"""
        for datei in ("spielplatz.html", "doku.html", ""):
            with self.subTest(seite=datei or "index.html"):
                self.s.goto(self.basis + datei)
                self.s.wait_for_selector("h1, h2")
                hoehe = self.s.evaluate("document.body.scrollHeight")
                verdeckt = []
                for y in range(0, hoehe, 700):
                    self.s.evaluate(f"window.scrollTo(0, {y})")
                    self.s.wait_for_timeout(120)
                    verdeckt += self.s.evaluate(sucht)
                self.assertEqual(sorted(set(verdeckt)), [],
                                 "Diese Stellen liegen hinter dem Hintergrund und sind unsichtbar.")

    def test_ohne_javascript_bleibt_die_seite_lesbar(self):
        """Dasselbe, wenn das Skript gar nicht erst ankommt: blockiert, kaputt, abgeschaltet."""
        ctx = self.browser.new_context(java_script_enabled=False)
        seite = ctx.new_page()
        try:
            for datei in ("", "tutorial.html", "doku.html"):
                with self.subTest(seite=datei or "index.html"):
                    seite.goto(self.basis + datei)
                    seite.wait_for_selector("h1, h2")
                    self.assertGreater(self.sichtbare_absaetze(seite), 10,
                                       f"{datei or 'index.html'} ist ohne JavaScript praktisch leer.")
        finally:
            ctx.close()

    def test_im_kurs_laeuft_die_spielwiese_in_der_lektion(self):
        """Der Link in den Spielplatz führt aus der Lektion heraus — der Knopf nicht.

        Geprüft wird beides, was daran wichtig ist: dass das Programm wirklich läuft, und
        dass es die Spielwiese **einmal** gibt. Eine je Codeblock hieße Pyodide je Block
        neu laden, und das sind 14 MB."""
        self.s.goto(self.basis + "tutorial.html")
        self.s.wait_for_selector(".hier-aus", timeout=60000)
        knoepfe = self.s.query_selector_all(".hier-aus")
        self.assertGreater(len(knoepfe), 20, "Kaum ein Codeblock lässt sich in der Lektion starten.")

        knoepfe[0].click()
        self.s.wait_for_function(
            "() => document.querySelector('.kurs-buehne .kp-ausgabe')?.textContent.includes('Hallo')",
            timeout=240000)
        self.assertIn("Hallo", self.s.inner_text(".kurs-buehne .kp-ausgabe"))

        # Die Bühne wandert zum nächsten Block, statt sich zu vermehren.
        knoepfe[1].click()
        self.s.wait_for_timeout(2500)
        self.assertEqual(len(self.s.query_selector_all(".kurs-buehne")), 1)
        self.assertTrue(self.s.evaluate("""() => {
            const b = document.querySelector('.kurs-buehne');
            const pre = document.querySelectorAll('.hier-aus')[1].closest('.code-kopf').nextElementSibling;
            return b.previousElementSibling === pre;
        }"""), "Die Spielwiese steht nicht bei dem Block, auf den geklickt wurde.")

        # Und der Weg in den Spielplatz bleibt für die, die mehr Platz wollen.
        self.assertTrue(self.s.query_selector(".code-kopf .probier"))

    def test_eine_uebungsaufgabe_laesst_sich_abgeben(self):
        """Der ganze Weg: Aufgabe wählen, Lösung eintippen, abgeben, Rückmeldung lesen.

        Geprüft wird im selben Worker, in dem das Programm läuft — hier zeigt sich, ob
        die Kette vom Regeltext in docs/AUFGABEN.md bis zum Haken auf der Seite hält."""
        self.s.goto(self.basis + "aufgaben.html")
        self.s.wait_for_selector(".auf-eintrag", timeout=60000)
        self.assertGreaterEqual(len(self.s.query_selector_all(".auf-eintrag")), 12)
        self.s.wait_for_function("() => !document.querySelector('.kp-lauf')?.disabled", timeout=240000)

        # Aufgabe 1 ist gewählt; erst eine Lösung, die noch nicht reicht.
        self.s.fill(".kp-text", 'Zeige "Hallo".')
        self.s.click("#auf-abgeben")
        self.s.wait_for_selector(".auf-befund:not([hidden])", timeout=120000)
        self.s.wait_for_function("() => document.querySelector('.auf-befund').classList.contains('ist-offen')",
                                 timeout=120000)
        self.assertIn("Noch nicht", self.s.inner_text(".auf-befund-kopf"))
        self.assertTrue(self.s.query_selector_all(".auf-befund li.ist-offen"))

        # Dann die Musterlösung — sie muss durchkommen.
        self.s.click("#auf-loesung")
        self.s.click("#auf-abgeben")
        self.s.wait_for_function("() => document.querySelector('.auf-befund').classList.contains('ist-gut')",
                                 timeout=120000)
        self.assertIn("Geschafft", self.s.inner_text(".auf-befund-kopf"))
        self.assertIn("geschafft", self.s.inner_text("#auf-fortschritt").lower())
        self.assertTrue(self.s.query_selector(".auf-eintrag.ist-fertig"),
                        "Die geschaffte Aufgabe wird in der Liste nicht abgehakt.")

    def test_leeres_blatt_zum_selbertippen(self):
        """Die Aufgaben im Kurs brauchen eine leere Fläche."""
        self.s.goto(self.basis + "spielplatz.html#beispiel=")
        self.s.reload()   # ein Ankersprung im selben Dokument lädt die Seite nicht neu
        self.s.wait_for_function("() => !document.querySelector('.kp-lauf').disabled", timeout=180000)
        self.assertEqual(self.s.input_value(".kp-text").strip(), "")
