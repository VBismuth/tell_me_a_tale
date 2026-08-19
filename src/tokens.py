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

""" Tokens for the TMT
Contains Pos and Token structures and TokenType enum
"""

from enum import Enum, auto as iota
from typing import Callable, Union, Optional, Type
from dataclasses import dataclass

from .text import Pos


# !!START!!
class TokenType(Enum):
    """ Tokey type """
    NONE        = 0
    COMMENT     = iota()
    IDENTIFIER  = iota()
    TYPES       = iota()
    STRING      = iota()
    METAKEY     = iota()
    NUMBER      = iota()
    EXPRESSION  = iota()
    RANGE       = iota()
    KEYWORD     = iota()
    LBRACE      = iota()
    RBRACE      = iota()
    LBRACKET    = iota()
    RBRACKET    = iota()
    LPAREN      = iota()
    RPAREN      = iota()
    EQUAL       = iota()
    NOTEQUAL    = iota()
    LESSTHAN    = iota()
    LESSEQUAL   = iota()
    GREATERTHAN = iota()
    GREATEQUAL  = iota()
    TERMINATOR  = iota()
    COMMA       = iota()
    COLON       = iota()
    WORD        = iota()

    COUNT       = iota()


@dataclass
class Token:
    """ Token structure """
    file: str
    start_pos: Pos
    end_pos: Pos
    type_: Enum = TokenType.NONE
    body: str = ''

    def __str__(self) -> str:
        if self.type_ == TokenType.NONE:
            return "[NONE]"
        if self.type_ == TokenType.COUNT:
            return "[NOT A TOKEN]"
        return (f"[{self.type_.name}:{self.body[:30]}" + ('<...>]'
                if len(self.body) >= 30 else ']'))

    def copy(self) -> Token:
        """ Copy self """
        return Token(
            file=self.file,
            start_pos=self.start_pos.copy(),
            end_pos=self.end_pos.copy(),
            type_=self.type_,
            body=self.body
        )


class ExpTokenType(Enum):
    """ Expression tokens """
    NONE    = 0
    PLUS    = iota()
    MINUS   = iota()
    MULT    = iota()
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


AnyTokenType = Union[TokenType, ExpTokenType]
AnyToken = Union[Token, ExpToken]


@dataclass
class TokenMeta:
    """ Token metadata """
    token_object: Type[AnyToken]  = Token
    token_type: Type[AnyTokenType] = TokenType
    clean_func: Optional[Callable[[AnyToken], None]] = None
