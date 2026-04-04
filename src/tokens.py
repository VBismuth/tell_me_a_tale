# -*- Encoding: utf-8 -*-
""" Tokens for the TMT
Contains Pos and Token structures and TokenType enum
"""

from enum import Enum, auto as iota
from dataclasses import dataclass


@dataclass
class Pos:
    """ Positon in text """
    line: int = 1
    column: int = 1


class TokenType(Enum):
    """ Tokey type """
    NONE = 0
    COMMENT = iota()
    KEYWORD = iota()
    MATH = iota()
    STRING = iota()
    TERMINATOR = iota()

    COUNT = iota()


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
        return (f"[{self.type_.name}:{self.body[:30]}" + '<...>]'
                if len(self.body) >= 30 else ']')
