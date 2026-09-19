"""Tests für die Zeichenbefehle (Gehe, Drehe, Stift, Farbe, Strichstärke)."""
import unittest

from klarsatz import Interpreter, LaufzeitFehler, LimitFehler, SyntaxFehler
from klarsatz.grenzen import Grenzen


def zeichne(code, **kw):
    """Führt Code aus und gibt die entstandenen Striche zurück."""
    i = Interpreter(ausgabe=lambda _z: None, **kw)
    i.lauf(code)
    return i.zeichnung


def punkte(striche):
    """Nur Anfangs- und Endpunkte, gerundet — für lesbare Vergleiche."""
    return [(round(x1), round(y1), round(x2), round(y2)) for _, x1, y1, x2, y2, _f, _b in striche]


class Grundzuege(unittest.TestCase):
    def test_stift_startet_in_der_mitte_und_zeigt_nach_oben(self):
        self.assertEqual(punkte(zeichne("Gehe 100 Schritte vor.")), [(0, 0, 0, 100)])

    def test_zurueck_geht_rueckwaerts_ohne_zu_drehen(self):
        self.assertEqual(punkte(zeichne("Gehe 50 Schritte zurück.")), [(0, 0, 0, -50)])

    def test_quadrat(self):
        striche = zeichne("""
            Wiederhole 4 Mal:
                Gehe 100 Schritte vor.
                Drehe dich um 90 Grad nach rechts.
            Ende.""")
        self.assertEqual(punkte(striche),
                         [(0, 0, 0, 100), (0, 100, 100, 100), (100, 100, 100, 0), (100, 0, 0, 0)])

    def test_links_und_rechts_drehen_entgegengesetzt(self):
        rechts = punkte(zeichne("Drehe dich um 90 Grad nach rechts.\nGehe 10 Schritte vor."))
        links = punkte(zeichne("Drehe dich um 90 Grad nach links.\nGehe 10 Schritte vor."))
        self.assertEqual(rechts, [(0, 0, 10, 0)])
        self.assertEqual(links, [(0, 0, -10, 0)])

    def test_dich_und_nach_sind_freiwillig(self):
        self.assertEqual(punkte(zeichne("Drehe um 90 Grad rechts.\nGehe 10 Schritte vor.")),
                         [(0, 0, 10, 0)])

    def test_gehobener_stift_malt_nicht_bewegt_aber(self):
        striche = zeichne("""
            Hebe den Stift.
            Gehe 50 Schritte vor.
            Senke den Stift.
            Gehe 50 Schritte vor.""")
        self.assertEqual(punkte(striche), [(0, 50, 0, 100)])

    def test_zur_mitte_setzt_ort_und_richtung_zurueck(self):
        striche = zeichne("""
            Drehe dich um 90 Grad nach rechts.
            Gehe 30 Schritte vor.
            Gehe zur Mitte.
            Gehe 20 Schritte vor.""")
        self.assertEqual(punkte(striche), [(0, 0, 30, 0), (0, 0, 0, 20)])

    def test_null_schritte_malen_nichts(self):
        self.assertEqual(zeichne("Gehe 0 Schritte vor."), [])

    def test_rechnung_als_weite_und_winkel(self):
        striche = zeichne("Merke 5 als n.\nGehe n mal 20 Schritte vor.")
        self.assertEqual(punkte(striche), [(0, 0, 0, 100)])


class FarbeUndStaerke(unittest.TestCase):
    def test_farbe_faerbt_die_folgenden_striche(self):
        striche = zeichne('Gehe 10 Schritte vor.\nNimm die Farbe "rot".\nGehe 10 Schritte vor.')
        self.assertEqual(striche[0][5], "#d9b45a")          # Gold ist die Voreinstellung
        self.assertEqual(striche[1][5], "#d94f4f")

    def test_farbe_versteht_umlaute_und_grossschreibung(self):
        self.assertEqual(zeichne('Nimm die Farbe "Grün".\nGehe 1 Schritte vor.')[0][5], "#7fb069")
        self.assertEqual(zeichne('Nimm die Farbe "WEISS".\nGehe 1 Schritte vor.')[0][5], "#f3efe6")

    def test_unbekannte_farbe_schlaegt_eine_vor(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Meintest du 'rot'"):
            zeichne('Nimm die Farbe "rott".')

    def test_farbe_muss_ein_text_sein(self):
        with self.assertRaisesRegex(LaufzeitFehler, "Eine Farbe ist ein Text"):
            zeichne("Nimm die Farbe 5.")

    def test_strichstaerke(self):
        self.assertEqual(zeichne("Nimm die Strichstärke 5.\nGehe 1 Schritte vor.")[0][6], 5)

    def test_strichstaerke_hat_grenzen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "zwischen 1 und 50"):
            zeichne("Nimm die Strichstärke 99.\nGehe 1 Schritte vor.")


