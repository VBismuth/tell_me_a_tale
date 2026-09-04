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

""" Interpreter functions for TMT """

from dataclasses import dataclass, field
from typing import List, Any, Tuple

from .text import Text, Pos
from .errors import error_message, TMTRuntimeError
from .ast_ import (
    Program, FunctionCall, Literal,
    DataType, Identifier, Pass, GetVar, Node,
    Variable, Constant,
)
from .typecheck import is_valid_type
from .builtins_ import TMT_BUILTIN_FUNCS, TmtObjectsTrack, TmtObject
from .utils import get_func_name, suggest_name, tmt_get_self, identifier_info


# !!START!!
@dataclass
class RuntimeContext:
    """ TMT runtime context """
    source: Text
    program: Program
    source_pos: Tuple[Pos, Pos]
    objects: TmtObjectsTrack = field(default_factory=TmtObjectsTrack)
    rerror: TMTRuntimeError = TMTRuntimeError.OK
    exiting: bool = False
    ret_code: int = 0

    @staticmethod
    def setup(source: Text, program: Program,
              *args: Any, **kwargs: Any) -> RuntimeContext:
        """ Setup new instance of runtime context """
        ctx: RuntimeContext = RuntimeContext(source, program,
                                             (Pos(), Pos()),
                                             *args, **kwargs)
        ctx.objects.setup_builtins()
        return ctx


def get_tmt_value(ctx: RuntimeContext, val: str, type_: DataType) -> Any:
    """ Get value """
    if type_.name == 'text':
        if val == '_BUILTIN_SELF':
            return tmt_get_self()
        res = val.replace(r'\\', '!!BACK_SLASH!!')
        escape_chars = {
            r'\a': '\a', r'\b': '\b', r'\f': '\f', r'\n': '\n',
            r'\r': '\r', r'\t': '\t', r'\v': '\v', r"\'": "'",
            r'\"': '"',
        }
        for fake_char, true_char in escape_chars.items():
            res = res.replace(fake_char, true_char)
        return res.replace('!!BACK_SLASH!!', '\\')
    if type_.name == 'number':
        return float(val) if type_.subtype is None or\
            type_.subtype.startswith('f') else int(val)
    if not is_valid_type(type_):
        error_message(
            *ctx.source_pos,
            ctx.source,
            f'Cannot get value of unknown type "{type_}"'
        )
        ctx.rerror = TMTRuntimeError.VALUEERR
    return None


def interp_expression(ctx: RuntimeContext,
                      expr: Node) -> Any:
    """ Process args for the builtin function """
    if isinstance(expr, Literal):
        return get_tmt_value(ctx, expr.value, expr.valtype)
    if isinstance(expr, (Identifier, GetVar)):
        if isinstance(expr, GetVar):
            target: Identifier = expr.target
            ctx.source_pos = expr.position
        else:
            target = expr
        obj: TmtObject | None = ctx.objects.get(target)
        if not obj:
            suggestion = suggest_name(target.name, ctx.objects.names_as_str())
            error_message(
                *ctx.source_pos,
                ctx.source,
                f'Unknown name {target.name!r}' +
                (f'. Did you mean {suggestion!r}?' if suggestion else '')
            )
            ctx.rerror = TMTRuntimeError.VALUEERR
            return None
        return (get_tmt_value(ctx, obj.value, obj.datatype)
                if isinstance(expr, GetVar) and
                isinstance(obj, (Variable, Constant))
                else identifier_info(target, ctx.objects))
    error_message(
        *ctx.source_pos,
        ctx.source,
        f'Unknown expression "{expr}"'
    )
    ctx.rerror = TMTRuntimeError.VALUEERR
    return None


def interp(ctx: RuntimeContext) -> TMTRuntimeError:
    """ Interprete program until the end or halt """
    for statement in ctx.program.body:
        if hasattr(statement, 'position'):
            ctx.source_pos = statement.position
        if ctx.rerror != TMTRuntimeError.OK or ctx.exiting:
            break
        if isinstance(statement, Pass):
            continue
        if isinstance(statement, FunctionCall) and\
                get_func_name(statement) in TMT_BUILTIN_FUNCS:
            # TODO: work with function returns
            args: List[Any] = [interp_expression(ctx, expr)
                               for expr in statement.args]
            if ctx.rerror != TMTRuntimeError.OK:
                break
            TMT_BUILTIN_FUNCS[get_func_name(statement)](*args)
        else:
            error_message(
                *ctx.source_pos,
                ctx.source,
                "ERROR: interpreter: unknown "
                f"statement {str(statement)!r}"
            )
            ctx.rerror = TMTRuntimeError.STATEMENTERR
    print(end='', flush=True)  # so builtin_print wont stay unflushed
    return ctx.rerror
