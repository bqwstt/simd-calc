from dataclasses import dataclass
from enum import Enum
from functools import singledispatchmethod
from typing import Optional, List, Tuple

from ..ast import *

# NOTE: This is a placeholder and is not be the final representation for types.
class IRLiteralType(Enum):
    INTEGER = 0
    FLOATING = 1
    PTR = 2

class IRTerm:
    pass

@dataclass(slots=True)
class IRLiteral(IRTerm):
    literal: str
    type: IRLiteralType

    def dump_ir(self) -> str:
        return f"{self.type.name} {self.literal}"

@dataclass(slots=True)
class IRVariable(IRTerm):
    id: str

    def dump_ir(self) -> str:
        return f"%v{self.id}"

class IRInstructionKind(Enum):
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    EXP = 4

    ALLOC = 9
    LOAD = 10
    STORE = 11
    CONST = 12

    CALL = 25
    RET = 26

type IROperands = Tuple[IRTerm, IRTerm] | IRTerm

@dataclass(slots=True)
class IRInstruction:
    kind: IRInstructionKind
    result: IRVariable
    operands: IROperands

    def dump_ir(self) -> str:
        has_value = self.result is not None
        dump = f"{self.result.dump_ir()} = " if self.result is not None else ""
        dump += self.kind.name
        if self.operands is not None:
            dump += " "
            if isinstance(self.operands, Tuple):
                dump += ", ".join(op.dump_ir() for op in self.operands)
            else:
                dump += self.operands.dump_ir()
        return dump

class IRBuilder:
    __slots__ = [
        "instructions",
        "current_variable_id"
    ]

    instructions: List[IRInstruction]
    current_variable_id: int

    def __init__(self):
        self.instructions = []
        self.current_variable_id = 0

    def new_variable(self) -> IRVariable:
        var = IRVariable(self.current_variable_id)
        self.current_variable_id += 1
        return var

    @singledispatchmethod
    def build(self, ast: ASTNode) -> Optional[IRVariable]:
        raise NotImplementedError(f"IR generation not implemented for {ast}")

    def emit(self, kind: IRInstructionKind, result: IRVariable, operands: IROperands) -> None:
        instruction = IRInstruction(kind=kind, result=result, operands=operands)
        self.instructions.append(instruction)

    @build.register
    def _(self, program: ASTProgram) -> None:
        for node in program.nodes:
            self.build(node)

    @build.register
    def _(self, node: ASTNumber) -> IRVariable:
        result = self.new_variable()
        self.emit(IRInstructionKind.CONST, result, IRLiteral(node.literal, IRLiteralType.INTEGER))
        return result

    @build.register
    def _(self, node: ASTIdentifier) -> IRVariable:
        result = self.new_variable()
        self.emit(IRInstructionKind.LOAD, result, IRLiteral(node.name, IRLiteralType.PTR))
        return result

    @build.register
    def _(self, node: ASTVariableDeclaration) -> None:
        # Allocate new variable
        result = self.new_variable()
        # TODO: ALLOC needs the type it has to allocate (e.g., "INTEGER", "PTR")
        self.emit(IRInstructionKind.ALLOC, result, operands=None)

        # Save expression into new variable
        expression = self.build(node.expression)
        self.emit(IRInstructionKind.STORE, result=None, operands=(result, expression))

    @build.register
    def _(self, node: ASTBinaryExpression) -> IRVariable:
        left = self.build(node.left)
        right = self.build(node.left)

        kind_map = {
            BinaryExpressionKind.PLUS: IRInstructionKind.ADD,
            BinaryExpressionKind.MINUS: IRInstructionKind.SUB,
            BinaryExpressionKind.MULTIPLY: IRInstructionKind.MUL,
            BinaryExpressionKind.DIVIDE: IRInstructionKind.DIV,
            BinaryExpressionKind.EXPONENT: IRInstructionKind.EXP,
        }

        result = self.new_variable()
        self.emit(kind_map[node.operation], result, operands=(left, right))
        return result

    def dump_ir(self) -> str:
        return "\n".join(instr.dump_ir() for instr in self.instructions)