class Fehler(unittest.TestCase):
    def test_drehen_braucht_eine_richtung(self):
        with self.assertRaisesRegex(SyntaxFehler, "nach links.*nach rechts"):
            zeichne("Drehe dich um 90 Grad.")

    def test_gehen_braucht_vor_oder_zurueck(self):
        with self.assertRaisesRegex(SyntaxFehler, "'vor'"):
            zeichne("Gehe 10 Schritte.")

    def test_schritte_muessen_eine_zahl_sein(self):
        with self.assertRaisesRegex(LaufzeitFehler, "erwarte ich eine Zahl"):
            zeichne('Gehe "viel" Schritte vor.')

    def test_zu_viele_striche_brechen_ab(self):
        with self.assertRaisesRegex(LimitFehler, "mehr als 10 Striche"):
            zeichne("""
                Wiederhole 50 Mal:
                    Gehe 5 Schritte vor.
                    Drehe dich um 10 Grad nach links.
                Ende.""", grenzen=Grenzen(striche=10))


class EigenerKanal(unittest.TestCase):
    def test_striche_gehen_an_den_rueckruf(self):
        gesammelt = []
        i = Interpreter(ausgabe=lambda _z: None, zeichne=gesammelt.append)
        i.lauf("Gehe 10 Schritte vor.")
        self.assertEqual(len(gesammelt), 1)
        self.assertEqual(gesammelt[0][0], "linie")

    def test_zeichnung_wird_zwischen_laeufen_zurueckgesetzt(self):
        i = Interpreter(ausgabe=lambda _z: None)
        i.lauf("Gehe 10 Schritte vor.")
        i.lauf("Drehe dich um 90 Grad nach links.\nGehe 10 Schritte vor.")
        self.assertEqual(punkte(i.zeichnung)[-1], (0, 0, -10, 0))


class AlsBild(unittest.TestCase):
    def test_svg_enthaelt_jeden_strich(self):
        from klarsatz.zeichnung import als_svg
        svg = als_svg(zeichne("""
            Wiederhole 3 Mal:
                Gehe 60 Schritte vor.
                Drehe dich um 120 Grad nach rechts.
            Ende."""))
        self.assertEqual(svg.count("<path"), 3)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg)
        self.assertIn("#d9b45a", svg)

    def test_svg_spiegelt_die_y_achse(self):
        from klarsatz.zeichnung import als_svg
        # Nach oben gehen heißt im Bild: kleinerer y-Wert am Ende.
        svg = als_svg(zeichne("Gehe 100 Schritte vor."))
        anfang, ende = svg.split('d="M')[1].split('"')[0].split("L")
        self.assertGreater(float(anfang.split()[1]), float(ende.split()[1]))

    def test_leere_zeichnung_ergibt_gueltiges_svg(self):
        from klarsatz.zeichnung import als_svg
        self.assertIn("<svg", als_svg([]))

    def test_web_schnittstelle_liefert_striche_im_verlauf(self):
        from klarsatz import web
        ergebnis = web.laufe('Nimm die Farbe "blau".\nGehe 10 Schritte vor.\nZeige "fertig".')
        arten = [eintrag[0] for eintrag in ergebnis.verlauf]
        self.assertIn("linie", arten)
        self.assertIn("aus", arten)
        linie = next(e for e in ergebnis.verlauf if e[0] == "linie")
        self.assertEqual(linie[5], "#5a8fd9")


