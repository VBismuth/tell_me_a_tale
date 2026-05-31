# -*- coding: utf8 -*-
#   Tell Me a Tale, a small story-like programming language.
#   Copyright (C) 2026  VBismuth <work.nicitons@yandex.ru>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" Expression handling for TMT
"""

from enum import Enum, auto as iota
from dataclasses import dataclass
from typing import Generator

from .text import Text
from .tokens import TokenMeta, Token
from .lexer import tokenize


# !!START!!
class ExpTokenType(Enum):
    """ Expression tokens """
    NONE    = 0
    PLUS    = iota()
    MINUS   = iota()
    MULTI   = iota()
    DIV     = iota()
    INTDIV  = iota()
    MOD     = iota()
    POW     = iota()
    LPAREN  = iota()
    RPAREN  = iota()
    NUMBER  = iota()
    IDENT   = iota()
    KEYWORD = iota()

    COUNT   = iota()


@dataclass
class ExpToken(Token):
    """ Token structure for expressions """
    type_: Enum = ExpTokenType.NONE

    def __str__(self) -> str:
        if self.type_ == ExpTokenType.NONE:
            return "<[NONE]>"
        if self.type_ == ExpTokenType.COUNT:
            return "<[NOT A TOKEN]>"
        return (f"<[{self.type_.name}:{self.body[:30]}" + ('<...>]>'
                if len(self.body) >= 30 else ']>'))


exp_token_patterns = {
    "PLUS":    r'\+',
    "MINUS":   r'\-',
    "MULT":    r'\+',
    "INTDIV":  r'\/\/',
    "DIV":     r'\/',
    "MOD":     r'\%',
    "POW":     r'\^',
    "LPAREN":  r'\(',
    "RPAREN":  r'\)',
    'NUMBER':  r'[+-]?[\d]+(?:\.[\d]+)?(?:e[+-]?\d+)?',
    "IDENT":   r'\$\"(?:[^\n](?:\\\")*)*?\"',
    "KEYWORD": r'[^\s\(\)]+',
}
assert ExpTokenType.COUNT.value == len(exp_token_patterns) + 1, \
    "Non-exhaustive token coverage for expressions"

EXPMULTIPATTERN: str = '|'.join(f'(?P<{name}>{ptrn})'
                                for name, ptrn in
                                exp_token_patterns.items())


def exp_clean(tok: ExpToken) -> None:
    """ Exp token fixing """
    if tok.type_ is ExpTokenType.IDENT:
        tok.body = tok.body[len('$"'):-len('"')]


def exp_tokenize(text: Text, pattern: str = EXPMULTIPATTERN,
                 meta: TokenMeta = TokenMeta(
                     token_object=ExpToken,
                     token_type=ExpTokenType,
                     clean_func=exp_clean
                 )) -> Generator[ExpToken]:
    """ Expression tokenizer from text using standart tokenizer """
    res: Generator[ExpToken] = tokenize(text, pattern, meta)
    assert isinstance(res, Generator), f"output is {str(type(res))}"
    return res
