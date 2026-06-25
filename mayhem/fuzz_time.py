#!/usr/bin/env python3
import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports():
    import formulas
    from formulas.errors import FormulaError



def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        ast_builder = formulas.Parser().ast(fdp.ConsumeRemainingString())[1]
        ast_builder.compile()
    except (SyntaxError, FormulaError, ValueError) as e:
        return -1
def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