class Uhrzeit(unittest.TestCase):
    """'die aktuelle Stunde' und Geschwister — die Uhr ist austauschbar, damit Tests fest stehen."""

    FEST = __import__("time").struct_time((2026, 9, 19, 10, 8, 30, 0, 0, -1))

    def laufe(self, code):
        aus = []
        Interpreter(ausgabe=aus.append, uhr=lambda: self.FEST).lauf(code)
        return aus

    def test_stunde_minute_sekunde(self):
        self.assertEqual(self.laufe("Zeige die aktuelle Stunde."), ["10"])
        self.assertEqual(self.laufe("Zeige die aktuelle Minute."), ["8"])
        self.assertEqual(self.laufe("Zeige die aktuelle Sekunde."), ["30"])

    def test_tag_monat_jahr(self):
        self.assertEqual(self.laufe("Zeige den aktuellen Tag und \".\" und den aktuellen Monat "
                                    "und \".\" und das aktuelle Jahr."), ["19.9.2026"])

    def test_zeit_steht_waehrend_eines_laufs_still(self):
        """Sonst könnte eine Uhr zwischen Minute und Sekunde springen."""
        zaehler = []

        def tickende_uhr():
            import time
            zaehler.append(1)
            return time.struct_time((2026, 9, 19, 10, 8, len(zaehler), 0, 0, -1))

        aus = []
        Interpreter(ausgabe=aus.append, uhr=tickende_uhr).lauf(
            "Zeige die aktuelle Sekunde.\nZeige die aktuelle Sekunde.")
        self.assertEqual(aus, ["1", "1"])
        self.assertEqual(len(zaehler), 1)

    def test_in_einer_rechnung(self):
        self.assertEqual(self.laufe("Zeige die aktuelle Stunde mal 30 plus die aktuelle Minute geteilt durch 2."),
                         ["304"])

    def test_unbekanntes_wort_nach_aktuelle(self):
        with self.assertRaisesRegex(SyntaxFehler, "Stunde, Minute, Sekunde"):
            self.laufe("Zeige die aktuelle Woche.")


class Takt(unittest.TestCase):
    """'Wiederhole dieses Programm jede Sekunde.' — der Interpreter wartet nicht selbst,
    er meldet nur den Wunsch; ausführen muss ihn die Umgebung."""

    def takt(self, code):
        i = Interpreter(ausgabe=lambda _z: None)
        i.lauf(code)
        return i.wiederholung

    def test_jede_sekunde(self):
        self.assertEqual(self.takt("Wiederhole dieses Programm jede Sekunde."), 1)

    def test_mehrere_sekunden(self):
        self.assertEqual(self.takt("Wiederhole dieses Programm alle 5 Sekunden."), 5)

    def test_ohne_takt_ist_nichts_gesetzt(self):
        self.assertIsNone(self.takt('Zeige "einmal".'))

    def test_takt_gilt_nur_fuer_den_laufenden_durchgang(self):
        i = Interpreter(ausgabe=lambda _z: None)
        i.lauf("Wiederhole dieses Programm jede Sekunde.")
        i.lauf('Zeige "ohne Takt".')
        self.assertIsNone(i.wiederholung)

    def test_zu_schnell_und_zu_langsam(self):
        for code in ("Wiederhole dieses Programm alle 0.05 Sekunden.",
                     "Wiederhole dieses Programm alle 5000 Sekunden."):
            with self.assertRaisesRegex(LaufzeitFehler, "zwischen 0,1 und 3600"):
                self.takt(code)

    def test_sekunde_muss_dabeistehen(self):
        with self.assertRaisesRegex(SyntaxFehler, "Sekunde"):
            self.takt("Wiederhole dieses Programm jede Minute.")

    def test_normale_wiederholungen_gehen_weiter(self):
        aus = []
        Interpreter(ausgabe=aus.append).lauf("Wiederhole 2 Mal:\n    Zeige 1.\nEnde.")
        self.assertEqual(aus, ["1", "1"])

    def test_web_schnittstelle_meldet_den_takt(self):
        from klarsatz import web
        self.assertEqual(web.laufe("Wiederhole dieses Programm alle 2 Sekunden.").wiederholung, 2)
        self.assertIsNone(web.laufe('Zeige "x".').wiederholung)


