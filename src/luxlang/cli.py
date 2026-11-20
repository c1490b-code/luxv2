"""Command line runner and interactive Lux REPL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runtime import LuxError, run


def main() -> None:
    parser = argparse.ArgumentParser(prog="lux", description="Run Lux programs or start the Lux REPL.")
    parser.add_argument("file", nargs="?", help="Lux source file (.lux)")
    args = parser.parse_args()
    if args.file:
        try:
            source = Path(args.file).read_text(encoding="utf-8")
            lines, _ = run(source)
            for line in lines:
                print(line)
        except (OSError, LuxError) as exc:
            print(f"lux: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        return

    print("Lux REPL — enter one statement per line; type exit or press Ctrl-D to quit.")
    variables = {}
    while True:
        try:
            line = input("lux> ")
        except EOFError:
            print()
            break
        if line.strip() in {"exit", "quit"}:
            break
        try:
            lines, variables = run(line, variables)
            for result in lines:
                print(result)
        except LuxError as exc:
            print(f"error: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
