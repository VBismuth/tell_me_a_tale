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
from typing import (
    List, Dict, get_args as type_get_args,
    cast as type_cast)
from sys import exit as sysexit

from .ast_ import (
    Identifier, Constant, Variable,
    DataType, Literal, Pass,
    FunctionDefinition, FunctionCall,
    Program, Node, Expression,
    Statement, GetVar
)
from .tokens import Token, TokenType
from .errors import error_print, warn_print, token_error, ParseError
from .text import Text, Pos
from .utils import suggest_name
from .builtins_ import (
    TmtObjectsTrack, TmtObject, NOTHING, NEWLINE
)


# !!START!!
# TODO: for import purposes should form dependency tree for the IMPORT
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

    def next_token(self, n: int = 1) -> Token | None:
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

    def prev_token(self, n: int = 1) -> Token | None:
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

    def last_token(self) -> Token | None:
        """ Move pointer and return last token if it exists, None otherwise """
        if self.tokens:
            self.pointer = len(self.tokens) - 1
            return self.get_token()
        return None

    def eof(self) -> None:
        """ Move pointer to the end of token list to stop iteration """
        self.pointer = len(self.tokens)

    @staticmethod
    def setup(source: Text, tokens: List[Token]) -> ParserContext:
        """ Setup default parser context """
        ctx = ParserContext(source, tokens)
        ctx.objects.setup_builtins()
        return ctx


def concatinate_words(ctx: ParserContext) -> Token:
    """ Concatinate words """
    tok: Token | None = ctx.get_token()
    if tok is None:
        sysexit("ERROR: parser.concatinate_words: got None for token, "
                f"expected word.\nContext: {ctx}")
    res: Token = tok.copy()
    res.type_ = TokenType.STRING
    tok = ctx.next_token()
    comments: List[Token] = []
    while tok and tok.type_ not in\
            (TokenType.COMMA, TokenType.TERMINATOR,
             TokenType.COLON, ):
        if tok.type_ is TokenType.COMMENT:
            comments.append(tok)
            tok = ctx.next_token()
            continue
        res.end_pos.update(tok.end_pos)
        res.body = ctx.source.get_slice(res.start_pos, res.end_pos)
        tok = ctx.next_token()
    # Clean comments out of the string
    for comm in comments:
        res.body = res.body.replace(comm.body, '')
    return res


def process_expression(ctx: ParserContext) -> None:
    """ Process expression """
    raise NotImplementedError


def fn_the_meaning_of(ctx: ParserContext) -> Expression:
    """ Process 'the meaning of' statement """
    tok: Token | None = ctx.get_token()
    assert tok is not None, "exprected the `meaning of`, but got None"
    start_pos: Pos = tok.start_pos
    end_pos: Pos = tok.end_pos
    tok = ctx.next_token()
    if tok is None:
        error_print('ERROR: fn_the_meaning_of: got None')
        ctx.perror = ParseError.TOKENERR
        ctx.eof()
        return NOTHING
    if tok.type_ != TokenType.IDENTIFIER:
        token_error(tok, ctx.source, '`The meaning of` expected argument'
                    f' of type `IDENTIFIER` but got `{tok.type_.name}`')
        ctx.perror = ParseError.SYNTAXERR
        return NOTHING
    if not ctx.objects.check_exists(tok.body):
        suggestion: str | None = suggest_name(
            tok.body,
            ctx.objects.names_as_str()
        )
        token_error(tok, ctx.source, f'Name "{tok.body}" is not defined' +
                    (f'. Did you mean "{suggestion}"?' if suggestion else ''))
        ctx.perror = ParseError.SYNTAXERR
        return NOTHING
    if ctx.objects.is_constant(tok.body):
        obj: TmtObject | None = ctx.objects.get(tok.body)
        assert isinstance(obj, Constant), \
            f"Expected constant, but got {type(obj)!r}"
        return Literal(obj.value, obj.datatype)
    end_pos = tok.end_pos
    return GetVar(position=(start_pos, end_pos), target=Identifier(tok.body))


def process_args(ctx: ParserContext) -> List[Expression]:
    """ Process secondary keywords, literals or expressions as
        the arguments for the operators """
    res: List[Expression] = []
    tok: Token | None = ctx.get_token()
    assert tok is not None, "ERROR: process_args: expected token, got None"
    if tok.body.lower() == 'the meaning of':
        res.append(fn_the_meaning_of(ctx))
    elif tok.type_ == TokenType.WORD:
        res.append(Literal(
            concatinate_words(ctx).body,
            DataType('text')
        ))
    elif tok.type_ == TokenType.STRING:
        res.append(Literal(tok.body, DataType('text')))
    elif tok.type_ == TokenType.IDENTIFIER:
        res.append(Identifier(tok.body))
    else:
        token_error(tok, ctx.source,
                    f'Unexpected keyword, literal or expression: {str(tok)}')
        ctx.perror = ParseError.SYNTAXERR
        ctx.eof()
        return res
    return res


