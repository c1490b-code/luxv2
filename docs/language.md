# Lux language guide

Lux is currently an interpreted, dynamically typed language. Run a source file with `lux path/to/file.lux`, or start the REPL with `lux`.

## Syntax

One statement per line (or separate statements with semicolons). Comments begin with `#`.

```lux
# Variables are introduced once with let.
let greeting = "Hello"
let score = 6 * 7
print(greeting + ", Lux!")
print(score, score == 42, type(score))
```

Values: numbers, double-quoted strings, `true`, `false`, and `nil`. Operators: unary `+`/`-`; arithmetic `+`, `-`, `*`, `/`; equality `==`, `!=`; and ordering `<`, `<=`, `>`, `>=`. Parentheses group expressions. `+` joins two strings or adds two numbers. Variables cannot be redeclared in the same environment.

Built-ins: `print(...values)`, `len(string)`, `str(value)`, `int(number_or_numeric_string)`, and `type(value)`. Runtime and syntax errors are reported as readable errors rather than Python tracebacks.

## Current limitations

This is an early foundation: no user-defined functions, control flow, modules, package manager, static types, debugger, or sandbox. Do not run untrusted source on a machine where its execution would be unsafe. Language features are listed in [ROADMAP.md](../ROADMAP.md) so planned work is not confused with shipped functionality.
