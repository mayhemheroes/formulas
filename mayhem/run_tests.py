#!/usr/bin/python3
"""run_tests.py — RUN formulas' own unittest suite for the parser/tokenizer and print a
parseable summary.

Invoked via the `/mayhem/formulas-tests` ELF launcher (NOT directly), so the verify-repo
sabotage oracle can neuter the launcher and prove the test oracle is behavioral.

It runs the real known-answer suites that exercise the exact code the Atheris harness fuzzes
(formulas.Parser().ast(...).compile()):

  * test/test_parser.py  — hundreds of ddt-parametrized cases asserting that
    Parser().ast(<formula>) compiles to an EXACT expected infix string (and that malformed
    formulas raise FormulaError).
  * test/test_tokens.py  — known-answer tokenizer cases (Range/Number/String/Operator names,
    A1<->R1C1 conversions, error tokens).

A no-op / "exit(0)" / behavior-altering patch to the formulas parser cannot pass these.

Prints one line:
    RUNTESTS tests=<n> passed=<p> failed=<f> skipped=<s>
Exit 0 iff failed == 0. mayhem/test.sh parses that line into a CTRF report.
"""
from __future__ import annotations

import sys
import unittest

SRC = "/mayhem"
MODULES = ["test.test_parser", "test.test_tokens"]


def main() -> int:
    if SRC not in sys.path:
        sys.path.insert(0, SRC)

    try:
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        for mod in MODULES:
            suite.addTests(loader.loadTestsFromName(mod))
    except Exception as e:  # import/collection error == failure, not a vacuous pass
        print(f"collection error: {e}", file=sys.stderr)
        print("RUNTESTS tests=0 passed=0 failed=1 skipped=0")
        return 1

    result = unittest.TextTestRunner(verbosity=1).run(suite)

    tests = result.testsRun
    failed = len(result.failures) + len(result.errors)
    skipped = len(getattr(result, "skipped", []))
    passed = tests - failed - skipped

    print(f"RUNTESTS tests={tests} passed={passed} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
