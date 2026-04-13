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
from typing import Generator

from .tokens import TokenType, Token
from .text import Text, Pos

# TODO: if common keyword used outside of context, like 'about' outside
# of 'tell me' then it should be connected to string
keywords = sorted((
    'this is', 'a tale', 'an actor', 'a constant', 'a pointer', 'a list',
    'a dict', 'of kind', 'of type', 'there was', 'there is', 'for ', 'in ',
    'about', 'in which', 'that is', 'become', 'and ', 'or ', 'not ',
    'say ', 'tell me', 'telling me', 'the meaning of', 'should listen to me',
    'if ', 'then ', 'otherwise', 'else', 'and that\'s it', 'equals', 'equal',
    'while', 'do ', 'until', 'repeat', 'so it begins', 'the end',
    'alias', 'as ', 'cast', 'append book', 'visit library', 'from ',
), key=len, reverse=True)

types = (
    'number', 'string', 'boolean', 'none',
)

# TODO: meta keywords like @LINKER -l:raylib.a
assert TokenType.COUNT.value == 15, "Nonexhaustive token handle"
token_patterns = {
    'COMMENT':    r'(?:-\([\s\S]*?\)-)|(?:--[^\n]*)',
    'IDENTIFIER': r'\"(?:[^\n](?:\\\")*)*?\"',
    'STRING':     r'`(?:[\s\S](?:\\`)*)*?`',
    'METAKEY':    r'@\w+',
    'ANYBRACE':   r'[\[\]\(\)\{\}]',
    'TYPES':      '(?:' + '|'.join(types) + r')(?:=[\w]+)?',
    'EXPRESSION': r'_[^\n]*?_',
    'NUMBER':     r'[+-]?[\d]+(?:\.[\d]+)?(?:e[+-]?\d+)?',
    'RANGE':      r'\.\.=?',
    'KEYWORD':    '|'.join(keywords),
    'TERMINATOR': '[.;]',
    'COMMA':      ',',
    'COLON':      ':',
    'WORD':       r'[-+=\w]+'
}

MULTIPATTERN: str = '|'.join(f'(?P<{name}>{ptrn})'
                             for name, ptrn in
                             token_patterns.items())


def tokenize(text: Text, pattern: str = MULTIPATTERN) -> Generator[Token]:
    """ Token generator from text """
    for match in re.finditer(pattern, text.text, re.IGNORECASE):
        tokenname: str = match.lastgroup or 'NONE'
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
