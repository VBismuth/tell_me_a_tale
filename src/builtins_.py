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

from dataclasses import dataclass, field
from typing import (
    List, Dict, Union, Callable, Any,
    get_args as type_get_args
)
from sys import stdout, stderr

from . import TMT_VERSION
from .ast_ import (
    Constant, Variable, FunctionDefinition, Identifier,
    DataType, Literal
)
from .errors import TMTRuntimeError, error_print, warn_print


# !!START!!
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
            error_print("ERROR: TmtObjectsTrack: Could not add object of type",
                        str(type(obj)),
                        "to track. Expected:", str(type_get_args(TmtObject)))
            return False
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
            res = self.consts.pop(name) if name in self.consts else (
                self.variables.pop(name) if name in self.variables
                else (self.functions.pop(name) if name in self.functions
                      else None)
            )  # pop object
            self.names.pop(self.names.index(name))  # remove name
            return res
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

    def names_as_str(self) -> List[str]:
        """ Return list of names as str """
        return [ident.name for ident in self.names]

    def check_exists(self, name: Identifier | str) -> bool:
        """ Check if Identifier is already tracked """
        res = Identifier(name) if isinstance(name, str) else name
        return isinstance(res, Identifier) and res in self.names

    def is_constant(self, name: Identifier | str) -> bool:
        """ Check if there's a constant using this name """
        res = Identifier(name) if isinstance(name, str) else name
        return isinstance(res, Identifier) and res in self.consts

    def is_variable(self, name: Identifier | str) -> bool:
        """ Check if there's a variable using this name """
        res = Identifier(name) if isinstance(name, str) else name
        return isinstance(res, Identifier) and res in self.variables

    def is_function(self, name: Identifier | str) -> bool:
        """ Check if there's a function using this name """
        res = Identifier(name) if isinstance(name, str) else name
        return isinstance(res, Identifier) and res in self.functions

    def setup_builtins(self) -> None:
        """ Setup builtins to track """
        for defaults in (TMT_BUILTIN_CONSTS, TMT_BUILTIN_VARS):
            for name, obj in defaults.items():
                if self.check_exists(name):
                    warn_print(f'WARN: TmtObjectsTrack.setup: name "{name}" is'
                               ' already defined')
                    continue
                if not self.add(obj):
                    warn_print('WARN: TmtObjectsTrack.setup: couldn\'t add '
                               f'"{name}" to track')
                    continue


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


def builtin_print(file: str, *args: Any) -> TMTRuntimeError:
    """ Python print wrapper for TMT builtin PRINT """
    if not isinstance(file, str) or len(file) < 1:
        file = 'STDOUT'
    if file == "STDOUT":
        print(*args, file=stdout, end='', sep='')
    elif file == "STDERR":
        print(*args, file=stderr, end='', sep='')
    # TODO: check file in system, or make builtin_writefile/readfile
    else:
        raise NotImplementedError
    return TMTRuntimeError.OK


TMT_BUILTIN_FUNCS: Dict[str, Callable[..., TMTRuntimeError]] = {
    "PRINT": builtin_print,
}
