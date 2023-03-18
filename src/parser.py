import defs
import implang_types
import lexer
import logger

class ParserError(Exception):
    """An error that occured during parsing"""
    def __init__(self, token: lexer.Token, message: str):
        self.token = token
        self.message = message

class ContextManager:
    def __init__(self):
        self.file = None
        self.tokens = []
        self.token_index = 0
        self.stack = []
        self.globals = {}
        self.require_defined_in_future_dict = {}
        self.level = 0

    def init(self, file: str, tokens: list[lexer.Token]):
        self.__init__() # Reset
        self.file = file
        self.tokens = tokens

    def enter_func(self):
        self.stack.append(("func", {}))
        self.level += 1

    def exit_func(self):
        if len(self.stack) == 0:
            raise Exception("Not in function")

        if self.stack[-1][0] != "func":
            raise Exception("Not in function")

        self.stack.pop()
        self.level -= 1

        for name in self.require_defined_in_future_dict:
            if self.require_defined_in_future_dict[name][0] > self.level:
                self.require_defined_in_future_dict[name][0] = self.level

    def enter_if(self):
        self.stack.append(("if", None))

    def exit_if(self):
        if len(self.stack) == 0:
            raise Exception("Not in if block")

        if self.stack[-1][0] != "if":
            raise Exception("Not in if block")

        self.stack.pop()
                
    def enter_loop(self):
        self.stack.append(("loop", None))

    def exit_loop(self):
        if len(self.stack) == 0:
            raise Exception("Not in loop")

        if self.stack[-1][0] != "loop":
            raise Exception("Not in loop")

        self.stack.pop()

    def enter_attribute(self):
        self.stack.append(("attribute", None))

    def exit_attribute(self):
        if len(self.stack) == 0:
            raise Exception("Not in attribute")

        if self.stack[-1][0] != "attribute":
            raise Exception("Not in attribute")

        self.stack.pop()

    def define(self, node):
        if ("if", None) in self.stack:
            raise ParserError(node.name_token, "Cannot define variable or function conditionally! (this will be implemented in the future)")
        
        if node.name in self.require_defined_in_future_dict:
            if self.level <= self.require_defined_in_future_dict[node.name][0]:
                if not isinstance(node, FuncNode):
                    logger.code_error(
                        self.file,
                        self.require_defined_in_future_dict[node.name][1].line,
                        self.require_defined_in_future_dict[node.name][1].column,
                        len(self.require_defined_in_future_dict[node.name][1].value),
                        f"'{node.name}' is required to be a function"
                    )
                    logger.code_note(
                        self.file,
                        node.name_token.line,
                        node.name_token.column,
                        len(node.name_token.value),
                        f"'{node.name}' defined here (bellow the reference) as normal variable"
                    )
                    exit(1)
                
                del self.require_defined_in_future_dict[node.name] # it's defined now
        
        globals_and_locals = {}
        globals_and_locals.update(self.globals)

        for _, v_locals in self.stack:
            if v_locals is not None:
                globals_and_locals.update(v_locals)

        if node.name in globals_and_locals:
            logger.code_error(
                self.file,
                node.name_token.line,
                node.name_token.column,
                len(node.name),
                f"'{node.name}' is already defined"    
            )
            logger.code_note(
                self.file,
                globals_and_locals[node.name].name_token.line,
                globals_and_locals[node.name].name_token.column,
                len(globals_and_locals[node.name].name_token.value),
                f"'{node.name}' defined here"
            )
            exit(1)

        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == "func":
                self.stack[i][1][node.name] = node
                return
        
        self.globals[node.name] = node   

    def delete(self, name: str):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == "func":
                if name in self.stack[i][1]:
                    del self.stack[i][1][name]
                    return
        
        if name in self.globals:
            del self.globals[name]

    def get_type(self, token: lexer.Token) -> lexer.Token:
        globals_and_locals = {}
        globals_and_locals.update(self.globals)

        for _, v_locals in self.stack:
            if v_locals is not None:
                globals_and_locals.update(v_locals)

        if token.value in globals_and_locals:
            if isinstance(globals_and_locals[token.value], FuncNode):
                return globals_and_locals[token.value].func_token
            elif isinstance(globals_and_locals[token.value], VarNode):
                return globals_and_locals[token.value].value_type_token
            else:
                return globals_and_locals[token.value].parameter_type_token

        raise ParserError(token, f"'{token.value}' is not defined")

    def require_defined_in_future_for_func(self, token: lexer.Token):
        globals_and_locals = {}
        globals_and_locals.update(self.globals)

        for _, v_locals in self.stack:
            if v_locals is not None:
                globals_and_locals.update(v_locals)

        if token.value in globals_and_locals:
            return

        if token.value in self.require_defined_in_future_dict:
            if self.require_defined_in_future_dict[token.value][0] > self.level:
                self.require_defined_in_future_dict[token.value] = [self.level, token]
        else:
            self.require_defined_in_future_dict[token.value] = [self.level, token]

    def get_functions(self):
        globals_and_locals = {}
        globals_and_locals.update(self.globals)

        for _, v_locals in self.stack:
            if v_locals is not None:
                globals_and_locals.update(v_locals)
        
        return {k: v for k, v in globals_and_locals.items() if isinstance(v, FuncNode)}

    def end_of_file(self):
        if len(self.require_defined_in_future_dict) > 0:
            for name, (level, token) in self.require_defined_in_future_dict.items():
                logger.code_error(
                    self.file,
                    token.line,
                    token.column,
                    len(token.value),
                    f"'{name}' is not defined"
                )

            exit(1)

