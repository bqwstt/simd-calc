from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from argparse import ArgumentParser

class OperatorAssociativityKind(Enum):
    RIGHT = 0
    LEFT = 1
    UNKNOWN = 2

class TokenKind(Enum):
    PLUS = 0 # +
    MINUS = 1 # -
    MULTIPLY = 2 # *
    DIVIDE = 3 # /
    EXPONENT = 4 # ^

    PLUS_EQUAL = 5 # +=
    MINUS_EQUAL = 6 # -=
    MULTIPLY_EQUAL = 7 # *=
    DIVIDE_EQUAL = 8 # /=

    ARRAY_OPEN = 9 # [
    ARRAY_CLOSE = 10 # ]
    PAREN_OPEN = 11 # (
    PAREN_CLOSE = 12 # )
    BRACE_OPEN = 13 # {
    BRACE_CLOSE = 14 # }

    ASSIGNMENT = 15 # :=
    SEMICOLON = 16 # ;
    COMMA = 17 # ,
    RANGE = 18 # ..
    FOR = 19 # for

    IDENTIFIER = 20
    NUMBER = 21

    def is_operator(self) -> bool:
        return self.value <= TokenKind.EXPONENT.value

    def operator_precedence(self) -> int:
        match self:
            case TokenKind.PLUS | TokenKind.MINUS:
                return 1
            case TokenKind.MULTIPLY | TokenKind.DIVIDE:
                return 2
            case TokenKind.EXPONENT:
                return 3
            case _:
                return 0
    
    def operator_associativity(self) -> OperatorAssociativityKind:
        match self:
            case TokenKind.PLUS | TokenKind.MINUS | TokenKind.MULTIPLY | TokenKind.DIVIDE:
                return OperatorAssociativityKind.LEFT
            case TokenKind.EXPONENT:
                return OperatorAssociativityKind.RIGHT
            case _:
                return OperatorAssociativityKind.UNKNOWN

@dataclass(slots=True)
class Token:
    kind: TokenKind
    literal: str
    line: int
    column: int

class Lexer:
    __slots__ = [
        "source",
        "start",
        "current",
        "tokens",
        "line",
        "column"
    ]

    source: str
    start: int
    current: int
    tokens: List[Token]
    line: int
    column: int

    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.tokens = []
        self.line = 1
        self.column = 0

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def peek(self) -> Optional[str]:
        return self.source[self.current] if self.current < len(self.source) else None

    def add_token(self, kind: TokenKind, advance: bool = False) -> None:
        column_start = self.column
        if advance:
            _ = self.advance()

        token = Token(
            kind=kind,
            literal=self.source[self.start:self.current],
            line=self.line,
            column=column_start)

        self.tokens.append(token)

    def consume_identifier(self, start: str) -> None:
        identifier = start
        next_char = self.peek()
        while next_char is not None and (next_char.isalnum() or next_char == '_'):
            identifier += next_char
            _ = self.advance()
            next_char = self.peek()

        kind = TokenKind.IDENTIFIER
        if identifier == "for":
            kind = TokenKind.FOR
            
        self.add_token(kind)

    def consume_number(self) -> None:
        next_char = self.peek()
        while next_char is not None and (next_char.isdigit() or next_char == '.'):
            _ = self.advance()
            next_char = self.peek()

        # TODO: Invalid numbers, e.g.: 1.5.1;
        self.add_token(TokenKind.NUMBER)
    
    def tokenize(self) -> List[Token]:
        while self.current < len(self.source):
            self.start = self.current
            current_char = self.advance()
            next_char = self.peek()

            match current_char:
                case ' ' | '\t' | '\r':
                    continue
                case '\n':
                    self.line += 1
                    self.column = 0
                    continue
                case '#':
                    while self.peek() is not None and self.peek() != '\n':
                        _ = self.advance()
                    continue
            
            match (current_char, next_char):
                case ('+', '='): self.add_token(TokenKind.PLUS_EQUAL, advance=True)
                case ('+', _):   self.add_token(TokenKind.PLUS)
                case ('-', '='): self.add_token(TokenKind.MINUS_EQUAL, advance=True)
                case ('-', _):   self.add_token(TokenKind.MINUS)
                case ('*', '='): self.add_token(TokenKind.MULTIPLY_EQUAL, advance=True)
                case ('*', _):   self.add_token(TokenKind.MULTIPLY)
                case ('/', '='): self.add_token(TokenKind.DIVIDE_EQUAL, advance=True)
                case ('/', _):   self.add_token(TokenKind.DIVIDE)
                case ('^', _):   self.add_token(TokenKind.EXPONENT)
                case ('[', _):   self.add_token(TokenKind.ARRAY_OPEN)
                case (']', _):   self.add_token(TokenKind.ARRAY_CLOSE)
                case ('(', _):   self.add_token(TokenKind.PAREN_OPEN)
                case (')', _):   self.add_token(TokenKind.PAREN_CLOSE)
                case ('{', _):   self.add_token(TokenKind.BRACE_OPEN)
                case ('}', _):   self.add_token(TokenKind.BRACE_CLOSE)
                case (':', '='): self.add_token(TokenKind.ASSIGNMENT, advance=True)
                case (';', _):   self.add_token(TokenKind.SEMICOLON)
                case (',', _):   self.add_token(TokenKind.COMMA)
                case ('.', '.'): self.add_token(TokenKind.RANGE, advance=True)
                case _:
                    if current_char.isalpha():
                        self.consume_identifier(current_char)
                    elif current_char.isdigit():
                        self.consume_number()
                    else:
                        raise SyntaxError(
                            f"Invalid character '{current_char}' at {self.line}:{self.column}.")
            
        return self.tokens

