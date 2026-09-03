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

""" Some utils for the TMT """

from difflib import get_close_matches
from typing import List
from pathlib import Path
from sys import exit as sysexit

from . import TMT_SELF
from .errors import error_print
from .ast_ import FunctionCall, FunctionDefinition, Identifier
from .builtins_ import TmtObject, TmtObjectsTrack


# !!START!!
SELF_ID_HEX: str = '212153454c462121'


def suggest_name(name: str, list_names: List[str]) -> str | None:
    """ Find the closest match of name in list_names if it exists,
        None otherwise """
    matches: List[str] = get_close_matches(name, list_names, n=1, cutoff=0.5)
    return matches[0] if matches else None


def tmt_get_self() -> str:
    """ Get full TMT sourcecode """
    return TMT_SELF.replace(
        bytes.fromhex(SELF_ID_HEX)\
             .decode('utf8'),
        TMT_SELF.replace("\\", r"\\")\
                .replace("'", "\\'"))


def check_tmt_file(app_name: str, filename: str,
                   allow_ast: bool = True) -> Path:
    """ Check if filename is a valid tmt file and returns Path object """
    file = Path(filename).resolve()
    suffixes = ('.tmt', '.ast.json') if allow_ast else ('.tmt',)
    if not file.exists():
        error_print(f'ERROR: {app_name}: File {filename!r} not found')
        sysexit(-1)
    if not file.is_file():
        error_print(f'ERROR: {app_name}: {filename!r} is not a file')
        sysexit(-1)
    if not any(file.name.endswith(suffix) for suffix in suffixes):
        error_print(f'ERROR: {app_name}: expected <file>.tmt' +
                    (' or <file>.ast.json,' if allow_ast else ','),
                    f'got {filename!r}')
        sysexit(-1)
    return file


def get_func_name(fn: FunctionCall | FunctionDefinition) -> str:
    """ Get TMT function name as str """
    return fn.name.name


def identifier_info(ident: str | Identifier, objects: TmtObjectsTrack) -> str:
    """ Get info about identifier """
    if not objects.check_exists(ident):
        return "<Not Found>"
    obj: TmtObject | None = objects.get(ident)
    assert obj is not None, 'expected name to exist, '\
        f'but got None. Context: {objects}'
    if isinstance(obj, FunctionDefinition):
        raise NotImplementedError  # TODO: implement
    return (f'<{obj.__class__.__name__} ' +
            f'"{obj.name.name}" : {obj.datatype.name}' +
            (f'={obj.datatype.subtype}>' if obj.datatype.subtype else '>'))