ctx_mgr = ContextManager()

class ExprNode:
    def __init__(self, operator_token: lexer.Token, operation: str, left, right):
        self.token = operator_token
        self.operation = operation
        self.left = left
        self.right = right

        if left.value_type in ["INTEGER", "FLOAT"] and right.value_type in ["INTEGER", "FLOAT"]:
            self.value_type = "FLOAT"

            if left.value_type == "INTEGER" and right.value_type == "INTEGER":
                self.value_type = "INTEGER"

        elif left.value_type == "STRING" and right.value_type == "STRING":
            self.value_type = "STRING"

        else:
            raise ParserError(operator_token, f"Illegal operation ('{operator_token.value}') on types '{left.value_type}' and '{right.value_type}'")

    def __str__(self):
        return f"ExprNode({self.operation}, {self.left}, {self.right})"

    def __repr__(self):
        return self.__str__()

class UnaryExprNode:
    def __init__(self, token: lexer.Token, operation: str, right):
        self.token = token # Operator token
        self.operation = operation
        self.right = right

        if right.value_type in ["INTEGER", "FLOAT"]:
            self.value_type = token.value_type
        else:
            raise ParserError(token, f"Illegal unary operation ('{token.value}') on type '{right.value_type}'")

    def __str__(self):
        return f"UnaryExprNode({self.operation}, {self.right})"

    def __repr__(self):
        return self.__str__()

class ValueNode:
    def __init__(self, token: lexer.Token, value_type: str, value: str):
        self.token = token # Value token
        self.value_type = value_type # NOTE: This is the type generated by the lexer (e.g "INTEGER", "FLOAT")
                                     #       and not the final type of the value (e.g "u8", "f32")
        self.value = value

    def __str__(self):
        return f"ValueNode({self.value_type}, {self.value})"

    def __repr__(self):
        return self.__str__()

class ParameterNode:
    def __init__(self, name_token: lexer.Token, parameter_type_token: lexer.Token, name: str, parameter_type: str):
        self.name_token = name_token # Identifier token
        self.parameter_type_token = parameter_type_token # Identifier token (type) - NOTE: this is actally final type (e.g "u8", "f32")
        self.name = name
        self.parameter_type = parameter_type

    def __str__(self):
        return f"ParameterNode({self.name}, {self.parameter_type})"

    def __repr__(self):
        return self.__str__()

