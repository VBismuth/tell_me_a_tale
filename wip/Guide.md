# Tell Me A Tale — Guide

## Introduction

This guide explains the rules, syntax, and key concepts of the TMT language. It serves as both a language reference and implementation specification for the Storyteller interpreter.

---

## Core Specification

### Type System

TMT is a statically typed language with the following types:

| Type | Description | Variants |
|------|-------------|----------|
| `number` | Integer types | `i8`, `u8`, `i16`, `u16`, `i32`, `u32`, `i64`, `u64`|
| `      ` | Floating-point types | `f32`, `f64` (default: `f64`) |
| `text` | String/text | Unicode-aware strings |
| `boolean` | Logical values | `true`, `false` |
| `nothing` | Null/void type | `none` |
| `pointer` | Memory reference | Type-safe pointers |
| `table` | Collection types | Indexed arrays or dictionaries |

### Design Principles

- **Natural language:** TMT syntax closely resembles prose and natural English sentences.
- **Readable:** Programs should read like stories rather than traditional code.
- **Forgiving:** Non-essential words and formatting are tolerated and discarded during parsing.

### Implementation Notes

- **Quine Support:** Interpreters must support the `SELF` variable to print their own source code.
- **Unrecognized Text:** The interpreter may optionally print unmatched prose to console, but the default behavior is silent discard.
- **Interactive Mode:** REPL should handle incomplete statements gracefully and prompt for continuation.


### Program Structure

- **Entry point:** Execution begins at the start of the program.
- **Comments:** 
  - Single-line: `--` to end of line
  - Multi-line: `-( )-` blocks (supports folding)
- **Special commands:** Prefixed with `@`, occupy entire line
- **Termination:** Meaningful statements end with `;` or `.`
- **Automatic termination:** Interactive (REPL) mode appends termination automatically

### Core Concepts

#### Identifiers
Variable, constant, and function names are enclosed in double quotes: `"myVariable"`, `"MY_CONSTANT"`, `"sayHello"`.

#### Text and Strings
Text literals are enclosed in backticks: `` `Hello, world` ``.

#### Numbers
Supported formats: `42`, `-8.9`, `3.14E-12`, `+100`.

#### Type Annotations
Explicit type specification: `number=f64`, `number=i32`. If omitted, `number` defaults to `f64`.

#### Expressions
Mathematical and logical expressions are enclosed in underscores: `_1 + sin($"x") ^ 2_`.

#### References
The `$"identifier"` syntax retrieves the value of a variable or constant. It can be used in:
- Expressions: `_$"x" + $"y" * 2_`
- String interpolation: `` `Result: $"result"` ``
- Shorthand for "The meaning of" statements

#### Variables, Constants, and Functions

- **Variables:** Mutable data containers (declared with `(this | that) (is | was) [an actor] [of (type | kind) ...] "name"`)
- **Constants:** Immutable data (declared with `(that is | ...) a constant ...`)
- **Functions:** Reusable code blocks (declared with `(this is | ...) a tale [(of type | of kind) ...] [in which ...] ...`)

#### Words and Text Parsing
- **Words:** Any tokens not explicitly matched by language constructs (identifiers, strings, numbers, keywords).
- **Text:** Words are automatically combined into descriptive text during the parsing stage.
- **Unused words:** If words don't match required statement syntax, they are silently discarded without error.

#### Special Variables

- **`ERROR`:** Set when non-critical errors occur (file read failures, invalid operations, etc.). Contains error code.
- **`SELF`:** Built-in variable containing the complete source code of the Storyteller interpreter (for Quine support).

### Error Handling

- **Non-critical errors:** When a statement fails at runtime, it is cancelled, the `ERROR` variable is set with the error code, and execution continues.
- **Critical errors:** Cause immediate termination.
- **User responsibility:** Programs should check `ERROR` after risky operations (file I/O, external calls) and handle as needed.

### Standard Features

- Standard input/output/error streams (`STDIN`, `STDOUT`, `STDERR`)
- File reading and writing operations
- Module importing and FFI (Foreign Function Interface) library support

---

## Syntax Reference

### Output Operations

#### Basic Output: `say` and `tell me`

Print messages to the console:

