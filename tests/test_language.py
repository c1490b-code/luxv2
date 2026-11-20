import unittest

from luxlang.runtime import LuxError, run


class LuxRuntimeTests(unittest.TestCase):
    def test_variables_arithmetic_and_print(self):
        output, env = run('let answer = 6 * 7\nprint("answer: " + str(answer))')
        self.assertEqual(output, ["answer: 42"])
        self.assertEqual(env["answer"], 42)

    def test_precedence_and_parentheses(self):
        output, _ = run("print(2 + 3 * 4)\nprint((2 + 3) * 4)")
        self.assertEqual(output, ["14", "20"])

    def test_values_and_builtins(self):
        output, _ = run('print(type(nil), type(true), len("lux"), int("12"))')
        self.assertEqual(output, ["nil boolean 3 12"])

    def test_comments_comparisons_and_booleans(self):
        output, _ = run("# hello\nprint(2 < 3, 4 == 4, false)")
        self.assertEqual(output, ["true true false"])

    def test_repl_environment(self):
        _, env = run("let x = 4", {})
        output, env = run("print(x + 1)", env)
        self.assertEqual(output, ["5"])
        self.assertEqual(env["x"], 4)

    def test_errors_are_lux_errors(self):
        for source in ("print(missing)", "let x = 1\nlet x = 2", "print(1 / 0)", "print(1 + true)"):
            with self.subTest(source=source), self.assertRaises(LuxError):
                run(source)


if __name__ == "__main__":
    unittest.main()
