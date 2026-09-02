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

""" Main function for TMT interpreter """

from sys import argv as sysargs, exit as sysexit
from typing import List, Dict
from textwrap import fill as tw_fill
from pathlib import Path
import json

from . import TMT_VERSION, TMT_LICENSE, TMT_AUTHOR
from .ast_ import ast_to_dict
from .errors import DEFAULT_INDENT, warn_print, error_print, ParseError
from .tests import run_tests
from .text import Text
from .lexer import tokenize
from .parser import ParserContext, parse
from .utils import check_tmt_file


# !!START!!
APP_OPTIONS: Dict[str, List[str]] = {
    # option: ['args', 'description']
    'help':        ['', 'Shows this message'],
    'info':        ['', 'Shows info about TMT'],
    'read':        ['<file>', 'Runs a script from provided file'],
    'tell':        ['<str>', 'Runs a script from provided string'],
    'test':        ['[name[, ...]]', 'Runs self tests by name or names '
                    '(optional) or just runs all tests'],
    'translate':   ['<file>', 'Translates file to AST and dumps it '
                    'in JSON format into the current directory '
                    'as "<file>.ast.json"'],
    'interactive': ['<str>', 'Runs interpreter in an interactive '
                    'mode (like repl)'],
}


def app_help(app_name: str) -> None:
    """ Standard help message """
    initial_indent: int = 4
    name_indent: int = max(len(f'{key} {val[0]}')
                           for key, val in APP_OPTIONS.items())
    colon: str = ' : '
    subsequent_indent: int = initial_indent + name_indent + len(colon)

    print(f'Usage: {app_name} [options] [file|string]\n')
    print('Options:')
    for name, arg_n_desc in APP_OPTIONS.items():
        option: str = f'{name} {arg_n_desc[0]}' if arg_n_desc[0] else str(name)
        line = f'{option.ljust(name_indent)}{colon}{arg_n_desc[1]}'
        print(tw_fill(
            line,
            initial_indent=DEFAULT_INDENT * initial_indent,
            subsequent_indent=DEFAULT_INDENT * subsequent_indent
        ))


def app_info(app_name: str) -> None:
    """ Show info """
    print('Tell me a tale (TMT) is a small esolang,',
          'that supposed to be read as a story.'
          f'\n{app_name}', 'is an implementation of TMT in pure python.\n')
    print('TMT Version', TMT_VERSION)
    print('This program is licenced under', TMT_LICENSE)
    print('Copyright', TMT_AUTHOR)


def app_translate(app_name: str, target: str) -> None:
    """ Translates target into AST JSON and dumps it """
    file = check_tmt_file(app_name, target)
    source = Text.new(file.read_text('utf8'), str(file))
    try:
        tokens = list(tokenize(source))
    except AssertionError as err:
        error_print(f'ERROR: {app_name}:', err)
        error_print(f'{app_name.capitalize()}:',
                    'got an error at tokenizing stage.',
                    'See message above')
        sysexit(-1)
    ctx = ParserContext.setup(source, tokens)
    res = parse(ctx)
    if ctx.perror != ParseError.OK:
        error_print(app_name.capitalize(),
                    f'got {ctx.perror.name!r} at parsing stage.',
                    'See messages above')
        sysexit(ctx.perror.value)
    dump_file = Path(file.name.replace('.tmt', '.ast') + '.json')
    with dump_file.open('w', encoding='utf8') as fp:
        json.dump(ast_to_dict(res), fp, ensure_ascii=False)
    print(f'Succesfuly translated {target!r} to {str(dump_file)!r}')


def main(argv: List[str]) -> None:
    """ Main function """
    argn: int = len(argv)
    app_name: str = argv[0]
    # TODO: add documentation option
    if any((pattern in argv)
           for pattern in ('--help', 'help', '-h')):
        app_help(app_name)
        sysexit()
    if argn < 2:
        warn_print("WARN: expected an option")
        app_help(app_name)
        sysexit(1)

    if argv[1] not in APP_OPTIONS:
        error_print(f'ERROR: unknown option {argv[1]!r}')
        app_help(app_name)
        sysexit(-1)

    if argv[1] == 'info':
        app_info(app_name)
        sysexit()

    if argv[1] == 'test':
        print(app_name.capitalize(), 'is doing tests...')
        run_tests(argv=[argv[0]] + argv[2:], verbosity=2)  # exits by default
    if argv[1] == 'interactive':
        raise NotImplementedError
        # sysexit(-1)

    if argn < 3:
        error_print('ERROR: expected an argument')
        app_help(app_name)
        sysexit(-1)

    if argv[1] == 'translate':
        app_translate(app_name, argv[2])
    elif argv[1] == 'tell':
        raise NotImplementedError
    elif argv[1] == 'read':
        raise NotImplementedError
# !!STOP!!


if __name__ == '__main__':
    main(sysargs)
