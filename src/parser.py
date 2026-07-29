# -*- coding: utf-8 -*-
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

""" Parser and symantic analazer for TMT """

from dataclasses import dataclass, field
from typing import List, Dict, Union, get_args as type_get_args
from enum import Enum, auto as iota
from sys import stderr, exit as sysexit

from .ast_ import (
    Identifier, Constant, Variable,
    FunctionDefinition, Program, Node
)
from .tokens import Token, TokenType
from .errors import error_print, warn_print
from .text import Text


# !!START!!
# TODO: for import purposes should form dependency tree for the IMPORT
TmtObject = Union[Constant, Variable, FunctionDefinition]


@dataclass
class TmtObjectsTrack:
    """ Tracks used TMT Objects """
    names: List[Identifier] =\
        field(default_factory=list)
    consts: Dict[Identifier, Constant] =\
        field(default_factory=dict)
    variables: Dict[Identifier, Variable] =\
        field(default_factory=dict)
    functions: Dict[Identifier, FunctionDefinition] =\
        field(default_factory=dict)

    def add(self, obj: TmtObject) -> bool:
        """ Add new object """
        if not isinstance(obj, type_get_args(TmtObject)):
            error_print("ERROR: parser: Could not add object of type",
                        str(type(obj)),
                        "to track. Expected:", str(type_get_args(TmtObject)))
            sysexit(1)
        if self.check_exists(obj.name):
            return False  # Return false if exists
        self.names.append(obj.name)
        if isinstance(obj, Constant):
            self.consts[obj.name] = obj
        elif isinstance(obj, Variable):
            self.variables[obj.name] = obj
        elif isinstance(obj, FunctionDefinition):
            self.functions[obj.name] = obj
        else:
            assert False, "Unreachable"
        return True

    def pop(self, name: Identifier | str) -> TmtObject | None:
        """ Checks if name exists and pops it out. Otherwise returns None"""
        name = Identifier(name) if isinstance(name, str) else name
        if self.check_exists(name):
            return self.consts.pop(name) if name in self.consts else (
                self.variables.pop(name) if name in self.variables
                else (self.functions.pop(name) if name in self.functions
                      else None)
            )
        return None

    def get(self, name: Identifier | str) -> TmtObject | None:
        """ Checks if name exists and returns it. Otherwise returns None"""
        name = Identifier(name) if isinstance(name, str) else name
        if self.check_exists(name):
            return self.consts.get(name) if name in self.consts else (
                self.variables.get(name) if name in self.variables
                else (self.functions.get(name) if name in self.functions
                      else None)
            )
        return None

    def check_exists(self, name: Identifier | str) -> bool:
        """ Check if Identifier is already tracked """
        res = Identifier(name) if isinstance(name, str) else name
        return isinstance(res, Identifier) and res in self.names


class ParseMode(Enum):
    """ Parser Modes to decide what to do """
    DEFAULT    = 0
    FUNCTION   = iota()
    EXPRESSION = iota()
    ARGUMENTS  = iota()


@dataclass
class ParserContext:
    """ Shared parser context """
    source: Text
    tokens: List[Token]
    pointer: int
    unmatched_braces: List[Token] = field(default_factory=list)
    mode: ParseMode = ParseMode.DEFAULT
    objects: TmtObjectsTrack = field(default_factory=TmtObjectsTrack)

    def get_token(self) -> Token | None:
        """ Returns current token if it exists """
        if not self.tokens:
            return None
        return self.tokens[self.pointer]

    def next(self, n: int = 1) -> Token | None:
        """ Move pointer and return previous n token
        if it exists, None otherwise """
        if self.pointer + n >= len(self.tokens):
            warn_print("WARN: ParserContext.next: Context next token "
                       "pointer out of boundaries for",
                       self.source.filename)
            return None
        self.pointer += n
        return self.get_token()

    def prev(self, n: int = 1) -> Token | None:
        """ Move pointer and return previous n token
        if it exists, None otherwise """
        if len(self.tokens) < self.pointer - n < 0:
            warn_print("WARN: ParserContext.prev: Context previous token "
                       "pointer out of boundaries for",
                       self.source.filename)
            return None
        self.pointer -= n
        return self.get_token()

    def reset_pointer(self) -> None:
        """ Reset pointer position to zero """
        self.pointer = 0

    def last(self) -> Token | None:
        """ Move pointer and return last token if it exists, None otherwise """
        if self.tokens:
            self.pointer = len(self.tokens) - 1
            return self.get_token()
        return None


def concatinate_words(ctx: ParserContext) -> Token:
    """ Concatinate words """
    tok: Token | None = ctx.get_token()
    if tok is None:
        sysexit("ERROR: parser.concatinate_words: got None for token, "
                f"expected word.\nContext: {ctx}")
    res: Token = tok.copy()
    res.type_ = TokenType.STRING
    tok = ctx.next()
    while tok and tok.type_ not in\
            (TokenType.COLON, TokenType.TERMINATOR):
        res.end_pos.update(tok.end_pos)
        res.body = ctx.source.get_slice(res.start_pos, res.end_pos)
        tok = ctx.next()
    return res


def process_keyword(ctx: ParserContext) -> Node:
    """ Process keyword """
    raise NotImplementedError


def parse(ctx: ParserContext) -> Program:
    """ Parse tokens """
    res = Program(
        filename=ctx.source.filename,
        filepath=ctx.source.filepath,
        body=[]
    )

    tok: Token | None = ctx.get_token()
    while tok:
        if tok.type_ == TokenType.WORD:
            concatinate_words(ctx)  # discard words
            continue
        if tok.type_ != TokenType.KEYWORD:
            tok = ctx.next()
            continue
        processed: Node = process_keyword(ctx)
        if isinstance(processed, type_get_args(Node)):
            res.body.append(processed)
        tok = ctx.next()
    return res
