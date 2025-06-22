from enum import Enum
from typing import Optional, List
from lexer import Token, TokenKind, OperatorAssociativityKind

# TODO: Can this be simplified/eliminated with the values already present in TokenKind?
class BinaryExpressionKind(Enum):
    PLUS = 0
    MINUS = 1
    MULTIPLY = 2
    DIVIDE = 3
    EXPONENT = 4

class ASTNode: pass
class ASTExpression: pass
class ASTIdentifier: pass
class ASTStatement: pass
class ASTProgram: pass
class ASTNumber: pass
class ASTVariableDeclaration: pass
class ASTBinaryExpression: pass

class ASTNode:
    def dump_ast(self, depth: int = 1) -> str:
        return ""

class ASTProgram(ASTNode):
    __slots__ = ["nodes"]

    nodes: List[ASTStatement]

    def __init__(self):
        self.nodes = []

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTProgram({", ".join(node.dump_ast(depth+1) for node in self.nodes)})"

# === Expressions ===
class ASTExpression(ASTNode):
    pass

class ASTIdentifier(ASTExpression):
    __slots__ = ["name"]

    name: str

    def __init__(self, name: str):
        self.name = name

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTIdentifier('{self.name}')"

class ASTNumber(ASTExpression):
    __slots__ = ["literal"]

    literal: str

    def __init__(self, literal: str):
        self.literal = literal

    def dump_ast(self, depth: int = 1) -> str:
        indent = "\t" * depth
        return f"ASTNumber({self.literal})"

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

# === Statements ===
class ASTStatement(ASTNode):
    pass

class ASTVariableDeclaration(ASTStatement):
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
        program = ASTProgram()
        while (statement := self.statement()) is not None:
            program.nodes.append(statement)

        return program

    def expression(self, precedence_limit: int = 0) -> ASTExpression:
        token = self.advance()
        if token.kind == TokenKind.IDENTIFIER:
            expression = ASTIdentifier(token.literal)
        elif token.kind == TokenKind.NUMBER:
            expression = ASTNumber(token.literal)

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

    def statement(self) -> Optional[ASTStatement]:
        statement = None

        if (token := self.peek()) is not None and token.kind == TokenKind.IDENTIFIER:
            statement = self.declaration()

        return statement
