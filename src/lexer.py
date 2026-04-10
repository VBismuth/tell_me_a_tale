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

""" Lexer for the TMT """

import re
from dataclasses import dataclass

from tokens import TokenType, Token, Pos

# TODO: if common keyword used outside of context, like 'about' outside
# of 'tell me' then it should be connected to string
keywords = (
    'this is', 'a tale', 'an actor', 'a constant', 'a pointer', 'a list',
    'a dict', 'of kind', 'of type', 'there was', 'there is', 'for ',
    'about', 'in which', 'that is', 'become', 'and ', 'or ', 'not ',
    'say ', 'tell me', 'telling me', 'the meaning of', 'should listen to me',
    'if ', 'then ', 'otherwise', 'else', 'and that\'s it', 'equals', 'equal',
    'while', 'do ', 'until', 'repeat', 'so it begins', 'the end',
    'alias', 'as ', 'cast', 'append book', 'visit library', 'from ',
)

types = (
    'number', 'string', 'boolean', 'none',
)

# TODO: meta keywords like @LINKER -l:raylib.a
assert TokenType.COUNT.value == 10, "Nonexhaustive token handle"
token_patterns = {
    'COMMENT':    r'(?:-\([\s\S]*?\)-)|(?:--[^\n]*)',
    'IDENTIFIER': r'\"[^\n]*?\"',
    'STRING':     r'`[\s\S]*?`',
    'TYPES':      '(?:' + '|'.join(types) + r')(?:=[\w]+)?',
    'EXPRESSION': r'_[^\n]*?_',
    'KEYWORD':    '|'.join(keywords),
    'TERMINATOR': '[.;]',
    'COLON':      ',',
    'WORD':       r'[\w]+'
}

MULTIPATTERN: str = '|'.join(f'(?P<{name}>{ptrn})'
                             for name, ptrn in
                             token_patterns.items())


@dataclass
class Text:
    """ Text structure """
    current_pos: Pos
    text: str
    filename: str = '<string>'

    def get_pos(self, idx: int = 0) -> tuple[int, int]:
        """ Gets text pos by index """
        line: int = self.current_pos.line
        col: int = self.current_pos.column
        if self.current_pos.index == 0 or self.current_pos.index > idx:
            pointer: int = 0
            line = 1
            col = 1
        else:
            pointer: int = self.current_pos.index
        line += self.text.count('\n', pointer, idx)
        if line == self.current_pos.line:
            col += max(idx - pointer, 0)
        else:
            col = max(idx - self.text.rfind('\n', pointer, idx), 1)
        return (line, col)

    def set_pos(self, idx: int = 0) -> None:
        """ Sets pos by index idx """
        line, col = self.get_pos(idx)
        self.current_pos.index = idx
        self.current_pos.line = line
        self.current_pos.column = col

    def get_line(self, line_n: int = 1) -> str:
        """ Get line from text """
        if not self.text:
            return ''
        return self.text.split('\n')[max(line_n - 1, 0)]


def tokenize(text: Text, pattern: str = MULTIPATTERN) -> Token:
    """ Token generator from text """
    for match in re.finditer(pattern, text.text, re.IGNORECASE):
        tokenname: str = match.lastgroup
        body: str = match.group(tokenname)
        idx_start, idx_end = match.span(tokenname)
        pos_start: Pos = Pos(*text.get_pos(idx_start), idx_start)
        pos_end: Pos = Pos(*text.get_pos(idx_end), idx_end)
        text.set_pos(idx_end)

        yield Token(
            start_pos=pos_start,
            end_pos=pos_end,
            filename=text.filename,
            body=body,
            type_=getattr(TokenType, tokenname) or TokenType.NONE
        )
