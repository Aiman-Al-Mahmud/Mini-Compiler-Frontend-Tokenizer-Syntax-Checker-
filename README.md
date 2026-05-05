# Mini Compiler Frontend (Tokenizer + Syntax Checker)

A tiny, single-file compiler frontend that reads a source file, tokenizes it, classifies tokens, and performs basic syntax analysis for declarations, assignments, and print statements.

## Features

- Tokenizes identifiers, numbers, strings, operators, and punctuation
- Classifies tokens into categories (keyword, identifier, operator, etc.)
- Validates simple expressions with operator/operand structure
- Tracks declared identifiers and reports undeclared uses
- Ignores single-line comments starting with `//`

## Supported Syntax (High-Level)

The syntax checker currently understands:

- **Declarations**: `int x = 10 ;` or `float y ;`
- **Assignments**: `x = y + 2 ;`
- **Print**: `print ( x ) ;` or `print ( "hello" ) ;`
- **Expressions**:
  - Numbers: `123`, `3.14`, `-7`
  - Strings: double-quoted strings with no escapes
  - Booleans: `true`, `false`
  - Identifiers (must be declared before use)
  - Binary operators: `+ - * / % == != < > <= >= && ||`
  - Unary operators: `- !`

## Project Structure

```
.
├── compile.py
├── src code.txt
└── README.md
```

- `compile.py` contains the tokenizer, classifier, and syntax checker.
- `src code.txt` is the input file used by default.

## How It Works

1. Reads `src code.txt`
2. Prints the raw token list
3. Tokenizes the source text
4. Groups and prints tokens by category
5. Performs line-by-line syntax analysis and reports errors

## Run

```bash
python3 compile.py
```

## Changing the Input File

By default, `compile.py` reads `src code.txt`. To use a different file, edit the `src_file` variable in `main()`.

## Example Input

```
int x = 10 ;
int y = 20 ;
int sum = x + y ;
print ( sum ) ;
print ( "this is the sum" ) ;
```

## Notes and Limitations

- Only single-line comments (`//`) are supported.
- Strings must be double-quoted and cannot include escaped quotes.
- Loop headers are minimally validated; loop bodies are not parsed yet.
- There is no support yet for blocks, functions, or full conditional parsing.
- This is a learning project and not a full compiler.
- The included `src code.txt` currently contains syntax errors; edit it for a clean run.

## License

Add your preferred license before publishing.