class BlockNode:
    def __init__(self, statements: list):
        self.statements = statements

    def __str__(self):
        return f"BlockNode({self.statements})"

    def __repr__(self):
        return self.__str__()

class IfNode:
    def __init__(self, condition: ExprNode, body: BlockNode, else_statement: BlockNode = None):
        self.condition = condition
        self.body = body
        self.else_statement = else_statement

    def __str__(self):
        return f"IfNode({self.condition}, {self.body}, {self.else_statement})"

    def __repr__(self):
        return self.__str__()

class WhileNode:
    def __init__(self, condition: ExprNode, body: BlockNode):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"WhileNode({self.condition}, {self.body})"

    def __repr__(self):
        return self.__str__()

class BreakNode:
    def __str__(self):
        return "BreakNode()"

    def __repr__(self):
        return self.__str__()

class ContinueNode:
    def __str__(self):
        return "ContinueNode()"

    def __repr__(self):
        return self.__str__()

class FuncNode:
    def __init__(self, func_token: lexer.Token, name_token: lexer.Token, return_type_token: lexer.Token, name: str, parameters: list[ParameterNode], return_type: str, body: BlockNode):
        self.func_token = func_token # Keyword (func) token
        self.name_token = name_token # Identifier token
        self.return_type_token = return_type_token # Identifier token (type) - NOTE: this is actally final type (e.g "u8", "f32")
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def __str__(self):
        return f"FuncNode({self.name}, {self.parameters}, {self.body}, {self.return_type})"

    def __repr__(self):
        return self.__str__()

class ReturnNode:
    def __init__(self, value: ExprNode):
        self.value = value

    def __str__(self):
        return f"ReturnNode({self.value})"

    def __repr__(self):
        return self.__str__()

class VariableNode:
    def __init__(self, token: lexer.Token, name: str):
        self.token = token
        self.name = name

        if name in defs.TYPES:
            self.value_type = implang_types.get_base_type(name)
        else:
            self.value_type = implang_types.get_base_type(ctx_mgr.get_type(token).value)

    def __str__(self):
        return f"VariableNode({self.name})"

    def __repr__(self):
        return self.__str__()

class VarNode:
    def __init__(self, name_token, value_type_token, name: str, value_type: str, value: ExprNode):
        self.name_token = name_token # Identifier token
        self.value_type_token = value_type_token # Identifier token (type) - NOTE: this is actally final type (e.g "u8", "f32")
        self.name = name
        self.value_type = value_type
        self.value = value

    def __str__(self):
        return f"VarNode({self.name}, {self.value_type}, {self.value})"

    def __repr__(self):
        return self.__str__()

class AssignmentNode:
    def __init__(self, name: str, value: ExprNode):
        self.name = name
        self.value = value

    def __str__(self):
        return f"AssignmentNode({self.name}, {self.value})"

    def __repr__(self):
        return self.__str__()

class AttributeNode:
    def __init__(self, token: lexer.Token, name: str, value = None):
        self.token = token
        self.name = name
        self.value = value

    def __str__(self):
        return f"AttributeNode({self.name}, {self.value})"

    def __repr__(self):
        return self.__str__()

