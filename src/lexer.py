# -*- Encoding: utf-8 -*-
""" Lexer for the TMT """

from dataclasses import dataclass

from tokens import TokenType as TT, Token, Pos

keywords = {'tell me a tale', 'tell me a tale about', 'tell me about',
            'say', 'in witch', 'there is a tale of', 'so it begins', 'the end',
            'self', 'of kind', 'string', 'number', 'boolean', 'none',
            }

assert TT.COUNT.value == 5, "Nonexhaustive token handle"
token_patterns = {
    'COMMENT': r'(?:[^\\]\{\{)(?:[^\n] && [^\}]{2} || (?:\\\}\}))',
}

''
@dataclass
class Text:
    """ Text structure """
    current_pos: Pos
    text: str
    filename: str = '<string>'
