COMPILER_NAME = "ImpLang Compiler"
COMPILER_VERSION = "0.1.0"
COMPILER_SHORT_NAME = "impc"

OPERATORS = [
    "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "POWER", "MODULO", # arithmetic
    "EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL" # comparison
    "AND", "OR", "XOR", "NOT", # logical
    "BITWISE_AND", "BITWISE_OR", "BITWISE_XOR", "BITWISE_NOT", "BITWISE_SHIFT_LEFT", "BITWISE_SHIFT_RIGHT" # bitwise
]

TOKENS_WITH_VALUE = [
    "IDENTIFIER", "INTEGER", "FLOAT", "STRING", "CHAR", "KEYWORD", "ATTRIBUTE"
]

TOKENS_HUMAN_READABLE = {
    "LPAREN": "opening parenthesis",
    "RPAREN": "closing parenthesis",
    "LBRACE": "opening brace",
    "RBRACE": "closing brace",
    "LBRACKET": "opening bracket",
    "RBRACKET": "closing bracket",
    "ASSIGN": "assignment operator"
}

ASSIGNMENT_OPERATORS = [
    "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MULTIPLY_ASSIGN", "DIVIDE_ASSIGN", "POWER_ASSIGN", "MODULO_ASSIGN",
    "AND_ASSIGN", "OR_ASSIGN", "XOR_ASSIGN",
    "BITWISE_AND_ASSIGN", "BITWISE_OR_ASSIGN", "BITWISE_XOR_ASSIGN",
    "BITWISE_LEFT_SHIFT_ASSIGN", "BITWISE_RIGHT_SHIFT_ASSIGN"
]

KEYWORDS = [
    "if", "else", "while", "break", "continue", "func", "return", "var"
]

TYPES = ["u8", "u16", "u32", "u64", "i8", "i16", "i32", "i64", "f32", "f64", "bool", "char", "str"]

INT_TYPES = {
    # type: (minimum_value, maximum_value) - this is used by the compiler to warn the user if overflow occurs
    "u8": (0, 255),
    "u16": (0, 65535),
    "u32": (0, 4294967295),
    "u64": (0, 18446744073709551615),
    "i8": (-128, 127),
    "i16": (-32768, 32767),
    "i32": (-2147483648, 2147483647),
    "i64": (-9223372036854775808, 9223372036854775807)
}

FLOAT_TYPES = {
    # type: (minimum_value, maximum_value) - this is used by the compiler to warn the user if overflow occurs
    "f32": (-3.4028234663852886e+38, 3.4028234663852886e+38),
    "f64": (-1.7976931348623157e+308, 1.7976931348623157e+308)
}
