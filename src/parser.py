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
from sys import exit as sysexit

from .ast_ import (
    Identifier, Constant, Variable,
    DataType, Literal, Pass,
    FunctionDefinition, FunctionCall,
    Program, Node,
)
from .tokens import Token, TokenType
from .errors import error_print, warn_print, token_error
from .text import Text
from . import TMT_SELF, TMT_VERSION


# !!START!!
# TODO: for import purposes should form dependency tree for the IMPORT
TmtObject = Union[Constant, Variable, FunctionDefinition]
SELF_ID_HEX: str = '212153454c462121'

TMT_DEFAULT_CONSTS: Dict[Identifier, Constant] = {
    Identifier("VERSION"): Constant(Identifier("VERSION"),
                                    DataType("text"),
                                    TMT_VERSION),
}
TMT_DEFAULT_VARS: Dict[Identifier, Variable] = {
    Identifier("SELF"):    Variable(Identifier("SELF"),
                                    DataType("text"),
                                    TMT_SELF.replace(
                                        bytes.fromhex(SELF_ID_HEX)\
                                             .decode('utf8'),
                                        TMT_SELF.replace("\\", r"\\")\
                                                .replace("'", "\\'"))
                                    ),
    Identifier("ERROR"):   Variable(Identifier("ERROR"),
                                    DataType("number", 'u8'),
                                    '0'),
}


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


class ParseError(Enum):
    """ Parser Modes to decide what to do """
    OK           = 0
    TOKENERR     = iota()
    SYNTAXERR    = iota()
    PARAMETERERR = iota()


@dataclass
class ParserContext:
    """ Shared parser context """
    source: Text
    tokens: List[Token]
    pointer: int = 0
    unmatched_braces: List[Token] = field(default_factory=list)
    perror: ParseError = ParseError.OK
    objects: TmtObjectsTrack = field(default_factory=TmtObjectsTrack)

    def get_token(self) -> Token | None:
        """ Returns current token if it exists """
        if not self.tokens or self.pointer >= len(self.tokens):
            return None
        return self.tokens[self.pointer]

    def next(self, n: int = 1) -> Token | None:
        """ Move pointer and return previous n token
        if it exists, None otherwise """
        if self.pointer + n >= len(self.tokens):
            # warn_print("WARN: ParserContext.next: Context next token "
            #            "pointer out of boundaries for",
            #            self.source.file)
            self.pointer = len(self.tokens)
            return None
        self.pointer += n
        return self.get_token()

    def prev(self, n: int = 1) -> Token | None:
        """ Move pointer and return previous n token
        if it exists, None otherwise """
        if len(self.tokens) < self.pointer - n < 0:
            # warn_print("WARN: ParserContext.prev: Context previous token "
            #            "pointer out of boundaries for",
            #            self.source.file)
            self.pointer = 0
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

    def end(self) -> None:
        """ Move pointer to the end of token list to stop iteration """
        self.pointer = len(self.tokens)


def concatinate_words(ctx: ParserContext) -> Token:
    """ Concatinate words """
    tok: Token | None = ctx.get_token()
    if tok is None:
        sysexit("ERROR: parser.concatinate_words: got None for token, "
                f"expected word.\nContext: {ctx}")
    res: Token = tok.copy()
    res.type_ = TokenType.STRING
    tok = ctx.next()
    comments: List[Token] = []
    while tok and tok.type_ not in\
            (TokenType.COMMA, TokenType.TERMINATOR,
             TokenType.COLON, ):
        if tok.type_ is TokenType.COMMENT:
            comments.append(tok)
            tok = ctx.next()
            continue
        res.end_pos.update(tok.end_pos)
        res.body = ctx.source.get_slice(res.start_pos, res.end_pos)
        tok = ctx.next()
    # Clean comments out of the string
    for comm in comments:
        res.body = res.body.replace(comm.body, '')
    print(res.body)
    return res


def process_expression(ctx: ParserContext) -> None:
    """ Process expression """
    raise NotImplementedError


def process_args(ctx: ParserContext) -> Node:
    """ Process secondary keywords, literals or expressions as
        the arguments for the operators """
    raise NotImplementedError


