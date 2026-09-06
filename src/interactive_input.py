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

""" Interactive input functional for the TMT """
import sys
import re
from typing import Optional, List
from difflib import get_close_matches

# !!START!!
# Platform-specific character reading setup
if sys.platform in ("win32", "cygwin"):
    try:
        import msvcrt
    except ImportError as err:
        sys.exit(
            f"interactive_input: couldn't import msvcrt: {err}"
        )

    def get_char() -> str:
        """ Get character from stdin and convert arrow keys"""
        assert hasattr(msvcrt, 'getch'), "getch() not found in module msvcrt"
        ch: bytes = msvcrt.getch()

        # Prefix for arrow/functional keys on Windows
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            return f"arrow_{ch2.hex()}"
        return ch.decode('utf-8', errors='ignore')

    # Map raw hexadecimal codes to actions
    KEY_UP = "arrow_48"
    KEY_DOWN = "arrow_50"
    KEY_LEFT = "arrow_4b"
    KEY_RIGHT = "arrow_4d"

else:
    try:
        import tty
        import termios
    except ImportError as err:
        sys.exit(
            f"interactive_input: couldn't import msvcrt: {err}"
        )

    def get_char() -> str:
        """ Get character from stdin and convert arrow keys"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch: str = sys.stdin.read(1)
            if ch == '\x1b':  # Escape sequence prefix on Unix
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return f"arrow_{ch3}"
            return str(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    KEY_UP = "arrow_A"
    KEY_DOWN = "arrow_B"
    KEY_RIGHT = "arrow_C"
    KEY_LEFT = "arrow_D"


CUR_CLEAR = '\x1b[K'
CUR_MOVE = '\x1b[{offset}C'
CTRL_C = '\x03'
CTRL_D = '\x04'

# Backspace Keys (\x7f on Unix, \x08 on Windows)
KEYS_BACKSPACE = ('\x7f', '\x08')


def visual_len(text: str) -> int:
    """ Return visual len of string ANSCII escapes """
    anscii_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')  # ]
    clean_text: str = anscii_escape.sub('', text)
    return len(clean_text)


class InteractiveInput:
    """ Interactive Input class """

    def __init__(self, prompt: str = "> ",
                 history: Optional[List[str]] = None,
                 auto_history: bool = True) -> None:
        self.prompt: str = prompt if isinstance(prompt, str) else ''
        self.history: List[str] = history if isinstance(history, list) else []
        self.auto_history: bool =\
            auto_history if isinstance(auto_history, bool) else False
        self.text_buf: List[str] = []
        self.cursor_pos: int = 0

    def clear_history(self) -> None:
        """ Clear history """
        self.history = []

    def read_history_file(self, filename: str = "history.txt") -> None:
        """ Get history from file and append it to existing one.
            By default tries to load history from the current dir """
        with open(filename, 'r', encoding='utf8') as f:
            self.history += f.readlines()

    def write_history_file(self, filename: str = "history.txt") -> None:
        """ Saves history to a file, history.txt by default """
        with open(filename, 'a+', encoding='utf8') as f:
            f.writelines(self.history)

    def add_history(self, entry: str) -> None:
        """ Add entry to history """
        if isinstance(entry, str):
            self.history.append(entry)

    def _arrow_keys_actions(self, ch: str,
                            history_buf: List[str],
                            history_idx: int) -> int:
        if ch == KEY_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1

        elif ch == KEY_RIGHT:
            if self.cursor_pos < len(self.text_buf):
                self.cursor_pos += 1

        elif ch == KEY_UP:
            if history_idx > 0:
                # Save live edits to current history slot before moving
                history_buf[history_idx] = "".join(self.text_buf)
                history_idx -= 1
                self.text_buf = list(history_buf[history_idx])
                self.cursor_pos = len(self.text_buf)

        elif ch == KEY_DOWN:
            if history_idx < len(history_buf) - 1:
                history_buf[history_idx] = "".join(self.text_buf)
                history_idx += 1
                self.text_buf = list(history_buf[history_idx])
                self.cursor_pos = len(self.text_buf)

        return history_idx

    def input(self, prompt: Optional[str] = None,
              history: Optional[List[str]] = None) -> str:
        """ Input function """
        prompt = prompt if isinstance(prompt, str) else self.prompt
        history = history if isinstance(history, str) else self.history

        # History temporary buffer
        history_buf: List[str] = history + ['']
        history_idx: int = len(history_buf) - 1

        self.text_buf = list(history_buf[history_idx])
        self.cursor_pos = len(self.text_buf)

        sys.stdout.write(prompt)
        sys.stdout.flush()

        while True:
            ch: str = get_char()
            if ch in ('\r', '\n'):  # Enter
                sys.stdout.write('\n')
                sys.stdout.flush()
                res: str = "".join(self.text_buf)
                if self.auto_history:
                    self.history.append(res)
                return res

            if ch in KEYS_BACKSPACE:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    self.text_buf.pop(self.cursor_pos)

            elif ch.startswith('arrow_'):
                history_idx =\
                    self._arrow_keys_actions(ch, history_buf, history_idx)
            elif ch == '\t' and self.cursor_pos >= len(self.text_buf):
                suggestions: List[str] =\
                    get_close_matches("".join(self.text_buf),
                                      self.history, 3, 0.3)
                if suggestions:
                    self.text_buf = list(
                        [suggest for suggest in suggestions
                         if len(suggest) >= len(self.text_buf)][0] or
                        suggestions[0]
                    )
                    self.cursor_pos = len(self.text_buf)

            elif ch == CTRL_C:
                sys.stdout.write('^C\n')
                sys.stdout.flush()
                raise KeyboardInterrupt from None
            elif ch == CTRL_D:
                sys.stdout.write('^D\n')
                sys.stdout.flush()
                raise EOFError from None

            elif len(ch) == 1 and ch.isprintable():  # Printable Character
                self.text_buf.insert(self.cursor_pos, ch)
                self.cursor_pos += 1
            else:
                # Ignore unhandled control characters
                continue

            # --- Screen Redrawing Routine ---
            # 1. CR (\r) returns cursor to the beginning of the line
            # 2. Print prompt and the updated text
            # 3. ANSI Sequence '\x1b[K' clears everything from the
            #    current cursor position to end of line
            sys.stdout.write(
                '\r' + prompt + "".join(self.text_buf) + CUR_CLEAR
            )

            # 4. Move the terminal cursor back to its logical horizontal pos
            offset: int = visual_len(prompt) + self.cursor_pos
            sys.stdout.write(
                '\r' + (CUR_MOVE.format(offset=offset) if offset > 0 else '')
            )
            sys.stdout.flush()
