"""Syntax-Hervorhebung für Klarsatz – EINE Regelliste, drei Ausgaben:
TextMate-Grammatik (VS Code, Shiki, GitHub …), Pygments-Lexer (Sphinx, MkDocs …) und Regeln für JavaScript.

Regeln sind (Regex, Bereiche). `Bereiche` ist ein Textname für den ganzen Treffer oder eine Liste mit einem Namen
pro Klammergruppe (None = ohne Farbe). Bei Regeln mit Gruppen decken die Gruppen den ganzen Treffer ab."""
import re

from .sprachdaten import (ANWEISUNGEN, BINDEWOERTER, FUNKTIONEN_MIT_VON, KONSTANTEN, KONTROLLE, alternative,
                          wort_regex)

TEXTMATE = {
    "kommentar": "comment.line.klarsatz", "text": "string.quoted.double.klarsatz",
    "zahl": "constant.numeric.klarsatz", "steuerung": "keyword.control.klarsatz",
    "anweisung": "keyword.other.statement.klarsatz", "funktion": "support.function.builtin.klarsatz",
    "konstante": "constant.language.klarsatz", "operator": "keyword.operator.word.klarsatz",
    "funktionsname": "entity.name.function.klarsatz", "typname": "entity.name.type.klarsatz",
    "zeichen": "punctuation.separator.klarsatz",
}


def regeln(buchstabe=r"\p{L}"):
    """Die Regelliste. `buchstabe`: Regex für einen Buchstaben ('\\p{L}' für TextMate/JavaScript, sonst Python-Form)."""
    B = buchstabe
    W = rf"{B}(?:{B}|\d|_)*"
    ci = lambda r: f"(?i:{r})"                                               # noqa: E731
    fuer = wort_regex("fuer")
    R = [
        (ci(r"anmerkung") + r"\s*:[^\n]*", "kommentar"),
        (r'"[^"\n]*"', "text"),
        (r"„[^“”\"\n]*[“”\"]".replace('\\"', '"'), "text"),
        (r"-?\d+(?:\.\d+)?", "zahl"),
        (rf"\b({ci('definiere')})(\s+)({ci('aufgabe')})(\s+)({W})", ["steuerung", None, "steuerung", None, "funktionsname"]),
        (rf"^(\s*)({W})(\s+)({ci('hat')})\b", [None, "typname", None, "operator"]),
        (rf"\b({ci(fuer)})(\s+)({ci('immer')})\b", ["steuerung", None, "operator"]),
        (rf"\b({ci(alternative(FUNKTIONEN_MIT_VON))})(?=\s+{ci('von')}\b)", "funktion"),
        (rf"\b({ci(wort_regex('wert'))})(?=\s+{ci(fuer)}\b)", "funktion"),
        (rf"\b({ci(wort_regex('element'))})(?=\s+(?:\d|\(|{ci('von')}\b|{W}\s+{ci('von')}\b))", "funktion"),
        (rf"\b({ci(alternative({'erste', 'letzte', 'zufaelliges', 'zufaellige'}))})(?=\s+{ci('element')}\b)", "funktion"),
        (rf"\b({ci('ein|eine|keine')})(\s+)({ci('zahl|text|liste|tabelle')})(?=\s+{ci('ist|sind')}\b)", ["operator", None, "typname"]),
        (rf"\b({ci('liste|tabelle')})(\s+)({ci('namens')})\b", ["typname", None, "operator"]),
        (rf"\b{ci(alternative(KONTROLLE))}\b", "steuerung"),
        (rf"\b{ci(alternative(ANWEISUNGEN))}\b", "anweisung"),
        (rf"\b{ci(alternative(BINDEWOERTER))}\b", "operator"),
        (rf"\b{ci(alternative(KONSTANTEN))}\b", "konstante"),
        (r"[.,:()]", "zeichen"),
    ]
    return R


# ── TextMate ────────────────────────────────────────────────────────────
def textmate_grammatik():
    muster = []
    for regex, bereiche in regeln(r"\p{L}"):
        eintrag = {"match": regex}
        if isinstance(bereiche, str):
            eintrag["name"] = TEXTMATE[bereiche]
        else:
            eintrag["captures"] = {str(i + 1): {"name": TEXTMATE[b]} for i, b in enumerate(bereiche) if b}
        muster.append(eintrag)
    return {"$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
            "name": "Klarsatz", "scopeName": "source.klarsatz", "fileTypes": ["klar"], "patterns": muster}


# ── JavaScript (für die Webseite) ─────────────────────────────────────────
def _fuer_js(regex):
    """JavaScript kennt weder '(?i:' noch ein Unicode-'\\b': am Wortanfang prüft der Tokenizer selbst,
    am Wortende ersetzt eine Vorausschau das '\\b'."""
    regex = regex.replace("(?i:", "(?:")
    if regex.startswith("\\b"):
        regex = regex[2:]
    return regex.replace("\\b", "(?![\\p{L}\\p{N}_])")


def js_regeln():
    """[{regex, bereiche}] – in JS mit den Flags 'imuy' verwenden (siehe playground/klarsatz-hervorhebung.js)."""
    return [{"regex": _fuer_js(r), "bereiche": b} for r, b in regeln(r"\p{L}")]


# ── Pygments ────────────────────────────────────────────────────────────
def pygments_lexer():
    from pygments.lexer import RegexLexer, bygroups
    from pygments.token import (Comment, Keyword, Name, Number, Operator, Punctuation, String, Text)
    tokens = {"kommentar": Comment.Single, "text": String.Double, "zahl": Number, "steuerung": Keyword,
              "anweisung": Keyword.Reserved, "funktion": Name.Builtin, "konstante": Keyword.Constant,
              "operator": Operator.Word, "funktionsname": Name.Function, "typname": Name.Class,
              "zeichen": Punctuation}
    regelliste = []
    for regex, bereiche in regeln(r"[^\W\d_]"):
        if isinstance(bereiche, str):
            regelliste.append((regex, tokens[bereiche]))
        else:
            regelliste.append((regex, bygroups(*[tokens[b] if b else Text for b in bereiche])))
    regelliste = [(r"\s+", Text)] + regelliste + [(rf"[^\W\d_](?:[^\W\d_]|\d|_)*", Name), (r".", Text)]

    class KlarsatzLexer(RegexLexer):
        name = "Klarsatz"
        aliases = ["klarsatz", "klar"]
        filenames = ["*.klar"]
        mimetypes = ["text/x-klarsatz"]
        flags = re.MULTILINE | re.UNICODE
        tokens = {"root": regelliste}

    return KlarsatzLexer
