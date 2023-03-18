import defs

def get_base_type(specific_type: str):
    if specific_type in defs.INT_TYPES:
        return "INTEGER"
    elif specific_type in defs.FLOAT_TYPES:
        return "FLOAT"
    elif specific_type == "bool":
        return "BOOLEAN"
    elif specific_type == "char":
        return "CHAR"
    elif specific_type == "str":
        return "STRING"

    return specific_type # if it's not a base type, it's a custom type
