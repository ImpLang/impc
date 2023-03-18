import sys

import defs
import lexer

COLORS = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}

def syntax_highlight(code: str) -> str:
    tokens = list(lexer.lex(code))[::-1]

    for token in tokens:
        if isinstance(token, lexer.LexerError):
            continue
        
        if token.kind == "KEYWORD":
            code = code[:token.position] + \
                    COLORS["BLUE"] + COLORS["BOLD"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                    code[token.position + len(token.value):]

        elif token.kind == "IDENTIFIER":
            if token.value in defs.TYPES:
                code = code[:token.position] + \
                        COLORS["MAGENTA"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                        code[token.position + len(token.value):]
            else:
                code = code[:token.position] + \
                        COLORS["YELLOW"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                        code[token.position + len(token.value):]

        elif token.kind in ["STRING", "CHAR"]:
            code = code[:token.position] + \
                    COLORS["GREEN"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                    code[token.position + len(token.value):]

        elif token.kind in ["INTEGER", "FLOAT"]:
            code = code[:token.position] + \
                    COLORS["CYAN"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                    code[token.position + len(token.value):]

        elif token.kind == "ATTRIBUTE":
            code = code[:token.position] + \
                    COLORS["MAGENTA"] + COLORS["BOLD"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                    code[token.position + len(token.value):]

        elif token.kind in ["BOOLEAN", "NULL"]:
            code = code[:token.position] + \
                    COLORS["BLUE"] + code[token.position:token.position + len(token.value)] + COLORS["RESET"] + \
                    code[token.position + len(token.value):]

    return code

def print_code(file: str, line: int, rmindent: bool = True):
    with open(file, "r") as f:
        lines = f.readlines()

        if rmindent:
            code_pretty = syntax_highlight(lines[line - 1].strip())
        else:
            code_pretty = syntax_highlight(lines[line - 1].rstrip())
        
        print(f"{COLORS['BLACK'] + COLORS['BOLD']}{line:>4} |{COLORS['RESET']} {code_pretty}", file=sys.stderr)

def print_underline(file: str, line: int, position: int, lenght: int):
    with open(file, "r") as f:
        lines = f.readlines()
        position -= len(lines[line - 1]) - len(lines[line - 1].lstrip())
    
    additional_spaces = len(str(line)) - 4 if len(str(line)) > 4 else 0
    print(" " * (6 + position + additional_spaces) + f"{COLORS['RED']}^{COLORS['RESET']}" * lenght, file=sys.stderr)


def compiler_error(msg: str):
    print(f"{defs.COMPILER_SHORT_NAME}: {COLORS['RED'] + COLORS['BOLD']}error:{COLORS['RESET']} {msg}", file=sys.stderr)

def compiler_warning(msg: str):
    print(f"{defs.COMPILER_SHORT_NAME}: {COLORS['YELLOW'] + COLORS['BOLD']}warning:{COLORS['RESET']} {msg}", file=sys.stderr)

def compiler_info(msg: str):
    print(f"{defs.COMPILER_SHORT_NAME}: {COLORS['CYAN'] + COLORS['BOLD']}info:{COLORS['RESET']} {msg}", file=sys.stderr)

def compiler_debug(msg: str):
    print(f"{defs.COMPILER_SHORT_NAME}: {COLORS['MAGENTA'] + COLORS['BOLD']}debug:{COLORS['RESET']} {msg}", file=sys.stderr)

###################

def code_error(file: str, line: int, position: int, lenght: int, msg: str):
    print(f"{file}:{line}:{position} {COLORS['RED'] + COLORS['BOLD']}error:{COLORS['RESET']} {msg}", file=sys.stderr)
    print(file=sys.stderr)

    print_code(file, line)
    print_underline(file, line, position, lenght)

    print(file=sys.stderr)

def code_warning(file: str, line: int, position: int, lenght: int, msg: str):
    print(f"{file}:{line}:{position} {COLORS['YELLOW'] + COLORS['BOLD']}warning:{COLORS['RESET']} {msg}", file=sys.stderr)
    print(file=sys.stderr)

    print_code(file, line)
    print_underline(file, line, position, lenght)

    print(file=sys.stderr)

def code_note(file: str, line: int, position: int, lenght: int, msg: str):
    print(f"{file}:{line}:{position} {COLORS['CYAN'] + COLORS['BOLD']}note:{COLORS['RESET']} {msg}", file=sys.stderr)
    print(file=sys.stderr)

    print_code(file, line)
    print_underline(file, line, position, lenght)

    print(file=sys.stderr)

def cut_here():
    cut_here_string = f"[ {COLORS['BOLD']}CUT HERE{COLORS['RESET']} ]"
    print(f"{cut_here_string:-^88}", file=sys.stderr)
