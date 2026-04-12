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
from dataclasses import dataclass

from .text import Pos


class TokenType(Enum):
    """ Tokey type """
    NONE        = 0
    COMMENT     = iota()
    IDENTIFIER  = iota()
    TYPES       = iota()
    STRING      = iota()
    EXPRESSION  = iota()
    KEYWORD     = iota()
    TERMINATOR  = iota()
    COLON       = iota()
    WORD        = iota()

    COUNT       = iota()


@dataclass
class Token:
    """ Token structure """
    filename: str
    start_pos: Pos
    end_pos: Pos
    type_: TokenType = TokenType.NONE
    body: str = ''

    def __str__(self) -> str:
        if self.type_ == TokenType.NONE:
            return "[NONE]"
        if self.type_ == TokenType.COUNT:
            return "[NOT A TOKEN]"
        return (f"[{self.type_.name}:{self.body[:30]}" + ('<...>]'
                if len(self.body) >= 30 else ']'))
