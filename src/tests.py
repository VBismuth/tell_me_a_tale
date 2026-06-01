""" TMT tests """
from unittest import TestCase, main as unittestmain

from .text import Text, Pos
from .tokens import Token, TokenType, ExpToken, ExpTokenType, AnyToken
from .lexer import tokenize, exp_tokenize


# !!START!!
class TestTokenize(TestCase):
    """ Test tokenization """

    def setUp(self) -> None:
        # initialize text
        self.expression = '_8 % 3 + 4 / (3 - 2^2 * 8) // 8.9 '\
            '+ $"Something" / exp(3.8)_'
        self.text = Text(Pos(), self.expression)

    def test_tokenize_output(self) -> None:
        """ Checks if output is correct """
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))

        result_str: str = ', '.join([str(token) for token in tokens])

        expected_str: str =\
            f'[EXPRESSION:{self.expression[1:31]}<...>]'

        self.assertEqual(result_str, expected_str)

    def test_tokenize_not_empty(self) -> None:
        """ Checks if tokens are generated """
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))
        self.assertGreater(len(tokens), 0,
                           "Tokens was not generated")

    def test_tokenize_right_size(self) -> None:
        """ Checks if tokens are generated of right size """
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))
        expected_size: int = 1
        self.assertEqual(len(tokens), expected_size,
                         "Number of tokens mismatch")

    def test_tokenize_returns_expected_types(self) -> None:
        """ Checks if type is correct """
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))
        for token in tokens:
            self.assertIsInstance(token.type_, TokenType,
                                  f"Token {str(token)} type is "
                                  f"incorrect")


class TestExpTokenize(TestCase):
    """ Test Expression tokenization """

    def setUp(self) -> None:
        # initialize text
        self.expression = '8 % 3 + 4 / (3 - 2^2 * 8) // 8.9 '\
            '+ $"Something" / exp(3.8)'
        self.text = Text(Pos(), self.expression)

    def test_exp_tokenize_output(self) -> None:
        """ Checks if output is correct """
        tokens: list[ExpToken] = list(exp_tokenize(self.text))

        result_str: str = ', '.join([str(token) for token in tokens])

        expected_str: str =\
            '<[NUMBER:8]>, <[MOD:%]>, <[NUMBER:3]>, <[PLUS:+]>, '\
            '<[NUMBER:4]>, <[DIV:/]>, <[LPAREN:(]>, <[NUMBER:3]>, <[MINUS:-]>'\
            ', <[NUMBER:2]>, <[POW:^]>, <[NUMBER:2]>, <[MULT:*]>, '\
            '<[NUMBER:8]>, <[RPAREN:)]>, <[INTDIV://]>, <[NUMBER:8.9]>, '\
            '<[PLUS:+]>, <[IDENT:Something]>, <[DIV:/]>, <[KEYWORD:exp]>, '\
            '<[LPAREN:(]>, <[NUMBER:3.8]>, <[RPAREN:)]>'

        self.assertEqual(result_str, expected_str)

    def test_exp_tokenize_not_empty(self) -> None:
        """ Checks if tokens are generated """
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        self.assertGreater(len(tokens), 0,
                           "Expression tokens was not generated")

    def test_exp_tokenize_right_size(self) -> None:
        """ Checks if tokens are generated of right size """
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        expected_size: int = 24
        self.assertEqual(len(tokens), expected_size,
                         "Number of expression tokens mismatch: "
                         f"expected {expected_size}, got {len(tokens)}")

    def test_exp_tokenize_returns_expected_types(self) -> None:
        """ Checks if type is correct """
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        for token in tokens:
            self.assertIsInstance(token.type_, ExpTokenType,
                                  f"Token {str(token)} type is "
                                  f"incorrect")
