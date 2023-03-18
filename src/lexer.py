import re
from typing import Iterable

import defs
import logger

class Token:
    def __init__(self, kind: str, value: str, position: int, line: int, column: int):
        self.kind = kind
        self.value = value
        self.position = position # The position of the token in the input string
        self.line = line # The line of the token in the input string
        self.column = column # The column of the token in the input string

    def __str__(self) -> str:
        if self.kind in defs.TOKENS_WITH_VALUE:
            return f"Token({self.kind}, {self.value}, line={self.line}, column={self.column})"

        return f"Token({self.kind}, line={self.line}, column={self.column})"

    def __repr__(self) -> str:
        return self.__str__()

class LexerError:
    """A syntax error that occured during lexing"""
    def __init__(self, line: int, column: int, char: str):
        self.line = line
        self.column = column
        self.char = char

def lex(input_text: str) -> Iterable[Token]:
    def xstrip(test: str) -> str:
        if test.strip() == "":
            return ""
        
        return test

    input_text = "\n".join([xstrip(line) for line in input_text.split("\n")])

    tokens = [
        ("ATTRIBUTE", r"\@[a-zA-z][a-zA-z0-9_]*"),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*"),
        ("FLOAT", r"([0-9]*)?\.[0-9]+"),
        ("INTEGER", r"[0-9]+"),
        ("STRING", r"\".*?\""),
        ("CHAR", r"\'(\\.|[^\\'])\'"),

        ("ARROW", r"\-\>"),

        ("COMMENT", r"\#.*"),
        ("NEWLINE", r"\n"),
        ("WHITESPACE", r"\s+"),

        ("EQUALS", r"\=\="),
        ("NOT_EQUALS", r"\!\="),
        ("LESS_THAN", r"\<"),
        ("GREATER_THAN", r"\>"),
        ("LESS_THAN_OR_EQUAL", r"\<\="),
        ("GREATER_THAN_OR_EQUAL", r"\>\="),

        ("ASSIGN", r"\="),
        ("PLUS_ASSIGN", r"\+\="),
        ("MINUS_ASSIGN", r"\-\="),
        ("MULTIPLY_ASSIGN", r"\*\="),
        ("DIVIDE_ASSIGN", r"\/\="),
        ("POWER_ASSIGN", r"\^\="),
        ("MODULO_ASSIGN", r"\%\="),
        ("AND_ASSIGN", r"\&\&\="),
        ("OR_ASSIGN", r"\|\|\="),
        ("XOR_ASSIGN", r"\^\^\="),
        ("BITWISE_AND_ASSIGN", r"\&\="),
        ("BITWISE_OR_ASSIGN", r"\|\="),
        ("BITWISE_XOR_ASSIGN", r"\^\="),
        ("BITWISE_LEFT_SHIFT_ASSIGN", r"\<\<\="),
        ("BITWISE_RIGHT_SHIFT_ASSIGN", r"\>\>\="),

        ("PLUS", r"\+"),
        ("MINUS", r"\-"),
        ("MULTIPLY", r"\*"),
        ("DIVIDE", r"\/"),
        ("POWER", r"\^"),
        ("MODULO", r"\%"),

        ("AND", r"\&\&"),
        ("OR", r"\|\|"),
        ("XOR", r"\^\^"),
        ("NOT", r"\!"),

        ("BITWISE_AND", r"\&"),
        ("BITWISE_OR", r"\|"),
        ("BITWISE_XOR", r"\^"),
        ("BITWISE_NOT", r"\~"),
        ("BITWISE_LEFT_SHIFT", r"\<\<"),
        ("BITWISE_RIGHT_SHIFT", r"\>\>"),

        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),

        ("COMMA", r"\,"),
        ("SEMICOLON", r"\;"),
        ("COLON", r"\:")
    ]

    token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in tokens)

    line = 1
    column = 1

    pos = 0
    while pos < len(input_text):
        match = re.match(token_regex, input_text[pos:])
        if match:
            kind = match.lastgroup
            value = match.group()

            if kind == "COMMENT":
                pass
            elif kind == "WHITESPACE":
                pass
            elif kind == "NEWLINE":
                column = 1
                line += 1

                yield Token(kind, value, pos, line, column)
            elif kind == "IDENTIFIER":
                if value in defs.KEYWORDS:
                    kind = "KEYWORD"
                
                for t in ["true", "false"]:
                    if value == t:
                        kind = "BOOLEAN"
                        break
                
                if value == "null":
                    kind = "NULL"

                yield Token(kind, value, pos, line, column)
            else:
                yield Token(kind, value, pos, line, column)

            pos += len(value)

            if kind != "NEWLINE":
                column += len(value)
        else:
            yield LexerError(line, column, input_text[pos])
            pos += 1
            column += 1

def lex_file(file: str) -> list[Token]:
    syntax_error_count = 0
    temp = []

    with open(file, "r") as f:
        for token in lex(f.read()):
            if isinstance(token, LexerError):
                logger.code_error(file, token.line, token.column, 1, f"Undefined token: {token.char}")
                syntax_error_count += 1

            temp.append(token)

    if syntax_error_count > 0:
        logger.compiler_error(f"{syntax_error_count} lexer error(s) while analyzing '{file}'")
        raise SystemExit(1)
    
    return temp