```tmt
-- (tell me | say) (word [, word[, ...]] | string)[, ...]
Say `Hello and welcome`.
Say Hello and welcome.
Tell me `Hello and welcome\n`.
```

**Behavior:**
- `say`: Automatically appends newline, writes to `STDOUT`
- `tell me`: Requires explicit newline in string
- Arguments separated by commas are joined without spaces

**Under the hood:** Both transform into `_PRINT` function calls

```tmt
Tell me a tale "_PRINT" with "STDOUT", `Hello and `, `welcome\n`.
```

#### Error Output

Print to standard error:

```tmt
Tell error `This is an error!\n`.
Tell me a tale "_PRINT" with "STDERR", `This `, `is an error!\n`.
```

#### Printing Variable Information

Display variable metadata or values:

```tmt
-- Print variable type and metadata
Tell me about "ERROR"\n.        -- Output: <Variable "ERROR" : u8>
Tell me the meaning of "ERROR"\n.  -- Output: current value
```

Note: `about` is optional in the syntax.

```tmt
Say "ERROR".
```

**Printing Interpreter Source Code:**

```tmt
Tell me the meaning of "SELF".  -- Prints complete Storyteller source code (it contains trailing newline, so you don't need to append it)
```

### Input Operations

#### Reading User Input

Read from standard input:

```tmt
-- Declare and read in one statement (text type by default)
This is an actor "My Input" that should listen to me.

-- Or read into existing variable
Listen to me, "My Input".

-- Alternative syntax using function call
This is "My Input" that tells me a tale "_INPUT".
```

**Behavior:** Blocks until user provides input. Result is stored in the specified variable.

### File Operations


#### Writing to Files

Store a file path as text in a variable for reuse:

```tmt
This is "My File" that is `./some/path/file.txt`.
```

Append or create files:

```tmt
-- Append to file
Tell `some/other/path/file2.txt` `hello, world\n`.

-- Clear file (erase contents)
Erase the meaning of "My File".

-- Then write specific content to file
Tell the meaning of "My File" `hello\n`.
```

**Behavior:** Writing creates a new file if it doesn't exist. Appending adds to existing files.

#### Error Handling for Files

File operation errors set the `ERROR` variable:

```tmt
Clear `nonexistent.txt`.
If $"ERROR" equals to $"FILE_READ_ERROR" then quit $"ERROR".
```

**Error codes:** See [Error Codes](#error-codes) section for standard constants.

---

## Language Features (Detailed)

### TODO: Control Flow
- Conditional statements (`if`, `then`, `else`)
- Loops (`while`, `for`, `repeat`)
- Jump statements (`quit`, `return`, `break`, `continue`)

### TODO: Variable Declaration
- Syntax and scoping rules
- Type inference vs. explicit typing
- Const vs. mutable semantics

### TODO: Function Definition
- Declaration syntax (`that tells me a tale`)
- Parameters and return types
- Recursion and tail-call optimization

### TODO: Tables
- Array literal syntax
- Dictionary/map syntax
- Indexing and slicing operations

### TODO: String Interpolation
- Escape sequences
- Expression embedding in strings

### TODO: Pattern Matching and Destructuring???

### TODO: Module System
- Import syntax
- Namespace management? (maybe something like "Hello-HelloVar")
- FFI bindings

---

## Keywords Reference

### TODO: Complete Keyword List

**Categories:**
- **Output:** `say`, `tell`
- **Input:** `listen`
- **Control:** `if`, `then`, `else/otherwise`, `while`, `for`, `quit`, `return`
- **Declaration:** `this is`, `that was`, etc.
- **Types:** `number`, `text`, `boolean`, `nothing`, `pointer`, `table`
- **Other:** TODO?

---

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| `FILE_READ_ERROR` | File read failure | Unable to open or read file |
| `FILE_WRITE_ERROR` | File write failure | Unable to write to file |
| `FILE_ERASE_ERROR` | File erase failure | Unable to clear file contents |
| TBD | ... | ... |

---

## Examples

See `examples` directory:

- Hello World --- `00_simple_hello.tmt`
- Functions --- `TBD`
- Expressions --- `TBD`
- User interaction --- `TBD`
- File I/O --- `TBD`
- Loops and conditionals --- `TBD`
- TMT as Quine --- `the_meaning_of_self.tmt`
- FFI --- `TBD`

---
