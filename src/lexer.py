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
    'this is', 'that was', 'a tale', 'an actor', 'a constant', 'a pointer',
    'a list', 'a dict', 'of kind', 'of type', 'there was', 'there is', 'for',
    'in', 'about', 'in which', 'that is', 'become', 'and', 'or', 'not',
    'say ', 'tell me', 'telling me', 'the meaning of', 'should listen to me',
    'if', 'then', 'otherwise', 'else', 'that\'s it', 'self',
    'while', 'do ', 'until', 'repeat', 'so it begins', 'the end',
    'alias', 'as ', 'cast', 'append book', 'visit library', 'from ',
    'read from file', 'rewrite to file', 'append to file',
), key=len, reverse=True)
# TODO: >, =, etc... should't be part of KEYWORDS

types = (
    'number', 'string', 'boolean', 'none',
)

# TODO: meta keywords like @LINKER -l:raylib.a
assert TokenType.COUNT.value == 26, "Nonexhaustive token handle"
token_patterns = {
    'COMMENT':      r'(?:-\([\s\S]*?\)-)|(?:--[^\n]*)',
    'IDENTIFIER':   r'\"(?:[^\n](?:\\\")*)*?\"',
    'STRING':       r'`(?:[\s\S](?:\\`)*)*?`',
    'METAKEY':      r'@\w+',
    'TYPES':        '(?:' + '|'.join(types) + r')(?:=[\w]+)?',
    'EXPRESSION':   r'_[^\n]*?_',
    'NUMBER':       r'[+-]?[\d]+(?:\.[\d]+)?(?:e[+-]?\d+)?',
    'RANGE':        r'\.\.=?',
    'KEYWORD':      r'\s|'.join(keywords) + r'\s',
    'LBRACE':       r'\{',
    'RBRACE':       r'\}',
    'LBRACKET':     r'\[',
    'RBRACKET':     r'\]',
    'LPAREN':       r'\(',
    'RPAREN':       r'\)',
    'EQUAL':        r'equal to|equals|same as|=',
    'NOTEQUAL':     r'not equal|doesn\'t equal|does not equal|!=|<>',
    'LESSTHAN':     r'less than|smaller than|lower than|<',
    'LESSEQUAL':    r'less or equal to|smaller '
                    'or equal to|lower or equal to|<=',
    'GREATERTHAN':  r'greater than|bigger than|higher than|>',
    'GREATEQUAL':   r'greater or equal to|bigger '
                    'or equal to|higher or equal to|>=',
    'TERMINATOR':   '[.;]',
    'COMMA':        ',',
    'COLON':        ':',
    'WORD':         r'[^\s\.,;]+'
}

MULTIPATTERN: str = '|'.join(f'(?P<{name}>{ptrn})'
                             for name, ptrn in
                             token_patterns.items())


def clean_token(text: Text, tok: Token) -> None:
    """ Clean token body from usless chars """
    match tok.type_:
        case TokenType.KEYWORD:
            body: str = re.sub(r'[\s]+$', '', tok.body)
            new_idx: int = tok.end_pos.index - (len(tok.body) - len(body))
            tok.end_pos.update(
                Pos(
                    *text.get_pos(new_idx, ignore_current_idx=True),
                    new_idx
                )
            )
            tok.body = body
        case TokenType.STRING:
            tok.body = tok.body.strip('`')
        case TokenType.EXPRESSION:
            tok.body = tok.body.strip('_')
        case TokenType.IDENTIFIER:
            tok.body = tok.body.strip('"')


# TODO: fix tokens for keywords
def tokenize(text: Text, pattern: str = MULTIPATTERN) -> Generator[Token]:
    """ Token generator from text """
    for match in re.finditer(pattern, text.text, re.IGNORECASE):
        tokenname: str = match.lastgroup or 'NONE'
        body: str = match.group(tokenname)
        idx_start, idx_end = match.span(tokenname)
        pos_start: Pos = Pos(*text.get_pos(idx_start), idx_start)
        pos_end: Pos = Pos(*text.get_pos(idx_end), idx_end)
        text.set_pos(idx_end)

        tok: Token = Token(
            start_pos=pos_start,
            end_pos=pos_end,
            filename=text.filename,
            body=body,
            type_=getattr(TokenType, tokenname) or TokenType.NONE
        )
        clean_token(text, tok)
        if tok.type_ is TokenType.WORD and tok.body in keywords:
            tok.type_ = TokenType.KEYWORD
        yield tok
