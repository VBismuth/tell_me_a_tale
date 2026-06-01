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

from enum import Enum

from .text import Text, Pos
from .tokens import AnyToken

# !!START!!
DEFAULT_IDENT = ' '


class Colors(Enum):
    """ Terminal colors (ANSI escape codes)"""
    # Foreground colors
    FG_BLACK   = "\033[30m"  # ]
    FG_RED     = "\033[31m"  # ]
    FG_GREEN   = "\033[32m"  # ]
    FG_YELLOW  = "\033[33m"  # ]
    FG_BLUE    = "\033[34m"  # ]
    FG_MAGENTA = "\033[35m"  # ]
    FG_CYAN    = "\033[36m"  # ]
    FG_WHITE   = "\033[37m"  # ]

    # Background colors
    BG_BLACK   = "\033[40m"  # ]
    BG_RED     = "\033[41m"  # ]
    BG_GREEN   = "\033[42m"  # ]
    BG_YELLOW  = "\033[43m"  # ]
    BG_BLUE    = "\033[44m"  # ]
    BG_MAGENTA = "\033[45m"  # ]
    BG_CYAN    = "\033[46m"  # ]
    BG_WHITE   = "\033[47m"  # ]

    # Set to default
    RESET      = "\033[0m"   # ]


def print_arrows(indent: int, size: int, color: Colors = Colors.RESET) -> None:
    """ Draw arrows """
    if not isinstance(color, Colors):
        color = Colors.RESET
    print(color.value, end='')
    print(DEFAULT_IDENT * indent + '^' * size)
    print(Colors.RESET.value, end='')


def error_message(start_pos: Pos, end_pos: Pos,
                  text: Text, message: str,
                  message_color: Colors = Colors.RESET) -> None:
    """ Print error message """
    if not isinstance(message_color, Colors):
        message_color = Colors.RESET
    print(f'{text.filename}:{start_pos.line}:{start_pos.column} :: '
          f'{message_color.value}{message}{Colors.RESET.value}')
    print(Colors.FG_MAGENTA.value, end='')
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
    print_arrows(start_pos.column - 1, arrows_size, message_color)

    for line in range(start_pos.line + 1, end_pos.line + 1):
        text_part = text.get_line(line)
        arrows_size = (
            len(text_part) if line != end_pos.line else end_pos.column - 1
        )
        print(f'{line:0{line_num_size}d} |', end='')
        print(text_part)
        print(' ' * (len(start_pos_num) - 1) + '|', end='')
        print_arrows(0, arrows_size, message_color)
    print(Colors.RESET.value, end='')


def token_error(token: AnyToken,
                text: Text, message: str,
                message_color: Colors = Colors.FG_RED) -> None:
    """ Print error for token """
    error_message(token.start_pos, token.end_pos, text, message, message_color)
