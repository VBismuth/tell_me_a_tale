# -*- Encoding: utf-8 -*-
""" Lexer for the TMT """

import re
from dataclasses import dataclass

from tokens import TokenType as TT, Token, Pos

# TODO: if common keyword used outside of context, like 'about' outside
# of 'tell me' then it should be connected to string
keywords = ('this is a tale', 'of kind', 'string', 'number', 'boolean', 'none',
            'about', 'in which', 'is',
            )

assert TT.COUNT.value == 7, "Nonexhaustive token handle"
token_patterns = {
    'COMMENT':    r'(?:-\([\s\S]*?\)-)|(?:--[^\n]*)',
    'NAME':       r'\"[^\n]*?\"',
    'TERMINATOR': r'[.;]',
    'KEYWORD':    r'|'.join(keywords),
    # TODO: MATH
}

PARSE_PTRN: str = '|'.join(f'(?P<{name}>{ptrn})'
                           for name, ptrn in
                           token_patterns.items())


@dataclass
class Text:
    """ Text structure """
    current_pos: Pos
    text: str
    txt_idx: int = 0
    filename: str = '<string>'

    # FIXME: strange pos of ~500 at idx 290
    def get_pos(self, idx: int = 0) -> tuple[int, int]:
        """ Gets text pos by index """
        if '\n' in self.text[self.txt_idx:idx]:
            line: int = self.current_pos.line + max(
                self.text.count('\n', self.txt_idx, idx), 1)
            col: int = max(
                idx - 1 - self.text.rfind('\n', self.txt_idx, idx), 1)
        else:
            line: int = self.current_pos.line
            col: int = max(self.current_pos.column + idx - 1, 1)
        return (line, col)

    def set_pos(self, idx: int = 0) -> None:
        """ Sets pos by idx """
        line, col = self.get_pos(idx)
        self.txt_idx = idx
        self.current_pos.line = line
        self.current_pos.column = col


def tokenize(text: Text, pattern: str = PARSE_PTRN) -> Token:
    """ Token generator from text """
    for match in re.finditer(pattern, text.text, re.IGNORECASE):
        tokenname: str = match.lastgroup
        body: str = match.group(tokenname)
        idx_start, idx_end = match.span(tokenname)
        pos_start: Pos = Pos(*text.get_pos(idx_start))
        pos_end: Pos = Pos(*text.get_pos(idx_end))
        text.set_pos(idx_end)

        yield Token(
            start_pos=pos_start,
            end_pos=pos_end,
            filename=text.filename,
            body=body,
            type_=getattr(TT, tokenname) or TT.NONE
        )
