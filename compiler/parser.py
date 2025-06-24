from typing import Optional, List

from .ast import *
from .lexer import Token, TokenKind, OperatorAssociativityKind

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

    def peek(self, lookahead: int = 0) -> Optional[Token]:
        return (self.tokens[self.current + lookahead]
            if self.current + lookahead < len(self.tokens)
            else None)

    def parse(self) -> ASTNode:
        program = ASTProgram()
        while (statement := self.statement()) is not None:
            program.nodes.append(statement)

        return program

    def expression(self, precedence_limit: int = 0) -> ASTExpression:
        token = self.peek()
        if token.kind == TokenKind.IDENTIFIER:
            # <Identifier> + <'('> = function call expression
            if self.peek(lookahead=1).kind == TokenKind.PAREN_OPEN:
                return self.function_call()

            expression = ASTIdentifier(token.literal)
        elif token.kind == TokenKind.NUMBER:
            expression = ASTNumber(token.literal)

        _ = self.advance()
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

    def function_call(self) -> ASTFunctionCall:
        function = ASTIdentifier(self.advance().literal)
        _ = self.advance() # Opening parenthesis

        parameters = []
        token = self.peek()
        while token is not None and token.kind != TokenKind.PAREN_CLOSE:
            # TODO: Error handling, expect commas in between identifiers
            if token.kind == TokenKind.COMMA:
                # Consume the comma
                _ = self.advance()
            else:
                parameters.append(self.expression())

            # Grab next token
            token = self.peek()

        # Function calls may be statements, which end in a semicolon, after the
        # closing parenthesis -- consume the token
        if self.peek().kind == TokenKind.SEMICOLON:
            _ = self.advance()

        return ASTFunctionCall(function, parameters)

    def statement(self) -> Optional[ASTStatement]:
        statement = None

        if (token := self.peek()) is not None and token.kind == TokenKind.IDENTIFIER:
            next_token = self.peek(lookahead=1)
            if next_token.kind == TokenKind.ASSIGNMENT:
                statement = self.declaration()
            elif next_token.kind == TokenKind.PAREN_OPEN:
                statement = self.function_call()

        return statement