class CallNode:
    def __init__(self, name_token: lexer.Token, name: str, arguments: list[ExprNode]):
        self.name_token = name_token # Identifier token
        self.name = name
        self.arguments = arguments
        
        if name in ctx_mgr.get_functions():
            self.value_type = implang_types.get_base_type(ctx_mgr.get_functions()[name].return_type)
        else:
            # Dumb scanning all the file for the function definition
            # TODO: Make this better

            for t in range(ctx_mgr.token_index, len(ctx_mgr.tokens)):
                if ctx_mgr.tokens[t].value == name and ctx_mgr.tokens[t-1].value == "func":
                    if ctx_mgr.tokens[t+1].kind == "LPAREN":
                        while ctx_mgr.tokens[t+1].kind != "RPAREN":
                            t += 1
                        else:
                            t += 1
                            if ctx_mgr.tokens[t+1].kind == "ARROW":
                                self.value_type = implang_types.get_base_type(ctx_mgr.tokens[t+2].value)
                            else:
                                self.value_type = None
                        
                        break

                elif ctx_mgr.tokens[t].value == name and ctx_mgr.tokens[t-1].value == "@import_symbol":
                    if ctx_mgr.tokens[t+1].kind == "LPAREN":
                        while ctx_mgr.tokens[t+1].kind != "RPAREN":
                            t += 1
                        else:
                            t += 1
                            if ctx_mgr.tokens[t+1].kind == "ARROW":
                                self.value_type = implang_types.get_base_type(ctx_mgr.tokens[t+2].value)
                            else:
                                self.value_type = None
                        
                        break
            else:
                self.value_type = None
    
    def __str__(self):
        return f"CallNode({self.name}, {self.arguments})"

    def __repr__(self):
        return self.__str__()

class Program:
    def __init__(self):
        self.attributes = []
        self.attribute_append_possible = True
        self.statements = []

    def append(self, statement):
        if isinstance(statement, AttributeNode):
            if not self.attribute_append_possible:
                raise ParserError(statement.token, "Attributes must be at the beginning of the file")
            
            self.attributes.append(statement)
            return

        self.attribute_append_possible = False
        self.statements.append(statement)

    def __str__(self):
        return f"Program(attributes={self.attributes}, statements={self.statements})"

    def __repr__(self):
        return self.__str__()

