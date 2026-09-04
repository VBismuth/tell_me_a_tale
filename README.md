# ![TMT Logo](tmt_logo.svg "Tell Me a Tale")  Tell Me a Tale

A small programming language designed to be read like a story

___

## The vision behind the language
I see you've stumbled upon this repository of my story-like language.
The idea of this language came to me suddenly --- I wanted to create a programming language that looks like a average story.
I've always been interested in such a small and strange languages built around some unique concept, like Brainfuck or Mogol. These are known as esoteric languages; they are quite fun, but not particaly useful.
Though, for TMT, I want to make it into a complete and self-hosted language with a FFI support that is both interpreted and compiled (maybe using VM, C or QBE backend).
Obviously, I don't expect this language to be used in production. I don't even know if I even finish this project. But I hope you'll like it...

## What I want to implement
- [x] Base structure for the language
- [ ] Expressions
- [ ] Functions
- [ ] Terminal I/O (1/2)
- [x] Interpreter
- [ ] External functions (FFI)
- [ ] Modules ("Books") and imports
- [ ] Filesystem operations (Read/Write)
- [ ] Compiler? (VM, C or QBE backend)
- [ ] Implement TMT in itself? (Woah!)
- [ ] Build system written in TMT?
- [ ] Debugger?
- [ ] Testing suite?

## Quickstart
### Requirements
* python 3.14
* mypy 2.3.1 (for type checking only)
* Nuitka 4.2 (for building)
* C compiler (for building, `gcc` or `clang` on Linux or MacOS and `msvc` on Windows)

### Running tests
To run all tests, just use
```shell
python -m src.tests
```

You also can provide test names as an argument, for example
```shell
python -m src.test TestAst
```

### Getting the Interpreter
There three ways to get interpreter.
You can use it from src by `python -m src.main`, but it will be limited. It's better if you merge src into one single file using
```shell
python source_merger.py
```
It will create a `storyteller.py` in `build/` directory.

If you want to get prebuilt binaries or python script, see [releases](https://github.com/VBismuth/tell_me_a_tale/releases) section.

### Using the Interpreter
>[!IMPORTANT]
> Please note, the interpreter is still `WIP` and lacks a lot of featires
> Right now it can only print text or values into the terminal

To see all possible commands use
```shell
storyteller help
```

There's example for "Hello World" program from shell argument and from file
```shell
storyteller tell "Say Hello World."

storyteller read ./examples/00_hello.tmt
```

TMT is also a quine. You can get a copy of it's full source code printed in terminal by running
```shell
storyteller tell "Tell me the meaning of \"SELF\"."
```

## How to Build
Ensure you have Nuitka installed in your system or venv
```shell
pip install nuitka
```

Then run sourcse_merger.py, so you'll get a merged source files
```shell
python sourcse_merger.py
```

_On Linux_ or _MacOS_ run
```shell
python -m nuitka --onefile --remove-output --output-dir=build --static-libpython=yes --python-flag=-O --output-filename=storyteller build/storyteller.py
```

_On Windows_ run
```shell
python -m nuitka --msvc=latest --onefile --remove-output --output-dir=build --static-libpython=yes --python-flag=-O --output-filename=storyteller build/storyteller.py
```
Nuitka could prompt for downloading DependencyWalker for onefile building on Windows
