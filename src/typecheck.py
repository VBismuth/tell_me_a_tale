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

from .ast_ import DataType, Literal
from .builtins_ import NOTHING

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


def value_wrap(val: Literal) -> Literal | None:
    """ Wrap values if their type is valid, returns None otherwise """
    if not isinstance(val, Literal) or not is_valid_type(val.valtype):
        return None
    value = val.value
    valuetype = val.valtype
    res = Literal(
        value=value,
        valtype=DataType(valuetype.name, valuetype.subtype)
    )
    if valuetype.name == 'number':
        if valuetype.subtype is None or valuetype.subtype == 'f64':
            val_float: float = float(value)
            res.value = str(val_float)
        elif valuetype.subtype is None or valuetype.subtype == 'f32':
            val_float  = float(value)
            res.value = str(val_float)  # TODO f32 to f64 conversion
        elif valuetype.subtype == 'u8':
            val_int: int = int(value) & 0xFF
            res.value = str(val_int)
        elif valuetype.subtype == 'u16':
            val_int = int(value) & 0xFFFF
            res.value = str(val_int)
        elif valuetype.subtype == 'u32':
            val_int = int(value) & 0xFFFFFFFF
            res.value = str(val_int)
        elif valuetype.subtype == 'u64':
            val_int = int(value) & 0xFFFFFFFFFFFFFFFF
            res.value = str(val_int)

    # TODO: finish

    return res
