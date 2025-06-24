from dataclasses import dataclass
from enum import Enum
from typing import List

# TODO: Can this be simplified/eliminated with the values already present in TokenKind?
class BinaryExpressionKind(Enum):
    PLUS = 0
    MINUS = 1
    MULTIPLY = 2
    DIVIDE = 3
    EXPONENT = 4

# Forward declare, just such that we please the type checker :)
class ASTStatement: pass

@dataclass
class ASTNode:
    def dump_ast(self, depth: int = 1) -> str:
        return ""

@dataclass(slots=True)
class ASTProgram(ASTNode):
    nodes: List[ASTStatement]

    def __init__(self):
        self.nodes = []

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTProgram({", ".join(node.dump_ast(depth+1) for node in self.nodes)})"

# === Expressions ===
@dataclass
class ASTExpression(ASTNode):
    pass

@dataclass(slots=True)
class ASTIdentifier(ASTExpression):
    name: str

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTIdentifier('{self.name}')"

@dataclass(slots=True)
class ASTNumber(ASTExpression):
    literal: str

    def dump_ast(self, depth: int = 1) -> str:
        return f"ASTNumber({self.literal})"

@dataclass(slots=True)
class ASTBinaryExpression(ASTExpression):
    operation: BinaryExpressionKind
    left: ASTExpression
    right: ASTExpression

    def dump_ast(self, depth: int = 1) -> str:
        left = self.left.dump_ast(depth + 1)
        right = self.right.dump_ast(depth + 1)
        return f"ASTBinaryExpression('{self.operation}', {left}, {right})"

# === Statements ===
@dataclass
class ASTStatement(ASTNode):
    pass

@dataclass(slots=True)
class ASTVariableDeclaration(ASTStatement):
    identifier: ASTIdentifier
    expression: ASTExpression
    
    def dump_ast(self, depth: int = 1) -> str:
        identifier = self.identifier.dump_ast(depth + 1)
        expression = self.expression.dump_ast(depth + 1)
        return f"ASTVariableDeclaration({identifier}, {expression})"

@dataclass(slots=True)
class ASTFunctionCall(ASTExpression, ASTStatement):
    function: ASTIdentifier
    parameters: List[ASTExpression]

    def dump_ast(self, depth: int = 1) -> str:
        # This assumes the function has parameters, which may not always be true.
        function = self.function.dump_ast(depth + 1)
        parameters = ", ".join(param.dump_ast(depth + 2) for param in self.parameters)
        return f"ASTFunctionCall({function}, {parameters})"
