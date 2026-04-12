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

""" Working with source text """

from dataclasses import dataclass


@dataclass
class Pos:
    """ Positon in text """
    line: int = 1
    column: int = 1
    index: int = 0


@dataclass
class Text:
    """ Text structure """
    current_pos: Pos
    text: str
    filename: str = '<string>'

    def get_pos(self, idx: int = 0) -> tuple[int, int]:
        """ Gets text pos by index """
        line: int = self.current_pos.line
        col: int = self.current_pos.column
        if self.current_pos.index == 0 or self.current_pos.index > idx:
            pointer: int = 0
            line = 1
            col = 1
        else:
            pointer = self.current_pos.index
        line += self.text.count('\n', pointer, idx)
        if line == self.current_pos.line:
            col += max(idx - pointer, 0)
        else:
            col = max(idx - self.text.rfind('\n', pointer, idx), 1)
        return (line, col)

    def set_pos(self, idx: int = 0) -> None:
        """ Sets pos by index idx """
        line, col = self.get_pos(idx)
        self.current_pos.index = idx
        self.current_pos.line = line
        self.current_pos.column = col

    def get_line(self, line_n: int = 1) -> str:
        """ Get line from text """
        if not self.text:
            return ''
        return self.text.split('\n')[max(line_n - 1, 0)]
