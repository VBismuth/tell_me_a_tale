""" TMT tests """
from unittest import TestCase, main as unittestmain
from typing import Any, get_args as type_get_args

from .text import Text, Pos
from .tokens import Token, TokenType, ExpToken, ExpTokenType, AnyToken
from .lexer import tokenize, exp_tokenize
from .ast_ import ast_from_dict, ast_to_dict, AstTypes


# !!START!!
class TestAst(TestCase):
    """ Test AST """

    def setUp(self) -> None:
        self.expected_dict: dict[str, Any] = {
            "type": "Program",
            "file": "/pseudo/path/to/file.tmt",
            "body": [
                {"type": "BinaryOperation",
                 "position": [
                    {"type": "Pos",
                     "line": 1,
                     "column": 2,
                     "index": 1},
                    {"type": "Pos",
                     "line": 1,
                     "column": 6,
                     "index": 5}, "__tuple__"],
                 "operator": "+",
                 "left": {
                    "type": "Literal",
                    "value": "1",
                    "valtype": {
                        "type": "DataType",
                        "name": "number",
                        "subtype": "i32"}},
                 "right": {
                     "type": "Literal",
                     "value": "2",
                     "valtype": {
                         "type": "DataType",
                         "name": "number",
                         "subtype": "i32"}}}]}

    def test_ast_load_empty(self) -> None:
        """ Test try loading empty """
        res = ast_from_dict({})
        self.assertIsNone(res, 'Loading from empty dict returned something')

    def test_ast_dump_empty(self) -> None:
        """ Test try dumping empty """
        res = ast_to_dict(None)
        self.assertIsNone(res, 'Dumping None returned something')

    def test_ast_roundabout(self) -> None:
        """ Test ast loading and dumping """
        target_dict: dict[str, Any] = self.expected_dict.copy()
        converted: AstTypes = ast_from_dict(target_dict)
        self.assertIsNotNone(converted, 'Converted ast dict is None')
        test_dict: dict[str, Any] = ast_to_dict(converted) or {}
        self.assertIsNotNone(test_dict, 'Converted ast dict is None')
        self.assertDictEqual(target_dict, test_dict,
                             'AST dump+load cycle is incorrect')


class TestTokenize(TestCase):
    """ Test tokenization """
    # TODO: Add a general test for tokenizer, not just expression

    def setUp(self) -> None:
        # initialize text
        self.expression = '_8 % 3 + 4 / (3 - 2^2 * 8) // 8.9 '\
            '+ $"Something" / exp(3.8)_'
        self.text = Text(Pos(), self.expression)

    def test_tokenize_output(self) -> None:
        """ Checks if output is correct """
        self.text.set_pos()  # reset
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))

        result_str: str = ', '.join([str(token) for token in tokens])

        expected_str: str =\
            f'[EXPRESSION:{self.expression[1:31]}<...>]'

        self.assertEqual(result_str, expected_str)
        self.assertEqual(f"_{tokens[0].body}_",
                         self.text.get_slice(tokens[0].start_pos,
                                             tokens[0].end_pos)
                         )

    def test_tokenize_not_empty(self) -> None:
        """ Checks if tokens are generated """
        self.text.set_pos()  # reset
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))
        self.assertGreater(len(tokens), 0,
                           "Tokens was not generated")

    def test_tokenize_right_size(self) -> None:
        """ Checks if tokens are generated of right size """
        self.text.set_pos()  # reset
        tokens: list[Token] = list(tokenize(self.text, tokenize_expr=False))
        expected_size: int = 1
        self.assertEqual(len(tokens), expected_size,
                         "Number of tokens mismatch")

    def test_tokenize_returns_expected_types(self) -> None:
        """ Checks if type is correct """
        self.text.set_pos()  # reset
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
        self.text_multiple = Text.new("say.\nSay _1 + 3_.")

    def test_exp_tokenize_output(self) -> None:
        """ Checks if output is correct """
        self.text.set_pos()  # reset
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
        self.text.set_pos()  # reset
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        self.assertGreater(len(tokens), 0,
                           "Expression tokens was not generated")

    def test_exp_tokenize_right_size(self) -> None:
        """ Checks if tokens are generated of right size """
        self.text.set_pos()  # reset
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        expected_size: int = 24
        self.assertEqual(len(tokens), expected_size,
                         "Number of expression tokens mismatch: "
                         f"expected {expected_size}, got {len(tokens)}")

    def test_exp_tokenize_returns_expected_types(self) -> None:
        """ Checks if type is correct """
        self.text.set_pos()  # reset
        tokens: list[ExpToken] = list(exp_tokenize(self.text))
        for token in tokens:
            self.assertIsInstance(token.type_, ExpTokenType,
                                  f"Token {str(token)} type is "
                                  f"incorrect")

    def test_exp_hybrid_tokenize_output(self) -> None:
        """ Checks if hybrid (regular + expression) output is correct """
        self.text_multiple.set_pos()  # reset
        tokens: list[AnyToken] = list(tokenize(self.text_multiple))

        result_str: str = ', '.join([str(token) for token in tokens])
        expected_str: str =\
            '[KEYWORD:say], [TERMINATOR:.], [KEYWORD:Say], '\
            '<[NUMBER:1]>, <[PLUS:+]>, <[NUMBER:3]>, [TERMINATOR:.]'

        self.assertEqual(result_str, expected_str)
        self.assertEqual(tokens[3].start_pos, Pos(2, 6, 10))


def run_tests(*args: Any, **kwargs: Any) -> None:
    """ Test TMT """
    # TODO: custom tester to beautify output
    unittestmain(*args, **kwargs)
# !!STOP!!


if __name__ == '__main__':
    run_tests(verbosity=2)
