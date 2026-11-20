"""Lexer, parser, and interpreter for the initial Lux language."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


class LuxError(Exception):
    """A user-facing Lux syntax or runtime error."""


_TOKEN = re.compile(
    r"(?P<SPACE>[ \t\r]+)|(?P<COMMENT>\#[^\n]*)|(?P<NEWLINE>\n)|"
    r"(?P<NUMBER>\d+(?:\.\d+)?)|(?P<STRING>\"(?:\\.|[^\"\\])*\")|"
    r"(?P<IDENT>[A-Za-z_][A-Za-z_0-9]*)|"
    r"(?P<OP>==|!=|<=|>=|[+*/<>()=,;\-])|(?P<BAD>.)"
)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int


def _lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    line = 1
    pos = 0
    while pos < len(source):
        match = _TOKEN.match(source, pos)
        if match is None:
            raise LuxError(f"line {line}: unable to read input")
        kind, value = match.lastgroup, match.group()
        if kind == "BAD":
            raise LuxError(f"line {line}: unexpected character {value!r}")
        if kind == "NEWLINE":
            tokens.append(Token("SEP", value, line))
            line += 1
        elif kind not in ("SPACE", "COMMENT"):
            tokens.append(Token(kind or "", value, line))
        pos = match.end()
    tokens.append(Token("EOF", "", line))
    return tokens


_PRECEDENCE = {"==": 1, "!=": 1, "<": 1, "<=": 1, ">": 1, ">=": 1,
               "+": 2, "-": 2, "*": 3, "/": 3}


class _Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def take(self) -> Token:
        token = self.peek()
        self.pos += 1
        return token

    def require(self, value: str) -> Token:
        token = self.take()
        if token.value != value:
            raise LuxError(f"line {token.line}: expected {value!r}, got {token.value!r}")
        return token

    def parse(self) -> list[tuple[Any, ...]]:
        statements = []
        while self.peek().kind != "EOF":
            if self.peek().kind == "SEP" or self.peek().value == ";":
                self.take()
                continue
            token = self.peek()
            if token.kind == "IDENT" and token.value == "let":
                self.take()
                name = self.take()
                if name.kind != "IDENT" or name.value in {"let", "true", "false", "nil"}:
                    raise LuxError(f"line {name.line}: expected a variable name")
                self.require("=")
                statements.append(("let", name.value, self.expression()))
            else:
                statements.append(("expr", self.expression()))
            if self.peek().kind not in ("SEP", "EOF") and self.peek().value != ";":
                t = self.peek()
                raise LuxError(f"line {t.line}: expected end of statement")
        return statements

    def expression(self, min_precedence: int = 0) -> tuple[Any, ...]:
        token = self.take()
        if token.value in ("-", "+"):
            left = ("unary", token.value, self.expression(4))
        elif token.value == "(":
            left = self.expression()
            self.require(")")
        elif token.kind == "NUMBER":
            left = ("literal", float(token.value) if "." in token.value else int(token.value))
        elif token.kind == "STRING":
            try:
                left = ("literal", json.loads(token.value))
            except json.JSONDecodeError as exc:
                raise LuxError(f"line {token.line}: invalid string escape") from exc
        elif token.kind == "IDENT":
            if token.value == "true":
                left = ("literal", True)
            elif token.value == "false":
                left = ("literal", False)
            elif token.value == "nil":
                left = ("literal", None)
            else:
                left = ("variable", token.value)
        else:
            raise LuxError(f"line {token.line}: expected an expression, got {token.value!r}")

        while True:
            if self.peek().value == "(":
                if 5 < min_precedence:
                    break
                self.take()
                args = []
                if self.peek().value != ")":
                    args.append(self.expression())
                    while self.peek().value == ",":
                        self.take()
                        args.append(self.expression())
                self.require(")")
                left = ("call", left, args)
                continue
            op = self.peek().value
            precedence = _PRECEDENCE.get(op, -1)
            if precedence < min_precedence:
                break
            self.take()
            right = self.expression(precedence + 1)
            left = ("binary", op, left, right)
        return left


def _display(value: Any) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _evaluate(node: tuple[Any, ...], env: dict[str, Any], output: list[str]) -> Any:
    kind = node[0]
    if kind == "literal":
        return node[1]
    if kind == "variable":
        if node[1] not in env:
            raise LuxError(f"undefined name {node[1]!r}")
        return env[node[1]]
    if kind == "unary":
        value = _evaluate(node[2], env, output)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise LuxError("unary arithmetic requires a number")
        return value if node[1] == "+" else -value
    if kind == "binary":
        op = node[1]
        left = _evaluate(node[2], env, output)
        right = _evaluate(node[3], env, output)
        try:
            if op == "+":
                if type(left) is not type(right) or not isinstance(left, (str, int, float)) or isinstance(left, bool):
                    raise LuxError("'+' requires two numbers or two strings of the same type")
                return left + right
            if op in ("-", "*", "/"):
                if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (left, right)):
                    raise LuxError(f"'{op}' requires numbers")
                if op == "-": return left - right
                if op == "*": return left * right
                return left / right
            if op in ("<", "<=", ">", ">=") and type(left) is not type(right):
                raise LuxError("comparison values must have the same type")
            return {"==": lambda: left == right, "!=": lambda: left != right,
                    "<": lambda: left < right, "<=": lambda: left <= right,
                    ">": lambda: left > right, ">=": lambda: left >= right}[op]()
        except (TypeError, ZeroDivisionError) as exc:
            raise LuxError(f"invalid operation: {exc}") from exc
    if kind == "call":
        callee = _evaluate(node[1], env, output)
        args = [_evaluate(arg, env, output) for arg in node[2]]
        if callee == "print":
            output.append(" ".join(_display(arg) for arg in args))
            return None
        if callee == "len":
            if len(args) != 1 or not isinstance(args[0], (str, list, tuple, dict)):
                raise LuxError("len expects one string or collection")
            return len(args[0])
        if callee == "str":
            if len(args) != 1: raise LuxError("str expects one argument")
            return _display(args[0])
        if callee == "int":
            if len(args) != 1 or isinstance(args[0], bool): raise LuxError("int expects one number or numeric string")
            try: return int(args[0])
            except (TypeError, ValueError) as exc: raise LuxError("int expects one number or numeric string") from exc
        if callee == "type":
            if len(args) != 1: raise LuxError("type expects one argument")
            value = args[0]
            return "nil" if value is None else "boolean" if isinstance(value, bool) else "number" if isinstance(value, (int, float)) else "string" if isinstance(value, str) else "unknown"
        raise LuxError(f"unknown function {callee!r}")
    raise LuxError("internal error: unknown expression")


def run(source: str, variables: dict[str, Any] | None = None) -> tuple[list[str], dict[str, Any]]:
    """Run Lux source and return printed lines plus the resulting variable environment."""
    env = dict(variables or {})
    output: list[str] = []
    for statement in _Parser(_lex(source)).parse():
        if statement[0] == "let":
            name = statement[1]
            if name in env:
                raise LuxError(f"name {name!r} is already defined")
            env[name] = _evaluate(statement[2], env, output)
        else:
            _evaluate(statement[1], env, output)
    return output, env
