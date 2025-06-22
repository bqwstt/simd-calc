from lexer import Lexer
from parser import Parser
from argparse import ArgumentParser

def main() -> None:
    argument_parser = ArgumentParser(
        prog="simd-calc",
        description="ASM transpiler for a simple calculator."
    )

    # TODO: CPU features flags (e.g.: -msse2, -mavx512)
    argument_parser.add_argument("filename")
    argument_parser.add_argument(
        "-O",
        dest="optimization_level",
        choices=["0", "1", "2", "3"],
        help="Optimization level (O0-O3)")

    args = argument_parser.parse_args()

    with open(args.filename, 'r') as file:
        lexer = Lexer(file.read())
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)

        parser = Parser(tokens)
        ast = parser.parse()
        print(ast.dump_ast())

if __name__ == "__main__":
    main()