def fn_tell_print(ctx: ParserContext, output: str | Identifier) -> Node:
    """ Process 'tell' or 'say' printing statements """
    res: Node = Pass()
    tok: Token | None = ctx.get_token()
    assert tok is not None, "ERROR: fn_tell_print: expected token, got None"
    fn_root: Token = tok
    res = FunctionCall((tok.start_pos, tok.end_pos),
                       Identifier("PRINT"), [])
    if output == 'stdout':
        res.args.append(Identifier('STDOUT'))
    elif output == 'stderr':
        res.args.append(Identifier('STDERR'))
    elif output == 'ident':
        tok = ctx.next()
        if not tok:
            token_error(fn_root, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected identifier argument but got nothing")
            ctx.perror = ParseError.SYNTAXERR
            ctx.end()
            return Pass()
        if tok.type_ != TokenType.IDENTIFIER:
            token_error(tok, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected [IDENTIFIER] argument but got "
                        f"[{tok.type_.name}]")
            ctx.perror = ParseError.SYNTAXERR
            ctx.end()
            return Pass()
        res.args.append(Identifier(tok.body))
        res.position = (res.position[0], tok.end_pos)
    elif output == 'path':
        tok = ctx.next()
        if not tok:
            token_error(fn_root, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected path argument but got nothing")
            ctx.perror = ParseError.SYNTAXERR
            ctx.end()
            return Pass()
        if tok.type_ == TokenType.WORD:
            tok = concatinate_words(ctx)
        if tok.type_ != TokenType.STRING:
            token_error(tok, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected [STRING] argument but got "
                        f"[{tok.type_.name}]")
            ctx.perror = ParseError.SYNTAXERR
            ctx.end()
            return Pass()
        res.args.append(Literal(value=tok.body, valtype=DataType('text')))
        res.position = (res.position[0], tok.end_pos)
    else:
        error_print('ERROR: fn_tell_print: Unknown output '
                    f'parameter `{output}`, expected `stdout`, '
                    '`stderr`, `ident` or `path`')
        ctx.perror = ParseError.PARAMETERERR
        ctx.end()
        return Pass()
    tok = ctx.next()
    while tok and tok.type_ not in (TokenType.TERMINATOR,):
        if not tok:
            break
        token_error(tok, ctx.source,
                    f"Unexpected `{fn_root.body}` argument "
                    f"'{str(tok)}'")
        ctx.perror = ParseError.SYNTAXERR
        # res.args += process_args(ctx)  # TODO: implement
        tok = ctx.next()
    return res


def process_statements(ctx: ParserContext) -> Node:
    """ Process primary keywords to create statements """
    tok: Token | None = ctx.get_token()
    res: Node = Pass()
    if tok is None:
        error_print("ERROR: parser: process_keyword "
                    "got None.\nContext:", str(ctx))
        ctx.perror = ParseError.TOKENERR
        return res
        # sysexit(1)
    if tok.body == "Say":
        res = fn_tell_print(ctx, 'stdout')
        if not isinstance(res, FunctionCall):
            return res
        res.args.append(Literal('\n', DataType('text')))

    elif tok.body == "Tell me":
        res = fn_tell_print(ctx, 'stdout')
    elif tok.body == "Tell error":
        res = fn_tell_print(ctx, 'stderr')
    elif tok.body == "Tell":
        tok = ctx.next()
        ctx.prev()
        if tok and tok.type_ == TokenType.IDENTIFIER:
            res = fn_tell_print(ctx, 'ident')
        else:
            res = fn_tell_print(ctx, 'path')
    else:
        token_error(tok, ctx.source,
                    f"Unexpected keyword '{tok.body}'")
        # sysexit(1)
        ctx.perror = ParseError.SYNTAXERR
        ctx.end()
    tok = ctx.last() if not ctx.get_token() else ctx.get_token()
    assert tok is not None, \
        "Expected token to exists, but got none."\
        f"Context: {ctx}"

    if tok.type_ != TokenType.TERMINATOR:
        token_error(tok, ctx.source,
                    "Expected . or ; at the end")
        ctx.perror = ParseError.SYNTAXERR
    return res
    # TODO: Complete


def parse(ctx: ParserContext) -> Program:
    """ Parse tokens """
    res = Program(
        file=ctx.source.file,
        body=[]
    )

    tok: Token | None = ctx.get_token()
    while tok:
        if tok.type_ == TokenType.WORD:
            concatinate_words(ctx)  # discard words
            tok = ctx.next()
            continue
        if tok.type_ != TokenType.KEYWORD:
            tok = ctx.next()
            continue
        processed: Node = process_statements(ctx)
        if isinstance(processed, type_get_args(Node)):
            res.body.append(processed)
        tok = ctx.next()
    if not res.body:
        res.body = [Pass()]
    return res
