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
from typing import Callable, Any
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
    filename: str
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


@dataclass
class TokenMeta:
    """ Token metadata """
    token_object: type[Any]  = Token
    token_type: type[Any] = TokenType
    clean_func: Callable[[Any], None] | None = None