class WarteUndLoeschen(unittest.TestCase):
    """'Warte' und 'Lösche die Zeichnung' — die Bausteine einer laufenden Anzeige."""

    def test_warte_haelt_an(self):
        import time
        i = Interpreter(ausgabe=lambda _z: None)
        vorher = time.monotonic()
        i.lauf("Warte 0.3 Sekunden.")
        self.assertGreaterEqual(time.monotonic() - vorher, 0.25)

    def test_wartezeit_zaehlt_nicht_als_rechenzeit(self):
        """Sonst würde die Zeitgrenze eine Uhr abwürgen, die brav jede Sekunde schläft."""
        from klarsatz.grenzen import Grenzen
        i = Interpreter(ausgabe=lambda _z: None, grenzen=Grenzen(sekunden=0.5))
        i.lauf("Warte 0.3 Sekunden.\nWarte 0.3 Sekunden.\nZeige \"fertig\".")

    def test_umgebung_darf_die_wartezeit_kuerzen(self):
        import time
        from klarsatz.grenzen import Grenzen
        i = Interpreter(ausgabe=lambda _z: None, grenzen=Grenzen(warte=0))
        vorher = time.monotonic()
        i.lauf("Warte 5 Sekunden.")
        self.assertLess(time.monotonic() - vorher, 1)

    def test_warten_hat_grenzen(self):
        with self.assertRaisesRegex(LaufzeitFehler, "0 bis 60"):
            Interpreter(ausgabe=lambda _z: None).lauf("Warte 90 Sekunden.")

    def test_sekunde_muss_dastehen(self):
        with self.assertRaisesRegex(SyntaxFehler, "Sekunde"):
            Interpreter(ausgabe=lambda _z: None).lauf("Warte 1 Minute.")

    def test_loeschen_leert_die_zeichnung(self):
        self.assertEqual(zeichne("Gehe 10 Schritte vor.\nLösche die Zeichnung."), [])

    def test_loeschen_meldet_sich_am_eigenen_kanal(self):
        gesammelt = []
        i = Interpreter(ausgabe=lambda _z: None, zeichne=gesammelt.append)
        i.lauf("Gehe 10 Schritte vor.\nLösche die Zeichnung.\nGehe 20 Schritte vor.")
        self.assertEqual([e[0] for e in gesammelt], ["linie", "loeschen", "linie"])

    def test_loeschen_setzt_den_strichzaehler_zurueck(self):
        """Sonst endet eine Uhr nach ein paar Stunden am Strichlimit."""
        from klarsatz.grenzen import Grenzen
        i = Interpreter(ausgabe=lambda _z: None, grenzen=Grenzen(striche=3, warte=0))
        i.lauf("""
            Wiederhole 5 Mal:
                Gehe 1 Schritte vor.
                Gehe 1 Schritte vor.
                Lösche die Zeichnung.
            Ende.""")


class Mitlesen(unittest.TestCase):
    """Die Web-Schnittstelle meldet jeden Eintrag sofort — sonst bliebe eine
    Endlosschleife stumm, egal wie viel sie ausgibt."""

    def test_eintraege_kommen_sofort(self):
        from klarsatz import web
        gemeldet = []
        ergebnis = web.laufe('Zeige "eins".\nGehe 5 Schritte vor.\nZeige "zwei".',
                             melde=gemeldet.append)
        self.assertEqual([e[0] for e in gemeldet], ["aus", "linie", "aus"])
        self.assertEqual(len(gemeldet), len(ergebnis.verlauf))

    def test_ohne_melde_bleibt_alles_wie_bisher(self):
        from klarsatz import web
        ergebnis = web.laufe('Zeige "x".')
        self.assertEqual(ergebnis.ausgabe, ["x"])

    def test_ausgabe_funktioniert_auch_wenn_gezeichnet_wird(self):
        """Striche haben sieben Teile, 'loeschen' nur einen — das darf die Ausgabe nicht stören."""
        from klarsatz import web
        ergebnis = web.laufe('Zeige "a".\nGehe 5 Schritte vor.\nLösche die Zeichnung.\nZeige "b".')
        self.assertEqual(ergebnis.ausgabe, ["a", "b"])

    def test_json_variante_meldet_texte(self):
        from klarsatz import web
        gemeldet = []
        web.laufe_json('Zeige "hallo".', melde=gemeldet.append)
        self.assertEqual(gemeldet, ['["aus", "hallo"]'])


if __name__ == "__main__":
    unittest.main()
