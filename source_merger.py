""" Merges several source py files into one """
from pathlib import Path
from typing import Optional, List, Dict
from sys import stderr


# Essentials
def _format(text: str) -> str:
    return SPECIAL_FORMAT.format(text)


def beautify_imports(including: List[str], treshold: int = 40) -> List[str]:
    """ Make large imports more clean by splitting large chunks """
    ident: str = ' ' * 4
    is_init: bool = False
    if not including or including[0] == INCLUDE_AS_MODULE:
        res: List[str] = [INCLUDE_AS_MODULE]
        to_include: List[str] = including[1:]
    elif including[0] == INCLUDE_AS_ALIAS:
        res = [*including[:2]]
        to_include = including[2:]
    else:
        res = []
        to_include = including
    text_size: int = len(to_include[0]) + len(', ')
    should_pass: bool = False
    for include in to_include:
        if should_pass:
            should_pass = False
            res.append(include)
        elif not include or include == INCLUDE_AS_MODULE:
            res.append(INCLUDE_AS_MODULE)
        elif include == INCLUDE_AS_ALIAS:
            should_pass = True
            res.append(include)
        elif not is_init:
            is_init = True
            res.append(f'(\n{ident}{include}')  # )
            text_size = len(include) + len(', ')
        elif text_size >= treshold:
            res.append(f'\n{ident}{include}')
            text_size = len(include)  + len(', ')
        else:
            res.append(include)
            text_size += len(include) + len(', ')
    res[-1] = f'{res[-1]}\n)'
    return res


SPECIAL_FORMAT: str = '!!{}!!'
INCLUDE_AS_MODULE: str = _format('module')
INCLUDE_AS_ALIAS: str = _format('module_alias')
PYTHON_EXT: str = '.py'
BLANK_LINES: str = '\n' * 3

# Config
TARGET_DIR: Path = Path('build')
TARGET: str = 'storyteller'
SOURCE_DIR: Path = Path('src')
SOURCE_SCHEME: List[str] = [
    'interactive_input',
    '__init__',
    'utils',
    'text',
    'errors',
    'tokens',
    'lexer',
    'ast_',
    'builtins_',
    'typecheck',
    'parser',
    'interpreter',
    'main'
]
INCLUDES: Dict[str, List[str]] = {
    're': [INCLUDE_AS_MODULE],
    'json': [INCLUDE_AS_MODULE],
    'textwrap': ['fill as tw_fill'],
    'pathlib': ['Path'],
    'difflib': ['get_close_matches'],
    'sys': [INCLUDE_AS_MODULE,
            'stdout', 'stderr', 'exit as sysexit',
            'argv as sysargs'],
    'typing': beautify_imports(
        ['Generator', 'Callable', 'Union',
         'Optional', 'Type', 'Any',
         'Tuple', 'List', 'Dict', 'TextIO',
         'get_args as type_get_args']),
    'dataclasses': ['dataclass', 'field'],
    'enum': ['Enum', 'auto as iota'],
}
HEADER_TEXT: str = '''# -*- coding: utf8 -*-
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

""" This is full source of the Storyteller - a TMT interpreter """
'''
FOOTER_TEXT: str = '''if __name__ == "__main__":
    main(sysargs)
'''


def post_processing(text: str) -> str:
    """ Function that will be called after merging """
    # pass
    return text.replace(_format('SELF'),
                        text.replace("\\", r"\\")\
                            .replace("'", "\\'"))


# Script main section
def _extract_content(text: str) -> str:
    begin_ptrn: str = _format('START')
    end_ptrn: str = _format('STOP')
    start_pos: int = text.find(begin_ptrn) + (len(begin_ptrn) + 1
                                              if begin_ptrn in text else 0)
    end_pos: int = text.rfind(end_ptrn)
    end_pos = text.rfind('\n', 0, end_pos) if end_pos >= 0 else end_pos
    return text[start_pos:end_pos]


def _merger(first: str, second: str, filename: Optional[str] = None) -> str:
    if isinstance(filename, str):
        second = f'# --- {filename + PYTHON_EXT} --- #\n' + second
    return first + BLANK_LINES + second


def _load_file(file: Path) -> str:
    res: str = ''
    if file.exists():
        res = file.read_text()
    else:
        print('\033[93mWARN: File', str(file), 'does not exist\033[0m',  # ]]
              file=stderr)
    return res


def _main() -> None:
    merged_file: str = HEADER_TEXT
    for module, includes in INCLUDES.items():
        index = 0
        from_module: List[str] = []
        while index < len(includes):
            include = includes[index]
            if include == INCLUDE_AS_MODULE:
                merged_file += f'\nimport {module}'
            elif include == INCLUDE_AS_ALIAS:
                if index + 1 >= len(includes):
                    raise IndexError(
                        'Expected an argument for INCLUDE_AS_ALIAS: '
                        f'{{{module}:{includes}}}')
                merged_file += f'\nimport {module} as {includes[index + 1]}'
                index += 1
            else:
                from_module.append(include)
            index += 1
        merged_file += (
            f'\nfrom {module} import '
            f'{", ".join(from_module).replace(', \n', ',\n')}'
            if from_module else '')

    for file in SOURCE_SCHEME:
        source: Path = SOURCE_DIR / (file + PYTHON_EXT)
        loaded: str = _load_file(source)
        if not loaded:
            continue
        content: str = _extract_content(loaded)
        if not content:
            print('\033[93mWARN:', source,  # ]
                  'has content or content is marked incorrectly\033[0m',  # ]
                  file=stderr)
            continue
        merged_file = _merger(merged_file, content, file)
        print('\033[34mINFO: merged', source, 'successfuly\033[0m')  # ]]
    merged_file += BLANK_LINES + FOOTER_TEXT
    if 'post_processing' in globals():
        merged_file = post_processing(merged_file)

    target_file: Path = TARGET_DIR / (TARGET + PYTHON_EXT)
    target_file.parent.mkdir(exist_ok=True, parents=True)
    target_file.touch(exist_ok=True)
    target_file.write_text(merged_file)
    print('\033[94mINFO: Merged to',  # ]
          f'{str(target_file.absolute())}\033[0m')  # ]


if __name__ == '__main__':
    _main()
