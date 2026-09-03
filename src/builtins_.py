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

""" TMT Builtins """

from typing import Dict, Union, Callable, Any
from sys import stdout, stderr

from . import TMT_VERSION
from .ast_ import (
    Constant, Variable, FunctionDefinition, Identifier,
    DataType, Literal
)
from .errors import TMTRuntimeError


# !!START!!
TmtObject = Union[Constant, Variable, FunctionDefinition]

TMT_BUILTIN_CONSTS: Dict[str, Constant] = {
    "VERSION":          Constant(Identifier("VERSION"),
                                 DataType("text"),
                                 TMT_VERSION),
    "UNKNOWN ERROR":    Constant(Identifier("UNKNOWN ERROR"),
                                 DataType('number', 'u8'),
                                 '255'),
    "NO ERROR":         Constant(Identifier("NO ERROR"),
                                 DataType('number', 'u8'),
                                 '0'),
    "RUNTIME ERROR":    Constant(Identifier("RUNTIME ERROR"),
                                 DataType('number', 'u8'),
                                 '1'),
    "MATH ERROR":       Constant(Identifier("MATH ERROR"),
                                 DataType('number', 'u8'),
                                 '2'),
    "FILE READ ERROR":  Constant(Identifier("FILE READ ERROR"),
                                 DataType('number', 'u8'),
                                 '3'),
    "FILE WRITE ERROR": Constant(Identifier("FILE WRITE ERROR"),
                                 DataType('number', 'u8'),
                                 '4'),
    "MEMORY ERROR":     Constant(Identifier("MEMORY ERROR"),
                                 DataType('number', 'u8'),
                                 '5'),
}
TMT_BUILTIN_VARS: Dict[str, Variable] = {
    "SELF":            Variable(Identifier("SELF"),
                                DataType("text"),
                                "_BUILTIN_SELF"
                                ),
    "ERROR":           Variable(Identifier("ERROR"),
                                DataType("number", 'u8'),
                                '0'),
}

NOTHING: Literal = Literal('nothing', DataType())
NEWLINE: Literal = Literal('\n', DataType('text'))


def builtin_print(*args: Any, file: str = "STDOUT") -> TMTRuntimeError:
    """ Python print wrapper for TMT builtin PRINT """
    if file == "STDOUT":
        print(*args, file=stdout, end='', sep='')
    elif file == "STDERR":
        print(*args, file=stderr, end='', sep='')
    # TODO: check file in system, or make builtin_writefile/readfile
    elif file == "__TODO__":
        raise NotImplementedError
    else:
        assert False, "Unreachable"
    return TMTRuntimeError.OK


TMT_BUILTIN_FUNCS: Dict[str, Callable[..., TMTRuntimeError]] = {
    "PRINT": builtin_print,
}
