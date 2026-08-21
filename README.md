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
- [ ] Terminal I/O
- [ ] Interpreter
- [ ] External functions (FFI)
- [ ] Modules ("Books") and imports
- [ ] Filesystem operations (Read/Write)
- [ ] Compiler? (VM, C or QBE backend)
- [ ] Implement TMT in itself? (Woah!)
- [ ] Build system written in TMT?
- [ ] Debugger?
- [ ] Testing suite?

## How to Build
You cannot do it yet.
It still WIP, but you can run `python source_merger.py` and it will merge TMT interpreter into single file `storyteller.py` and put it into tmp dir. Though it can only run tests at the moment.
