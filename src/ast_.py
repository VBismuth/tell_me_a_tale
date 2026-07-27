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

""" Abstract Syntax Tree for TMT """

from dataclasses import dataclass
from typing import (
    Union, Optional, Any,
    Tuple, List, Dict,
    get_args as type_get_args
)

from .text import Text, Pos


# !!START!!
@dataclass
class DataType:
    """ Types of TMT data are static """
    name: str
    subtype: Optional[str] = None


@dataclass(frozen=True)
class Identifier:
    """ For function or variable name """
    name: str


@dataclass
class Variable:
    """ Represents a variable structure in TMT """
    name: Identifier
    datatype: DataType
    value: str  # value represented as str, but can be processed using datatype
    _mutable: bool = True


@dataclass
class Constant(Variable):
    """ Represents a constant structure in TMT, same as Variable """
    _mutable: bool = False


@dataclass
class Literal:
    """ Usually a base r-value or parameter """
    value: str
    valtype: DataType


@dataclass
class ListLiteral:
    """ Array of expresions """
    values: List[Expression]


@dataclass
class TMTImport:
    """ Import C lib or TMT module """
    position: Tuple[Pos, Pos]
    name: str
    file: str
    imported: Dict[Identifier, FunctionDefinition | Constant]
    is_ffi: bool = False


@dataclass
class BinaryOperation:
    """ Math operations or comparison on two operands """
    position: Tuple[Pos, Pos]
    operator: str
    left: Expression
    right: Expression


@dataclass
class UnaryOperation:
    """ Single operation like '-(1+2)' or 'not true' """
    position: Tuple[Pos, Pos]
    operator: str
    operand: Expression


@dataclass
class LogicOperation:
    """ Logic operation like 'a and b' """
    position: Tuple[Pos, Pos]
    operator: str
    left: Expression
    right: Expression


@dataclass
class VariableDeclaration:
    """ Variable declaration in TMT. Requires type """
    position: Tuple[Pos, Pos]
    object: Variable
    assignment: Expression


@dataclass
class ConstantDeclaration:
    """ Same as variable, but immutable and can be optimized in expressions """
    position: Tuple[Pos, Pos]
    object: Constant
    assignment: Expression


@dataclass
class VariableAssignment:
    """ Assign variable to expression """
    position: Tuple[Pos, Pos]
    left: Variable
    right: Expression


@dataclass
class FunctionDefinition:
    """ Represents a function structure in TMT """
    position: Tuple[Pos, Pos]
    name: Identifier
    returntype: DataType
    args: List[Variable]
    body: List[Statement]


@dataclass
class FunctionCall:
    """ Calling defined or builtin function """
    position: Tuple[Pos, Pos]
    name: Identifier
    args: List[Expression]


@dataclass
class Branch:
    """ Basic control flow with conditions """
    position: Tuple[Pos, Pos]
    condition: Expression
    if_body: List[Statement]
    else_body: List[Statement]


@dataclass
class WhileLoop:
    """ Basic loop. Also it is Until with negative condition """
    position: Tuple[Pos, Pos]
    condition: Expression
    body: List[Statement]


@dataclass
class ForLoop:
    """ WhileLoop but with batteries """
    position: Tuple[Pos, Pos]
    vars: List[Identifier]
    iterable: Expression
    body: List[Statement]


@dataclass
class ContinueStatement:
    """ Jump to the next iteration in a loop """
    position: Tuple[Pos, Pos]


@dataclass
class BreakStatement:
    """ Jump out of a loop """
    position: Tuple[Pos, Pos]


@dataclass
class Range:
    """ Range for slices, list assignment and iterables in ForLoop """
    position: Tuple[Pos, Pos]
    range_type: str  # inclusive or exclusive
    range_from: Expression
    range_to: Expression
    is_including: bool = False
    step: Optional[Expression] = None


@dataclass
class IndexAccess:
    """ Accessing values from list """
    position: Tuple[Pos, Pos]
    container: Expression
    index: Expression


@dataclass
class ReturnStatement:
    """ Return value or None in functions """
    position: Tuple[Pos, Pos]
    value: Optional[Expression] = None


@dataclass
class Program:
    """ Main node for a program """
    filename: str
    filepath: str
    source: Text
    body: List[Statement]


Expression = Union[
    Literal,
    ListLiteral,
    Identifier,
    BinaryOperation,
    UnaryOperation,
    LogicOperation,
    FunctionCall,
    Range,
    IndexAccess
]
Statement = Union[
    VariableDeclaration,
    ConstantDeclaration,
    VariableAssignment,
    FunctionDefinition,
    FunctionCall,
    Branch,
    WhileLoop,
    ForLoop,
    ReturnStatement,
    ContinueStatement,
    BreakStatement,
]
Node = Union[Expression, Statement, Program, DataType]
AstTypes = Union[Node, Pos, Text]

AST_TYPES_MAP = {cls.__name__: cls for cls in type_get_args(AstTypes)}


def ast_to_dict(node: AstTypes | None) -> Dict[str, Any] | None:
    """ Convert ast to dict """
    if not isinstance(node, type_get_args(AstTypes)) or\
            not hasattr(node, '__dataclass_fields__'):
        return None
    res: Dict[str, Any] = {'type': node.__class__.__name__}
    for field_name in node.__dataclass_fields__:
        field = getattr(node, field_name)
        if isinstance(field, type_get_args(AstTypes)):
            res[field_name] = ast_to_dict(field)
        elif isinstance(field, tuple):
            res[field_name] = [ast_to_dict(item) for item in field]
            res[field_name].append('__tuple__')
        elif isinstance(field, list):
            res[field_name] = [ast_to_dict(item) for item in field]
        else:
            res[field_name] = field
    return res


def ast_from_dict(obj: dict[str, Any] | Any) -> AstTypes | Any:
    """ Load ast from dict """
    if not isinstance(obj, dict):
        return obj
    if 'type' not in obj or obj['type'] not in AST_TYPES_MAP:
        return None
    obj_type = obj['type']
    new_fields: dict[str, Any] = {
        key: val for key, val in obj.items() if key != 'type'}
    for field in new_fields:
        value = new_fields[field]
        if isinstance(value, dict):
            if 'type' not in value:
                continue
            new_fields[field] = ast_from_dict(value)
        elif isinstance(value, list) and '__tuple__' in value:
            new_fields[field] = tuple(
                ast_from_dict(item) for item in value
                if item != '__tuple__')
        elif isinstance(value, list) and '__tuple__' not in value:
            new_fields[field] = [ast_from_dict(item) for item in value]
    res: AstTypes = AST_TYPES_MAP[obj_type](**new_fields)
    return res