def fn_tell_print(ctx: ParserContext, output: str | Identifier) -> Node:
    """ Process 'tell' or 'say' printing statements """
    res: Node = Pass()
    tok: Token | None = ctx.get_token()
    assert tok is not None, "ERROR: fn_tell_print: expected token, got None"
    fn_root: Token = tok
    res = FunctionCall((tok.start_pos, tok.end_pos),
                       Identifier("PRINT"), [])
    if output == 'stdout':
        res.args.append(Literal('STDOUT', DataType('text')))
    elif output == 'stderr':
        res.args.append(Literal('STDERR', DataType('text')))
    elif output == 'ident':
        tok = ctx.next_token()
        if not tok:
            token_error(fn_root, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected identifier argument but got nothing")
            ctx.perror = ParseError.SYNTAXERR
            ctx.eof()
            return Pass()
        if tok.type_ != TokenType.IDENTIFIER:
            token_error(tok, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected [IDENTIFIER] argument but got "
                        f"[{tok.type_.name}]")
            ctx.perror = ParseError.SYNTAXERR
            ctx.eof()
            return Pass()
        res.args.append(GetVar(
            (tok.start_pos, tok.end_pos),
            Identifier(tok.body)))
        res.position = (res.position[0], tok.end_pos)
    elif output == 'path':
        tok = ctx.next_token()
        if not tok:
            token_error(fn_root, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected path argument but got nothing")
            ctx.perror = ParseError.SYNTAXERR
            ctx.eof()
            return Pass()
        if tok.type_ == TokenType.WORD:
            tok = concatinate_words(ctx)
        if tok.type_ != TokenType.STRING:
            token_error(tok, ctx.source,
                        f"ERROR: `{fn_root.body}` "
                        "expected [STRING] argument but got "
                        f"[{tok.type_.name}]")
            ctx.perror = ParseError.SYNTAXERR
            ctx.eof()
            return Pass()
        res.args.append(Literal(value=tok.body, valtype=DataType('text')))
        res.position = (res.position[0], tok.end_pos)
    else:
        error_print('ERROR: fn_tell_print: Unknown output '
                    f'parameter `{output}`, expected `stdout`, '
                    '`stderr`, `ident` or `path`')
        ctx.perror = ParseError.PARAMETERERR
        ctx.eof()
        return Pass()
    tok = ctx.next_token()
    while tok and tok.type_ not in (TokenType.TERMINATOR,):
        if not tok:
            break
        res.args += process_args(ctx)  # TODO: complete
        res.position = (res.position[0], (ctx.get_token() or tok).end_pos)
        tok = ctx.next_token()
    return res


def process_statements(ctx: ParserContext) -> Node:
    """ Process primary keywords to create statements """
    tok: Token | None = ctx.get_token()
    res: Node = Pass()
    if tok is None:
        error_print("ERROR: parser: process_keyword "
                    "got None.\nContext:", str(ctx))
        ctx.perror = ParseError.TOKENERR
        ctx.eof()
        return res
        # sysexit(1)
    if tok.body.lower() == "say":
        res = fn_tell_print(ctx, 'stdout')
        if not isinstance(res, FunctionCall):
            return res
        res.args.append(NEWLINE)

    elif tok.body.lower() == "tell me":
        res = fn_tell_print(ctx, 'stdout')
    elif tok.body.lower() == "tell error":
        res = fn_tell_print(ctx, 'stderr')
    elif tok.body.lower() == "tell":
        tok = ctx.next_token()
        ctx.prev_token()
        if tok and tok.type_ == TokenType.IDENTIFIER:
            res = fn_tell_print(ctx, 'ident')
        else:
            res = fn_tell_print(ctx, 'path')
    else:
        token_error(tok, ctx.source,
                    f"Unexpected keyword '{tok.body}'")
        # sysexit(1)
        ctx.perror = ParseError.SYNTAXERR
        ctx.eof()
    tok = ctx.last_token() if not ctx.get_token() else ctx.get_token()
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
            tok = ctx.next_token()
            continue
        if tok.type_ != TokenType.KEYWORD:
            tok = ctx.next_token()
            continue
        processed: Node = process_statements(ctx)
        if isinstance(processed, type_get_args(Node)):
            res.body.append(processed)
        tok = ctx.next_token()
    if not res.body:
        res.body = [Pass()]
    return res
