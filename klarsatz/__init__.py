"""Klarsatz – eine Programmiersprache, die wie Deutsch klingt."""
from .fehler import KlarsatzFehler, LaufzeitFehler, LimitFehler, SyntaxFehler
from .interpreter import Interpreter
from .lexer import lexer, norm
from .parser import Parser

__version__ = "0.10.0"
__all__ = ["Interpreter", "KlarsatzFehler", "LaufzeitFehler", "LimitFehler", "SyntaxFehler",
           "Parser", "lexer", "norm", "__version__"]