class BinaryExpressionKind(Enum):
    PLUS = 0
    MINUS = 1
    MULTIPLY = 2
    DIVIDE = 3
    EXPONENT = 4

class ASTNode:
    def dump_ast(self, depth: int = 1) -> str:
        return ""

class ASTIdentifier(ASTNode):
    __slots__ = ["name"]

    name: str

    def __init__(self, name: str):
        self.name = name

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTIdentifier('{self.name}')"

class ASTExpression(ASTNode):
    ...

class ASTNumber(ASTExpression):
    __slots__ = ["literal"]

    literal: str

    def __init__(self, literal: str):
        self.literal = literal

    def dump_ast(self, depth: int = 1) -> str:
        indent = "\t" * depth
        return f"ASTNumber({self.literal})"

class ASTVariableDeclaration(ASTNode):
    __slots__ = [
        "identifier",
        "expression"
    ]

    identifier: ASTIdentifier
    expression: ASTExpression

    def __init__(self, identifier: ASTIdentifier, expression: ASTExpression):
        self.identifier = identifier
        self.expression = expression
    
    def dump_ast(self, depth: int = 1) -> str:
        identifier = self.identifier.dump_ast(depth + 1)
        expression = self.expression.dump_ast(depth + 1)
        return f"ASTVariableDeclaration({identifier}, {expression})"

class ASTBinaryExpression(ASTExpression):
    __slots__ = [
        "operation",
        "left",
        "right"
    ]

    operation: BinaryExpressionKind
    left: ASTExpression
    right: ASTExpression

    def __init__(self, operation: BinaryExpressionKind, left: ASTExpression, right: ASTExpression):
        self.operation = operation
        self.left = left
        self.right = right

    def dump_ast(self, depth: int = 1) -> str:
        left = self.left.dump_ast(depth + 1)
        right = self.right.dump_ast(depth + 1)
        return f"ASTBinaryExpression('{self.operation}', {left}, {right})"

class Parser:
    __slots__ = [
        "tokens",
        "current"
    ]

    tokens: List[Token]
    current: int

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def advance(self) -> Token:
        token = self.tokens[self.current]
        self.current += 1
        return token

    def peek(self) -> Optional[Token]:
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def parse(self) -> ASTNode:
        # TODO: start from program node, go downwards declarations
        program = self.declaration()
        return program

    def expression(self, precedence_limit: int = 0) -> ASTExpression:
        expression = ASTNumber(self.advance().literal)
        next_token = self.peek()

        while next_token is not None and next_token.kind.is_operator():
            precedence = next_token.kind.operator_precedence()
            final_precedence = precedence

            if next_token.kind.operator_associativity() == OperatorAssociativityKind.RIGHT:
                final_precedence -= 1

            if precedence <= precedence_limit:
                return expression

            # Consume the operator
            operator = BinaryExpressionKind(self.advance().kind.value)

            right = self.expression(final_precedence)
            expression = ASTBinaryExpression(operator, expression, right)
            next_token = self.peek()

        return expression

    def declaration(self) -> ASTVariableDeclaration:
        identifier = ASTIdentifier(self.advance().literal)
        _ = self.advance() # Assignment token, TODO: error handling
        expression = self.expression()
        _ = self.advance() # Semicolon, TODO: error handling
        return ASTVariableDeclaration(identifier, expression)


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
