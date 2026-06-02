# -*- coding: utf-8 -*-
""" Abstract Syntax Tree for TMT """
from dataclasses import dataclass
from typing import Union, Optional

from .text import Text, Pos


# !!START!!
# TODO: Import node and Foreign function support
@dataclass
class DataType:
    """ Types of TMT data are static """
    name: str
    subtype: Optional[str] = None


@dataclass
class Identifier:
    """ For function or variable name """
    name: str


@dataclass
class Literal:
    """ Usually a base r-value or parameter """
    value: LiteralType


@dataclass
class ListLiteral:
    """ Array of expresions """
    values: list[Expression]


@dataclass
class BinaryOperation:
    """ Math operations or comparison on two operands """
    position: tuple[Pos, Pos]
    operator: str
    left: Expression
    right: Expression


@dataclass
class UnaryOperation:
    """ Single operation like '-1' or 'not true' """
    position: tuple[Pos, Pos]
    operator: str
    operand: Expression


@dataclass
class LogicOperation:
    """ Logic operation like 'a and b' """
    position: tuple[Pos, Pos]
    operator: str
    left: Expression
    right: Expression


@dataclass
class VariableDeclaration:
    """ Variable declaration in TMT. Requires type """
    position: tuple[Pos, Pos]
    name: Identifier
    datatype: DataType
    assignment: Expression


@dataclass
class ConstantDeclaration:
    """ Same as variable, but immutable and can be optimized in expressions """
    position: tuple[Pos, Pos]
    datatype: DataType
    name: Identifier
    assignment: Expression


@dataclass
class VariableAssignment:
    """ Assign variable to expression """
    position: tuple[Pos, Pos]
    left: Identifier
    right: Expression


@dataclass
class FunctionDefinition:
    """ Represents a function structure in TMT """
    position: tuple[Pos, Pos]
    name: Identifier
    returntype: DataType
    args: list[tuple[Identifier, DataType]]
    body: list[Statement]


@dataclass
class FunctionCall:
    """ Calling defined or builtin function """
    position: tuple[Pos, Pos]
    name: Identifier
    args: list[Expression]


@dataclass
class Branch:
    """ Basic control flow with conditions """
    position: tuple[Pos, Pos]
    condition: Expression
    if_body: list[Statement]
    else_body: list[Statement]


@dataclass
class WhileLoop:
    """ Basic loop. Also it is Until with negative condition """
    position: tuple[Pos, Pos]
    condition: Expression
    body: list[Statement]


@dataclass
class ForLoop:
    """ WhileLoop but with batteries """
    position: tuple[Pos, Pos]
    vars: list[Identifier]
    iterable: Expression
    body: list[Statement]


@dataclass
class ContinueStatement:
    """ Jump to the next iteration in a loop """
    position: tuple[Pos, Pos]


@dataclass
class BreakStatement:
    """ Jump out of a loop """
    position: tuple[Pos, Pos]


@dataclass
class Range:
    """ Range for slices, list assignment and iterables in ForLoop """
    position: tuple[Pos, Pos]
    range_type: str  # inclusive or exclusive
    range_from: Expression
    range_to: Expression
    is_including: bool = False
    step: Optional[Expression] = None


@dataclass
class IndexAccess:
    """ Accessing values from list """
    position: tuple[Pos, Pos]
    container: Expression
    index: Expression


@dataclass
class ReturnStatement:
    """ Return value or None in functions """
    position: tuple[Pos, Pos]
    value: Optional[Expression] = None


@dataclass
class Program:
    """ Main node for a program """
    filename: str
    filepath: str
    source: Text
    body: list[Statement]


LiteralType = Union[int, float, str, bool, None]
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
