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

from .tokens import (
    TokenType, Token,
    ExpTokenType, ExpToken,
    AnyToken,
    TokenMeta
)
from .text import Text, Pos

# !!START!!
keywords = (
    'should listen to me', 'rewrite to file', 'the meaning of',
    'read from file', 'append to file', 'visit library', 'so it begins',
    'append book', 'a constant', 'telling me', 'a pointer', 'there was',
    'otherwise', "that's it", 'that was', 'an actor', 'there is', 'in which',
    'this is', 'of kind', 'of type', 'that is', 'tell me', 'the end',
    'a tale', 'a list', 'a dict', 'become', 'repeat', 'about', 'while',
    'until', 'alias', 'from ', 'say ', 'then', 'else', 'self', 'cast',
    'for', 'and', 'not', 'do', 'as', 'in', 'or', 'if'
)

types = (
    'number', 'string', 'boolean', 'none',
)

# TODO: meta keywords like @LINKER -l:raylib.a
token_patterns = {
    'COMMENT':      r'(?:-\([\s\S]*?\)-)|(?:--[^\n]*)',
    'IDENTIFIER':   r'\"(?:[^\n](?:\\\")*)*?\"',
    'STRING':       r'`(?:[\s\S](?:\\`)*)*?`',
    'METAKEY':      r'@\w+',
    'TYPES':        '(?:' + '|'.join(types) + r')(?:=[\w]+)?',
    'EXPRESSION':   r'_[^\n]*?_',
    'NUMBER':       r'[+-]?[\d]+(?:\.[\d]+)?(?:e[+-]?\d+)?',
    'RANGE':        r'\.\.=?',
    'KEYWORD':      r'\b' + r'\b|'.join(keywords) + r'\b',
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
assert TokenType.COUNT.value == len(token_patterns) + 1, \
    "Nonexhaustive token handle"

MULTIPATTERN: str = '|'.join(f'(?P<{name}>{ptrn})'
                             for name, ptrn in
                             token_patterns.items())

exp_token_patterns = {
    "PLUS":    r'\+',
    "MINUS":   r'\-',
    "MULT":    r'\*',
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


def exp_clean(tok: AnyToken) -> None:
    """ Exp token fixing """
    assert isinstance(tok, ExpToken), \
        f'exp_clean encounter wrong type "{type(tok)}", '\
        '"ExpToken" expected'
    if tok.type_ is ExpTokenType.IDENT:
        tok.body = tok.body[len('$"'):-len('"')]


def clean_token(tok: AnyToken) -> None:
    """ Clean token body from usless chars
    and correct unresolved keywords"""
    assert isinstance(tok, Token), \
        f'clean_token encounter wrong type "{type(tok)}", '\
        '"Token" expected'
    match tok.type_:
        case TokenType.KEYWORD:
            body: str = re.sub(r'[\s]+$', '', tok.body)
            tok.body = body
        case TokenType.STRING:
            tok.body = tok.body.strip('`')
        case TokenType.EXPRESSION:
            tok.body = tok.body.strip('_')
        case TokenType.IDENTIFIER:
            tok.body = tok.body.strip('"')

    if tok.type_ is TokenType.WORD and tok.body in keywords:
        tok.type_ = TokenType.KEYWORD


def tokenize(text: Text, pattern: str = MULTIPATTERN,
             meta: TokenMeta = TokenMeta(
                 clean_func=clean_token),
             text_offset: int = 0,
             tokenize_expr: bool = True) -> Generator[AnyToken]:
    """ Token generator from text """
    for match in re.finditer(pattern, text.text, re.IGNORECASE):
        tokenname: str = match.lastgroup or 'NONE'
        body: str = match.group(tokenname)
        idx_start, idx_end = match.span(tokenname)
        idx_start += text_offset
        idx_end += text_offset
        pos_start: Pos = Pos(*text.get_pos(idx_start), idx_start)
        pos_end: Pos = Pos(*text.get_pos(idx_end), idx_end)
        text.set_pos(idx_end)
        if tokenname == 'EXPRESSION' and tokenize_expr:
            body = body.strip('_')
            exp_text: Text = Text(
                text=body,
                current_pos=Pos()
            )
            exp_meta: TokenMeta = TokenMeta(
                token_object=ExpToken,
                token_type=ExpTokenType,
                clean_func=exp_clean,
            )
            yield from tokenize(
                exp_text,
                meta=exp_meta,
                pattern=EXPMULTIPATTERN,
                text_offset=idx_start + 1,
            )
        else:
            tok: AnyToken = meta.token_object(
                start_pos=pos_start,
                end_pos=pos_end,
                filename=text.filename,
                body=body,
                type_=(getattr(meta.token_type, tokenname) or
                       meta.token_type.NONE)
            )
            if callable(meta.clean_func):
                meta.clean_func(tok)
            yield tok


def exp_tokenize(text: Text, pattern: str = EXPMULTIPATTERN,
                 meta: TokenMeta = TokenMeta(
                     token_object=ExpToken,
                     token_type=ExpTokenType,
                     clean_func=exp_clean,
                 ), text_offset: int = 0) -> Generator[ExpToken]:
    """ Token generator for expressions from text """
    for tok in tokenize(text, pattern, meta, text_offset, False):
        assert isinstance(tok, ExpToken), \
            f'exp_tokenizer encounter a wrong type "{type(tok)}", '\
            '"ExpToken" expected'
        yield tok
