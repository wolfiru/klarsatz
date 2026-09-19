"""Dateizugriff für Klarsatz-Programme – austauschbar und auf Wunsch streng begrenzt."""
import os

from .fehler import LaufzeitFehler


class Dateisystem:
    """Schnittstelle: Was ein Programm mit 'Lies' und 'Schreibe' tun darf."""

    def lesen(self, pfad, max_zeichen):
        raise NotImplementedError

    def schreiben(self, pfad, text, max_zeichen):
        raise NotImplementedError


class KeinDateisystem(Dateisystem):
    """Jeder Dateizugriff ist verboten."""

    def lesen(self, pfad, max_zeichen):
        raise LaufzeitFehler("Dateizugriff ist in diesem Lauf abgeschaltet.")

    def schreiben(self, pfad, text, max_zeichen):
        raise LaufzeitFehler("Dateizugriff ist in diesem Lauf abgeschaltet.")


class OrdnerDateisystem(Dateisystem):
    """Echte Dateien, aber nur in einem Ordner (und darunter). wurzel=None erlaubt alles (gefährlich!).

    Ausbrüche über absolute Pfade, '..' oder Verknüpfungen (Symlinks) werden abgefangen."""

    def __init__(self, wurzel=None):
        self.wurzel = os.path.realpath(wurzel) if wurzel is not None else None

    def _aufloesen(self, pfad):
        if not isinstance(pfad, str) or pfad == "" or "\x00" in pfad:
            raise LaufzeitFehler("Das ist kein gültiger Dateiname.")
        if self.wurzel is None:
            return pfad
        voll = os.path.realpath(os.path.join(self.wurzel, pfad))
        vorne = self.wurzel if self.wurzel.endswith(os.sep) else self.wurzel + os.sep
        if voll != self.wurzel and not voll.startswith(vorne):
            raise LaufzeitFehler(f"Auf '{pfad}' darf dieses Programm nicht zugreifen: "
                                 "erlaubt sind nur Dateien im Arbeitsordner und darunter.")
        return voll

    @staticmethod
    def _uebersetze(pfad, e):
        if isinstance(e, FileNotFoundError):
            return LaufzeitFehler(f"Die Datei '{pfad}' gibt es nicht.")
        if isinstance(e, IsADirectoryError):
            return LaufzeitFehler(f"'{pfad}' ist ein Ordner, keine Datei.")
        if isinstance(e, PermissionError):
            return LaufzeitFehler(f"Für die Datei '{pfad}' fehlt die Berechtigung.")
        return LaufzeitFehler(f"Mit der Datei '{pfad}' ist etwas schiefgegangen ({e.strerror or 'Fehler'}).")

    def lesen(self, pfad, max_zeichen):
        voll = self._aufloesen(pfad)
        try:
            with open(voll, encoding="utf-8") as f:
                text = f.read(max_zeichen + 1)
        except UnicodeDecodeError:
            raise LaufzeitFehler(f"Die Datei '{pfad}' ist keine Textdatei (UTF-8).")
        except OSError as e:
            raise self._uebersetze(pfad, e)
        if len(text) > max_zeichen:
            raise LaufzeitFehler(f"Die Datei '{pfad}' ist zu groß (mehr als {max_zeichen} Zeichen).")
        return text

    def schreiben(self, pfad, text, max_zeichen):
        voll = self._aufloesen(pfad)
        if len(text) > max_zeichen:
            raise LaufzeitFehler(f"Der Text ist zu lang für eine Datei (mehr als {max_zeichen} Zeichen).")
        try:
            with open(voll, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError as e:
            raise self._uebersetze(pfad, e)


class SpeicherDateisystem(Dateisystem):
    """Dateien nur im Arbeitsspeicher (für Webseiten und Tests). Namen sind flach, ohne Ordner."""

    def __init__(self, dateien=None, max_dateien=100):
        self.dateien = dict(dateien or {})
        self.max_dateien = max_dateien

    @staticmethod
    def _name(pfad):
        if not isinstance(pfad, str) or not pfad.strip() or len(pfad) > 200 or "\x00" in pfad:
            raise LaufzeitFehler("Das ist kein gültiger Dateiname.")
        return pfad.strip()

    def lesen(self, pfad, max_zeichen):
        name = self._name(pfad)
        if name not in self.dateien:
            raise LaufzeitFehler(f"Die Datei '{pfad}' gibt es nicht.")
        return self.dateien[name]

    def schreiben(self, pfad, text, max_zeichen):
        name = self._name(pfad)
        if len(text) > max_zeichen:
            raise LaufzeitFehler(f"Der Text ist zu lang für eine Datei (mehr als {max_zeichen} Zeichen).")
        if name not in self.dateien and len(self.dateien) >= self.max_dateien:
            raise LaufzeitFehler(f"Es sind schon {self.max_dateien} Dateien angelegt – mehr geht nicht.")
        self.dateien[name] = text
