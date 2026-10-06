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

""" Some utils for working with TMT types """

from .ast_ import DataType
from .errors import error_print, warn_print

# !!START!!
# Unsigned Integers
MAX_U8 = 255
MAX_U16 = 65_535
MAX_U32 = 4_294_967_295
MAX_U64 = 18_446_744_073_709_551_615

# Signed Integers
MAX_I8 = 127
MIN_I8 = -128
MAX_I16 = 32_767
MIN_I16 = -32_768
MAX_I32 = 2_147_483_647
MIN_I32 = -2_147_483_648
MAX_I64 = 9_223_372_036_854_775_807
MIN_I64 = -9_223_372_036_854_775_808

# Floats (IEEE 754)
MAX_F32 = 3.4028235e+38
MAX_F64 = 1.7976931348623157e+308

MIN_F32 = 1.1754944e-38
MIN_F64 = 2.2250738585072014e-308

VALID_TYPES = ('text', 'number', 'boolean',
               'pointer', 'none', 'array')

NUMBER_SUBTYPES = ('i8', 'i16', 'i32', 'i64', 'f32',
                   'u8', 'u16', 'u32', 'u64', 'f64')

ARRAY_SUBTYPES = ('text', 'boolean', 'pointer') + NUMBER_SUBTYPES


def is_valid_type(val: DataType) -> bool:
    """ Checks is a valid type """
    return (
        isinstance(val, DataType) and
        val.name not in VALID_TYPES and
        (val.name == 'number' and
         (val.subtype is None or val.subtype in NUMBER_SUBTYPES)
         ) and
        (val.name == 'array' and
         (val.subtype is None or val.subtype in ARRAY_SUBTYPES)
         )
    )


def number_wrap(value: str, valtype: DataType) -> str | None:
    """ Wrap number values if their type is valid, returns None otherwise """
    if not isinstance(value, str) or not is_valid_type(valtype) or\
            valtype.name != 'number':
        error_print(
            f'ERROR: number_wrap: expected "str" but got {type(value)!r},',
            f'or not valid type {valtype!r}, expected "number"')
        return None
    res = value
    if valtype.subtype is None or valtype.subtype == 'f64':
        val_float: float = float(value)
        val_float = val_float % (MAX_F64 if val_float > 0 else MIN_F64)
        res = str(val_float)
    elif valtype.subtype == 'f32':
        val_float  = float(value)
        val_float = val_float % (MAX_F32 if val_float > 0 else MIN_F32)
        res = str(val_float)
    elif valtype.subtype == 'u8':
        val_int: int = int(value) & 0xFF
        res = str(val_int)
    elif valtype.subtype == 'u16':
        val_int = int(value) & 0xFFFF
        res = str(val_int)
    elif valtype.subtype == 'u32':
        val_int = int(value) & 0xFFFFFFFF
        res = str(val_int)
    elif valtype.subtype == 'u64':
        val_int = int(value) & 0xFFFFFFFFFFFFFFFF
        res = str(val_int)
    elif valtype.subtype == 'i8':
        val_int = int(value)
        val_int = val_int % (MAX_I8 if val_int > 0 else MIN_I8)
        res = str(val_int)
    elif valtype.subtype == 'i16':
        val_int = int(value)
        val_int = val_int % (MAX_I16 if val_int > 0 else MIN_I16)
        res = str(val_int)
    elif valtype.subtype == 'i32':
        val_int = int(value)
        val_int = val_int % (MAX_I32 if val_int > 0 else MIN_I32)
        res = str(val_int)
    elif valtype.subtype == 'i64':
        val_int = int(value)
        val_int = val_int % (MAX_I64 if val_int > 0 else MIN_I64)
        res = str(val_int)
    else:
        error_print('ERROR: number_wrap: not a valid subtype: ',
                    f'{valtype.subtype!r}')
        return None
    return res


def is_castable(this: DataType, other: DataType) -> bool:
    """ Checks if provided type is castable to anther """
    res: bool = False
    if not is_valid_type(this) or not is_valid_type(other):
        warn_print('WARN: is_castable: invalid check {this!r} -> {other!r}')
        res = False
    elif this.name == other.name and this.subtype == other.subtype:
        res = True
    elif this.name == 'pointer' and other.subtype in (this.subtype, this.name):
        res = True
    elif this.name == 'number' and other.name == 'number' and\
            other.subtype in (None, 'f64'):
        res = True
    elif this.name in ('number', 'bool', 'none') and\
            other.name in ('text', 'number', 'bool'):
        res = (this.subtype == other.subtype) or\
            (this.subtype is not None and other.subtype is not None and
             int(this.subtype[1:]) >= int(other.subtype[1:]))
    elif this.name == 'text':
        res = other.name in ('text', 'boolean', 'number')
    return res
