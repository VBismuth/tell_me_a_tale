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

from . import TMT_SELF


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