def parse(file: str, tokens: list[lexer.Token]) -> Program:
    ctx_mgr.init(file, tokens)

    def next_token():
        ctx_mgr.token_index += 1
        return ctx_mgr.tokens[ctx_mgr.token_index - 1]

    def peek_token(n=0):
        try:
            return ctx_mgr.tokens[ctx_mgr.token_index + n]
        except IndexError:
            return None

    def expect_token(kind: str, value: str = None):
        token = peek_token()
        if token.kind != kind:
            if kind in defs.TOKENS_HUMAN_READABLE:
                if token.kind in defs.TOKENS_HUMAN_READABLE:
                    raise ParserError(token, f"Expected {defs.TOKENS_HUMAN_READABLE[kind]}, got {defs.TOKENS_HUMAN_READABLE[token.kind]}")
                else:
                    raise ParserError(token, f"Expected {defs.TOKENS_HUMAN_READABLE[kind]}, got '{token.kind}'")
            
            if token.kind in defs.TOKENS_HUMAN_READABLE:
                raise ParserError(token, f"Expected {kind.lower()}, got {defs.TOKENS_HUMAN_READABLE[token.kind]}")
            else:
                raise ParserError(token, f"Expected {kind.lower()}, got '{token.kind}'")
        
        if value is not None and token.value != value:
            raise ParserError(token, f"Expected token with value '{value}', got {token.value}")
        
        return token

    def skip_newlines() -> int:
        counter = 0

        if peek_token() is None:
            return counter
        
        while peek_token().kind == "NEWLINE":
            next_token()
            counter += 1

            if peek_token() is None:
                return counter

        return counter

    def skip_newlines_or_semicolons() -> int:
        counter = 0
        
        if peek_token() is None:
            return counter

        while peek_token().kind in ["NEWLINE", "SEMICOLON"]:
            next_token()
            counter += 1

            if peek_token() is None:
                return counter

        return counter

    def parse_statement():
        token = peek_token()

        if peek_token() is None:
            return None

        if token.kind in ["NEWLINE", "SEMICOLON"]:
            next_token()
            return parse_statement()

        if token.kind == "KEYWORD":
            if token.value == "if":
                ans = parse_if()
            elif token.value == "while":
                ans = parse_while()
            elif token.value == "break":
                ans = parse_break()
            elif token.value == "continue":
                ans = parse_continue()
            elif token.value == "func":
                ans = parse_func()
            elif token.value == "return":
                ans = parse_return()
            elif token.value == "var":
                ans = parse_var()
            else:
                raise ParserError(token, f"Unexpected keyword '{token.value}'")

        elif token.kind == "IDENTIFIER":
            # this could be an assignment, a function call, or just an expression on its own (this is actually useless)
            if peek_token(1).kind in ["ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MULTIPLY_ASSIGN", "DIVIDE_ASSIGN", "POWER_ASSIGN", "MODULO_ASSIGN", "AND_ASSIGN", "OR_ASSIGN", "XOR_ASSIGN", "BITWISE_AND_ASSIGN", "BITWISE_OR_ASSIGN", "BITWISE_XOR_ASSIGN", "BITWISE_LEFT_SHIFT_ASSIGN", "BITWISE_RIGHT_SHIFT_ASSIGN"]:
                ans = parse_assignment()
            elif peek_token(1).kind == "OPEN_PAREN":
                ans = parse_call()
            else:
                ans = parse_expr()

        elif token.kind == "ATTRIBUTE":
            ans = parse_attribute()

        elif token.kind == "LPAREN":
            ans = parse_expr()

        else:
            raise ParserError(token, f"Unexpected token '{token.value}'")

        if peek_token() is None:
            return ans
        
        if not peek_token().kind in ["NEWLINE", "SEMICOLON"]:
            if peek_token().kind in defs.TOKENS_WITH_VALUE:
                if peek_token().kind in defs.TOKENS_HUMAN_READABLE:
                    raise ParserError(peek_token(), f"Expected newline or semicolon, got {defs.TOKENS_HUMAN_READABLE[peek_token().kind]} {peek_token().value}")
                else:
                    raise ParserError(peek_token(), f"Expected newline or semicolon, got {peek_token().kind.lower()} {peek_token().value}")
            else:
                if peek_token().kind in defs.TOKENS_HUMAN_READABLE:
                    raise ParserError(peek_token(), f"Expected newline or semicolon, got {defs.TOKENS_HUMAN_READABLE[peek_token().kind]}")
                else:
                    raise ParserError(peek_token(), f"Expected newline or semicolon, got {peek_token().kind.lower()}")

        return ans

    def parse_if():
        expect_token("KEYWORD", "if")
        next_token()

        condition = parse_expr()
        skip_newlines()

        expect_token("LBRACE")

        ctx_mgr.enter_if()
        body = parse_block()
        ctx_mgr.exit_if()

        newline_count = skip_newlines()

        if peek_token().kind == "KEYWORD" and peek_token().value == "else":
            next_token()
            skip_newlines()
            
            ctx_mgr.enter_if()

            if peek_token().kind == "KEYWORD" and peek_token().value == "if":
                else_body = parse_if()
            else:
                expect_token("LBRACE")
                else_body = parse_block()
            
            ctx_mgr.exit_if()

            return IfNode(condition, body, else_body)

        ctx_mgr.token_index -= newline_count

        return IfNode(condition, body)

    def parse_while():
        expect_token("KEYWORD", "while")
        next_token()

        condition = parse_expr()
        skip_newlines()

        expect_token("LBRACE")
        
        ctx_mgr.enter_loop()
        body = parse_block()
        ctx_mgr.exit_loop()

        return WhileNode(condition, body)

    def parse_break():
        expect_token("KEYWORD", "break")
        next_token()

        return BreakNode()

    def parse_continue():
        expect_token("KEYWORD", "continue")
        next_token()

        return ContinueNode()

    def parse_func():
        expect_token("KEYWORD", "func")
        func_token = next_token()

        name = expect_token("IDENTIFIER")
        next_token()

        expect_token("LPAREN")
        next_token()

        parameters = []

        try:
            ctx_mgr.enter_func()
        except:
            raise ParserError(func_token, "Cannot define function inside another function")

        while peek_token().kind != "RPAREN":
            skip_newlines()

            arg_name = expect_token("IDENTIFIER")
            next_token()

            expect_token("COLON")
            next_token()

            arg_type = expect_token("IDENTIFIER")
            next_token()

            new_parameter = ParameterNode(arg_name, arg_type, arg_name.value, arg_type.value)

            parameters.append(new_parameter)
            ctx_mgr.define(new_parameter)

            if peek_token().kind == "COMMA":
                next_token()

            skip_newlines()

        next_token()

        return_type = None
        return_type_token = func_token

        if peek_token().kind == "ARROW":
            next_token()

            return_type_token = expect_token("IDENTIFIER")
            return_type = return_type_token.value

            next_token()
        
        skip_newlines()

        ctx_mgr.define(FuncNode(func_token, name, return_type_token, name.value, parameters, return_type, None))

        expect_token("LBRACE")

        body = parse_block()
        ctx_mgr.exit_func()

        ctx_mgr.delete(name.value)
        func_node = FuncNode(func_token, name, return_type_token, name.value, parameters, return_type, body)
        ctx_mgr.define(func_node)

        return func_node

    def parse_return():
        expect_token("KEYWORD", "return")
        next_token()

        if peek_token().kind in ["NEWLINE", "SEMICOLON"]:
            return ReturnNode(ValueNode(peek_token(-1), "NULL", "null"))

        value = parse_expr()

        return ReturnNode(value)

    def parse_var():
        expect_token("KEYWORD", "var")
        next_token()

        name = expect_token("IDENTIFIER")
        next_token()

        expect_token("COLON")
        next_token()

        var_type = expect_token("IDENTIFIER")
        next_token()

        if peek_token().kind in ["NEWLINE", "SEMICOLON"]:
            var_node = VarNode(name, var_type, name.value, var_type.value, None)
            ctx_mgr.define(var_node)

            return var_node

        try:
            assign_token = expect_token("ASSIGN")
        except ParserError as e:
            raise ParserError(e.token, f"Expected newline, semicolon or assigment, got {e.message.split('got')[1].strip()}")
        
        next_token()

        value = parse_expr()

        if implang_types.get_base_type(var_type.value) != value.value_type:
            raise ParserError(assign_token, f"Cannot assign value of type {value.value_type} to variable of type {implang_types.get_base_type(var_type.value)}")

        var_node = VarNode(name, var_type, name.value, var_type.value, value)
        ctx_mgr.define(var_node)

        return var_node

    def parse_assignment():
        name = expect_token("IDENTIFIER")
        next_token()

        assignment_type = next_token()

        if assignment_type.kind not in ["ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MULTIPLY_ASSIGN", "DIVIDE_ASSIGN", "POWER_ASSIGN", "MODULO_ASSIGN", "AND_ASSIGN", "OR_ASSIGN", "XOR_ASSIGN", "BITWISE_AND_ASSIGN", "BITWISE_OR_ASSIGN", "BITWISE_XOR_ASSIGN", "BITWISE_LEFT_SHIFT_ASSIGN", "BITWISE_RIGHT_SHIFT_ASSIGN"]:
            raise ParserError(assignment_type, f"Unexpected token '{assignment_type.value}'")

        value = parse_expr()

        try:
            orig_type = ctx_mgr.get_type(name)
        except ParserError:
            raise ParserError(name, f"Tried to assign to undeclared variable '{name.value}'")

        if implang_types.get_base_type(orig_type.value) != value.value_type:
            raise ParserError(assignment_type, f"Cannot assign value of type {value.value_type} to variable of type {implang_types.get_base_type(orig_type.value)}")

        if assignment_type.kind == "ASSIGN":
            return AssignmentNode(name.value, value)
        else:
            return AssignmentNode(name.value, ExprNode(assignment_type, assignment_type.kind.replace("_ASSIGN", ""), VariableNode(name, name.value), value))

    def parse_call(check_defined=True):
        name = expect_token("IDENTIFIER")
        next_token()

        expect_token("LPAREN")
        next_token()

        if check_defined:
            ctx_mgr.require_defined_in_future_for_func(name)
            #if ctx_mgr.get_type(name).value not in  ["func", "@import_symbol"]:
            #    raise ParserError(name, f"Expected function, got {ctx_mgr.get_type(name)}")

        skip_newlines()

        arguments = []

        while peek_token().kind != "RPAREN":
            arguments.append(parse_expr())

            if peek_token().kind == "COMMA":
                next_token()

            skip_newlines()

        next_token()

        return CallNode(name, name.value, arguments)

    def parse_attribute():
        attr_token = expect_token("ATTRIBUTE")
        next_token()

        if peek_token().kind in ["NEWLINE", "SEMICOLON"]:
            return AttributeNode(attr_token, attr_token.value)
        else:
            ctx_mgr.enter_attribute()

            if peek_token().kind == "IDENTIFIER" and peek_token(1).kind == "LPAREN":
                if not attr_token.value == "@import_symbol":
                    raise ParserError(attr_token, f"Symbol definition is only allowed for imported symbols (attribute '@import_symbol')")
                
                value = parse_call(check_defined=False)

                for arg in value.arguments:
                    if not isinstance(arg, VariableNode):
                        if getattr(arg, "token", None) is not None:
                            raise ParserError(arg.token, f"Expected argument type, got {arg.token.value}")
                        else:
                            raise ParserError(attr_token, f"In imported symbol, expected types of arguments, got {arg}")
                # here we can have also return type
                if peek_token().kind == "ARROW":
                    next_token()
                    return_type = expect_token("IDENTIFIER")
                    next_token()
                    value = FuncNode(
                        attr_token,
                        value.name_token,
                        return_type,
                        value.name,
                        [ParameterNode(None, arg.token, None, arg.name) for arg in value.arguments],
                        return_type.value,
                        # Imported symbol: we do not parse the body
                        None
                    )
                else:
                    value = FuncNode(
                        attr_token,
                        value.name_token,
                        None,
                        value.name,
                        [ParameterNode(None, arg.token, None, arg.name) for arg in value.arguments],
                        None,
                        # Imported symbol: we do not parse the body
                        None
                    )

                ctx_mgr.define(value)
            else:
                value = parse_expr()

            if peek_token().kind not in ["NEWLINE", "SEMICOLON"]:
                raise ParserError(peek_token(), "Expected newline or semicolon after attribute value")

            ctx_mgr.exit_attribute()            
            return AttributeNode(attr_token, attr_token.value, value)

    def parse_block():
        expect_token("LBRACE")
        next_token()

        statements = []

        skip_newlines()

        while peek_token().kind != "RBRACE":
            statements.append(parse_statement())

            skip_newlines_or_semicolons()

        expect_token("RBRACE")
        next_token()

        return BlockNode(statements)

    def parse_expr():
        def parse_power():
            left = parse_unary()

            while peek_token().kind == "POWER":
                power_token = next_token()

                right = parse_unary()

                left = ExprNode(power_token, "POWER", left, right)

            return left

        def parse_multiply():
            left = parse_power()

            while peek_token().kind in ["MULTIPLY", "DIVIDE", "MODULO"]:
                operator = peek_token()
                next_token()

                right = parse_power()

                left = ExprNode(operator, operator.kind, left, right)

            return left

        def parse_add():
            left = parse_multiply()

            while peek_token().kind in ["PLUS", "MINUS"]:
                operator = peek_token()
                next_token()

                right = parse_multiply()

                left = ExprNode(operator, operator.kind, left, right)

            return left

        def parse_comparison():
            left = parse_add()

            while peek_token().kind in ["EQUALS", "NOT_EQUALS", "GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL"]:
                operator = peek_token()
                next_token()

                right = parse_add()

                left = ExprNode(operator, operator.kind, left, right)

            return left
        
        def parse_bitwise():
            left = parse_comparison()

            while peek_token().kind in ["BITWISE_AND", "BITWISE_OR", "BITWISE_XOR", "BITWISE_SHIFT_LEFT", "BITWISE_SHIFT_RIGHT"]:
                operator = peek_token()
                next_token()

                right = parse_comparison()

                left = ExprNode(operator, operator.kind, left, right)

            return left

        def parse_logical():
            left = parse_bitwise()

            while peek_token().kind in ["AND", "OR", "XOR"]:
                operator = peek_token()
                next_token()

                right = parse_bitwise()

                left = ExprNode(operator, operator.kind, left, right)

            return left
        
        def parse_unary():
            if peek_token().kind == "LPAREN":
                next_token()

                expr = parse_expr()

                expect_token("RPAREN")
                next_token()

                return expr
            # check if the expression starts with a unary operator
            elif peek_token().kind in ["PLUS", "MINUS", "NOT", "BITWISE_NOT"]:
                operator = next_token()
                value = parse_unary()

                return UnaryExprNode(operator, operator.kind, value)

            # check if the expression is a function call
            elif peek_token().kind == "IDENTIFIER" and peek_token(1).kind == "LPAREN":
                return parse_call()

            # check if the expression is a variable
            elif peek_token().kind == "IDENTIFIER":
                name = next_token()

                if len(ctx_mgr.stack) == 0:
                    raise ParserError(name, f"Expected fixed value or variable name, got function '{name.value}'")

                if not ctx_mgr.stack[-1][0] == "attribute":
                    if ctx_mgr.get_type(name).value == "func":
                        raise ParserError(name, f"Expected fixed value or variable name, got function '{name.value}'")

                return VariableNode(name, name.value)

            # check if the expression is a int, float, char, string, boolen or null
            elif peek_token().kind in ["INTEGER", "FLOAT", "CHAR", "STRING", "BOOLEAN", "NULL"]:
                token = next_token()

                return ValueNode(token, token.kind, token.value)

            else:
                raise ParserError(peek_token(), "Expected expression")

        # check if the expression is a parenthesized expression
        if peek_token().kind == "LPAREN":
            next_token()

            expr = parse_expr()

            expect_token("RPAREN")
            next_token()

            left = expr
        else:
            left = parse_logical()

        return left

    def parse_program() -> Program:
        p = Program()

        while peek_token() is not None:
            stmt = parse_statement()

            if stmt is not None:
                p.append(stmt)

        ctx_mgr.end_of_file()
        return p

    try:
        return parse_program()
    except ParserError as e:
        logger.code_error(file, e.token.line, e.token.column, len(e.token.value), e.message)
        exit(1)
    except Exception:
        import traceback
        import sys

        logger.cut_here()
        logger.compiler_error(f"An unhandled exception occurred!")

        tb = traceback.format_exc().splitlines()

        for line in tb:
            logger.compiler_error(line)

        print(file=sys.stderr)

        try:
            relevant_code_line = tokens[ctx_mgr.token_index].line
        except IndexError:
            relevant_code_line = tokens[-1].line

        logger.compiler_info(f"Relevant code:")

        if relevant_code_line > 2:
            logger.print_code(file, relevant_code_line - 2, rmindent=False)

        logger.print_code(file, relevant_code_line - 1, rmindent=False)

        with open(file, "r") as f:
            if relevant_code_line < len(f.readlines()):
                logger.print_code(file, relevant_code_line, rmindent=False)

        print(file=sys.stderr)

        logger.compiler_info("Please report this error in the GitHub issue")

        exit(1)
