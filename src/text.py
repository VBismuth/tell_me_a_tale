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
from typing import Optional


# !!START!!
@dataclass
class Pos:
    """ Positon in text """
    line: int = 1
    column: int = 1
    index: int = 0

    def update(self, other: Pos) -> None:
        """ Update Pos object """
        self.line = other.line
        self.column = other.column
        self.index = other.index

    def copy(self) -> "Pos":
        """ Copy self """
        return Pos(
            line=self.line,
            column=self.column,
            index=self.index
        )


@dataclass
class Text:
    """ Text structure """
    current_pos: Pos
    text: str
    file: str = '<string>'

    def get_pos(self, idx: int = 0,
                ignore_current_idx: bool = False) -> tuple[int, int]:
        """ Gets text pos by index """
        line: int = self.current_pos.line
        col: int = self.current_pos.column
        if (ignore_current_idx or
                self.current_pos.index == 0 or
                self.current_pos.index > idx):
            pointer: int = 0
            line = 1
            col = 1
        else:
            pointer = self.current_pos.index
        line += self.text.count('\n', pointer, idx)
        if not ignore_current_idx and line == self.current_pos.line:
            col += max(idx - pointer, 0)
        else:
            col = max(idx - self.text.rfind('\n', pointer, idx), 1)
        return (line, col)

    def set_pos(self, idx: int = 0) -> None:
        """ Sets pos by index idx """
        # Need to ignore current index to not accumulate unessery columns
        line, col = self.get_pos(idx, ignore_current_idx=True)
        self.current_pos.index = idx
        self.current_pos.line = line
        self.current_pos.column = col

    def get_line(self, line_n: int = 1) -> str:
        """ Get line from text """
        if not self.text:
            return ''
        return self.text.split('\n')[max(line_n - 1, 0)]

    def get_slice(self, start_pos: Pos, end_pos: Pos) -> str:
        """ Get slice from text from start to end positions """
        return self.text[start_pos.index:end_pos.index]

    def get_rest(self, end_pos: Optional[Pos] = None) -> str:
        """ Get slice of text from current position
            to text end or end pos (optional)"""
        if not isinstance(end_pos, Pos):
            end_pos = Pos(
                *self.get_pos(len(self.text)),
                len(self.text)
            )
        return self.get_slice(self.current_pos, end_pos)

    def copy(self) -> Text:
        """ Copy self """
        return Text(
            current_pos=self.current_pos.copy(),
            text=self.text,
            file=self.file
        )

    @staticmethod
    def new(text: str, file: str = '<string>') -> "Text":
        """ Create new instance of Text """
        return Text(
            current_pos=Pos(),
            text=text,
            file=file
        )
