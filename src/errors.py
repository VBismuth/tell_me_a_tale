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

""" Printing error messages """

from .text import Text, Pos

DEFAULT_IDENT = ' '


def print_arrows(indent: int, size: int) -> None:
    """ Draw arrows """
    print(DEFAULT_IDENT * indent + '^' * size)


def error_message(start_pos: Pos, end_pos: Pos,
                  text: Text, message: str) -> None:
    """ Print error message """
    print()  # TODO reformat message
    line_num_size: int = len(str(max(start_pos.line, end_pos.line)))
    start_pos_num: str = f'{start_pos.line:0{line_num_size}d} |'
    if start_pos.line > 1 and text.get_line(start_pos.line - 1):
        print(f'{start_pos.line - 1:0{line_num_size}d} |', end='')
        print(text.get_line(start_pos.line - 1))
    text_part: str = text.get_line(start_pos.line)
    print(start_pos_num, end='')
    print(text_part)
    if end_pos.line == start_pos.line:
        arrows_size: int = max(end_pos.column - start_pos.column, 1)
    else:
        arrows_size = len(text_part) - start_pos.column + 1
    print(' ' * (len(start_pos_num) - 1) + '|', end='')
    print_arrows(start_pos.column - 1, arrows_size)

    for line in range(start_pos.line + 1, end_pos.line + 1):
        text_part = text.get_line(line)
        arrows_size = (
            len(text_part) if line != end_pos.line else end_pos.column - 1
        )
        print(f'{line:0{line_num_size}d} |', end='')
        print(text_part)
        print(' ' * (len(start_pos_num) - 1) + '|', end='')
        print_arrows(0, arrows_size)

    print(f'\n{text.filename}:{start_pos.line}:{start_pos.column}  {message}')
