"""Attempt at making a simple code parser.

Here be Dragons (and bad code)
Ye've been warned

Created on 2026.01.14
Contributors:
    Widmo
    
TODO list:
    add checks for unterminated parens/closures/strings/expressions/...
    add arg type/count checking to all functions
    add while loop
    add things I forgot to add
    validate expressions while parsing
    fix bugs
    add lists?
"""

from __future__ import annotations
import logging
from pathlib import Path
from string import ascii_letters, digits, whitespace
from typing import Type, Any, Collection

from enums import TokenType, NodeType, Operator, ClosureLabel, PPUInstruction, Keyword
from errors import PyScriptSyntaxError, PyScriptNameError, PyScriptTypeError, PyScriptError
from pyscript_dataclasses import (
    Constant,
    Variable,
    ExternalFunction,
    Function,
    AnyValue,
    AnyFunction,
    AnyReference,
    AnyFrozenRef,
    DataType,
    Token,
    ProcessNode,
    ProcessTree,
    Closure,
    Instruction,
    Program,
    FunctionArg,
    SubprogramProvider,
)
# ATP we might as well 'from pyscript_dataclasses import *'

logger = logging.getLogger(__name__)
REFERENCE_CHARS = ascii_letters + digits + "_" # should these be sets?
REFERENCE_START_CHARS = ascii_letters + "_"
SINGLE_COMMENT = "#"
ESCAPE_CHAR = "\\"
QUOTES = "\"'"
BOOLEANS = {
    "true": True,
    "false": False,
}
KEYWORDS = {
    "const":  Keyword.CONST,
    "var":    Keyword.VAR,
    "func":   Keyword.FUNC,
    "if":     Keyword.IF,
    "else":   Keyword.ELSE,
    "while":  Keyword.WHILE,
    "return": Keyword.RETURN,
}
TOKEN_PAIRS = {
    TokenType.OPEN_PAREN: TokenType.CLOSE_PAREN,
    TokenType.INDENT:     TokenType.DEINDENT,
}
SINGLE_CHAR_TOKENS = {
    "{": TokenType.INDENT,
    "}": TokenType.DEINDENT,
    "=": TokenType.ASSIGN,
    "(": TokenType.OPEN_PAREN,
    ")": TokenType.CLOSE_PAREN,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
}
DATATYPES = (
    DataType("str", str),
    DataType("int", int),
    DataType("float", float),
    DataType("bool", bool)
)
operator_map = {op.value[0]: op for op in Operator}                   # string -> operator lookup table
operator_initial_characters = {key[0] for key in operator_map.keys()} # chars that prompt the tokenizer to look for operators
operator_all_characters = {c for c in "".join(operator_map.keys())}   # this is horrible


def read_file(path: Path) -> str:
    """Read a file from disk and return the contents as plaintext."""
    text = ""
    with open(path, "rt") as file:
        text = file.read()
    return text


class Parser(object):
    """Handles parsing of PyScript files."""
    path: Path
    external_references: Collection[AnyFrozenRef]
    token_count: int

    def __init__(
        self,
        path: Path = Path("pyscript/test.pyscript"),
        external_references: Collection[AnyFrozenRef] | None=None
    ):
        self.path = path
        if external_references is None:
            self.external_references = []
        else:
            self.external_references = *DATATYPES, *external_references
        self.token_count = 0

    @staticmethod
    def parse_expression(expression: ProcessNode):
        logger.debug(f"Start parsing EXPRESSION ({expression.get_value()})")
        assert expression.get_type() == NodeType.EXPRESSION
        # Step 1: find any unary minus
        previous_node: ProcessNode | None = None
        nodes = list(expression.get_children())
        for node in nodes:
            if (node.get_type() == NodeType.OPERATION
                and node.get_value() == Operator.SUB
                and (previous_node is None
                     or previous_node.get_type() == NodeType.OPERATION)
                ):
                node._value = Operator.NEGATIVE # yes I'm modifying a private attribute
        # Step 2: Rearrange expression into postfix notation; thanks to:
        # https://www.geeksforgeeks.org/dsa/convert-infix-expression-to-postfix-expression/
        operation_stack = []
        result = []
        while nodes != []:
            node = nodes[0] # not popped here because sometimes the same node is evaluated >once
            # logger.debug(node.format())
            if node.get_type() == NodeType.OPERATION:
                if operation_stack == []:
                    # logger.debug("Stack empty! -> in it goes")
                    operation_stack.append(nodes.pop(0))
                else:
                    current_op: Operator = node.get_value()
                    stack_op:   Operator = operation_stack[-1].get_value()
                    if (stack_op.priority < current_op.priority
                        or stack_op.priority == current_op.priority
                        and not current_op.is_right_to_left
                    ):
                        # logger.debug("Lower priority! -> pop the stack")
                        result.append(operation_stack.pop(-1))
                    else:
                        # logger.debug("Higher priority! -> in it goes")
                        operation_stack.append(nodes.pop(0))
            else:
                # logger.debug("Operand! -> out it goes")
                result.append(nodes.pop(0))
        while operation_stack != []: # pop remaining operators
            result.append(operation_stack.pop(-1))
        expression._children = tuple(result) # modifying a private attribute *again*
        logger.debug(f"Finish parsing EXPRESSION ({expression.get_value()})")

    def get_source(self) -> str:
        """Load a pyscript source file fromm disk."""
        return read_file(self.path)

    def tokenize(self, source: str) -> list[Token]:
        """Cut the source code into processable tokens."""
        tokens = []
        current_token = ""
        token_type = TokenType.NOP
        logger.info(f"Start tokenizing '{self.path}'")
        line = 1
        c = 0
        def add_token(token_type: TokenType, value: Any=None, length: int=1) -> None:
            """Create a specified Token and add it to the list.
            
            Helper function for Parser.tokenize
            """
            nonlocal line
            nonlocal c
            token = Token(token_type, value, line)
            tokens.append(token)
            logger.debug(f"Line {line}: found {str(token)}")
            c += length
        # if you have a token (like "=") that starts with the same char as an operator (like "=="),
        # one of them will claim that character, even if it's not the correct one
        # solution: put operators first and raise this flag if the check fails
        # flag is lowered immediately after the operator is checked
        skip_operators = False
        while c < len(source):
            current_token = ""
            char = source[c]

            if char == "\n":
                line += 1
                c += 1

            elif char in whitespace:
                #logger.debug(f"Found whitespace at {c}")
                c += 1

            elif char == SINGLE_COMMENT:
                i = 1
                # skip the rest of the line
                while char != "\n":
                    i += 1
                    char = source[c+i]
                line += 1
                c += i+1

            elif char in REFERENCE_START_CHARS:
                i = 0
                while char in REFERENCE_CHARS:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = source[c + i]
                if current_token in KEYWORDS:
                    add_token(TokenType.KEYWORD, KEYWORDS[current_token], i)
                elif current_token in BOOLEANS:
                    add_token(TokenType.BOOL_LIT, BOOLEANS[current_token], i)
                else:
                    add_token(TokenType.REFERENCE, current_token, i)
                

            elif char in digits:
                is_int = True
                i = 0
                while char in digits:
                    # get the rest of integer part
                    current_token += char
                    i += 1
                    char = source[c + i]
                if char == ".":
                    # it's a float, it seems
                    is_int = False
                    current_token += char
                    i+=1
                    char = source[c + i]
                    while char in digits:
                        # get the decimal part
                        current_token += char
                        i += 1
                        char = source[c + i]
                if char == "e":
                    # exponent
                    is_int = False
                    current_token += char
                    i+=1
                    char = source[c + i]
                    if char in "+-":
                        current_token += char
                        i += 1
                        char = source[c + i]
                    if char in digits:
                        while char in digits:
                            # get the exponent
                            current_token += char
                            i += 1
                            char = source[c + i]
                    else:
                        raise PyScriptSyntaxError(f"{self.path} (line {line}): Invalid float literal: {current_token}")

                if is_int:
                    add_token(TokenType.INT_LIT, int(current_token), i)
                else:
                    add_token(TokenType.FLOAT_LIT, float(current_token), i)

            elif char in QUOTES:
                start_quote = char
                for i in range(c+1, len(source)-1):
                    char = source[i]
                    if char == start_quote:
                        # logger.debug("Found endquote")
                        # TODO: Rework handling of escape characters
                        escaped = False
                        for j in range(i-1, c+1, -1):
                            if source[j] == ESCAPE_CHAR:
                                escaped = not escaped
                            else:
                                break
                        if escaped:
                            # logger.debug("Quote escaped")
                            current_token += char
                        else:
                            # logger.debug(f"length of str is {i - c - 1}")
                            c = i + 1
                            break
                    else:
                        current_token += char
                # offset already handled
                add_token(TokenType.STRING_LIT, current_token, 0)

            elif char in operator_initial_characters and not skip_operators:
                i = 0
                while char in operator_all_characters:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = source[c + i]
                if current_token not in operator_map:
                    # prevent infinite loop
                    skip_operators = True
                    continue
                add_token(TokenType.OPERATOR, operator_map[current_token], i)

            elif char in SINGLE_CHAR_TOKENS:
                add_token(SINGLE_CHAR_TOKENS[char])

            else:
                raise PyScriptSyntaxError(f"{self.path} (line {line}): invalid character {repr(char)}")
            skip_operators = False

        self.token_count = len(tokens)
        logger.info(f"Finished tokenizing '{self.path}' into {self.token_count} tokens")
        return tokens

    def parse(self, tokens: list[Token]) -> ProcessTree:
        """Turn a list of tokens created by Parser.tokenize into a ProcessTree.

        Parsing handles some of the syntax checking.
        """
        logger.info(f"Start parsing '{self.path}'")
        process_tree = ProcessTree(self.external_references)
        code_stack = [process_tree.get_root()]
        current_node = code_stack[0] # -> ProcessNode of type CLOSURE
        current_closure: Closure = process_tree.get_root().get_value() # -> Closure (not Any, bc Pylance isn't smart enough)
        expressions = []

        def step_into(node_type: NodeType, line: int, value: Any) -> None:
            """Create a new node of the specified type as a child of current_node and step into it."""
            nonlocal code_stack
            nonlocal current_node
            nonlocal current_closure
            if node_type == NodeType.EXPRESSION and value == None:
                value = len(expressions) # expression counter
            if value is None:
                logger.debug(f"Stepping into   {node_type}")
            else:
                logger.debug(f"Stepping into   {node_type} ({repr(value)})")
            if node_type == NodeType.CLOSURE:
                assert isinstance(value, Closure)
                assert value.get_parent() is current_closure
                current_closure = value
            new_node = ProcessNode(current_node, node_type, line, value)
            current_node.add_child(new_node)
            current_node = new_node
            code_stack.append(current_node)
            if node_type == NodeType.EXPRESSION:
                expressions.append(current_node)

        def step_out_of(node_type: NodeType | Any) -> None:
            """Step out of a node on the stack.

            Checks whether the node being popped is of the correct type.
            """
            nonlocal code_stack
            nonlocal current_node
            exited_node = code_stack.pop(-1)
            if exited_node.get_value() is None:
                logger.debug(f"Stepping out of {exited_node.get_type()}")
            else:
                logger.debug(f"Stepping out of {exited_node.get_type()} ({repr(exited_node.get_value())})")
            if node_type is not Any:
                assert exited_node.get_type() == node_type
            if node_type == NodeType.CLOSURE:
                assert isinstance(exited_node.get_value(), Closure)
                current_closure = exited_node.get_value()
            current_node = code_stack[-1]

        def ensure_expression(current_line: int) -> None:
            """Ensure the current node is within an expression. Create a new one if it isn't."""
            nonlocal code_stack
            if code_stack[-1].get_type() != NodeType.EXPRESSION:
                step_into(NodeType.EXPRESSION, current_line, None)
        
        def require_closure(current_line: int, action_description: str):
            """Raise a PyScriptSyntaxError if a given node is placed outside of a closure.
            
            Message format: ~You cannot {action_description} here;
            """
            nonlocal code_stack
            if code_stack[-1].get_type() != NodeType.CLOSURE:
                raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): You cannot {action_description} here; maybe you forgot a semicolon?")
        
        def is_next_token(token_type: TokenType, lookahead: int=0) -> bool:
            nonlocal tokens
            return tokens[lookahead].type == token_type

        try:
            while len(tokens) > 0:
                current_token = tokens.pop(0)
                match current_token.type:
                    case TokenType.REFERENCE:
                        match tokens[0].type:
                            case TokenType.OPEN_PAREN:
                                # looks like a function call
                                function = current_closure.find(current_token.value)
                                if function is None:
                                    raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference: {current_token.value}")
                                elif not isinstance(function, AnyFunction):
                                    raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not callable")
                                if code_stack[-1].get_type() == NodeType.PARENTHESIS:
                                    step_into(NodeType.EXPRESSION, current_token.line, None)
                                step_into(NodeType.CALL, current_token.line, function)
                                if is_next_token(TokenType.CLOSE_PAREN, 1): # no arguments
                                    tokens.pop(0) # consume the OPEN_PAREN
                                    tokens.pop(0) # consume the CLOSE_PAREN
                                    step_out_of(NodeType.CALL)
                                else:
                                    step_into(NodeType.EXPRESSION, tokens.pop(0).line, None) # consumes the OPEN_PAREN + step into first arg
                            case TokenType.ASSIGN:
                                require_closure(current_token.line, "assign a value to a variable")
                                variable = current_closure.find(current_token.value)
                                if variable is None:
                                    raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference: {current_token.value}")
                                elif not isinstance(variable, Variable):
                                    raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not a variable")
                                step_into(NodeType.WRITE, current_token.line, variable)
                                step_into(NodeType.EXPRESSION, tokens.pop(0).line, None) # consumes the '='
                            case _:
                                value = current_closure.find(current_token.value)
                                if value is None:
                                    raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference: {current_token.value}")
                                elif not isinstance(value, AnyValue):
                                    raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not a constant or variable")
                                if code_stack[-1].get_type() == NodeType.PARENTHESIS:
                                    step_into(NodeType.EXPRESSION, current_token.line, None)
                                ensure_expression(current_token.line)
                                current_node.add_child(ProcessNode(current_node, NodeType.READ, current_token.line, value))
                    
                    case TokenType.OPEN_PAREN:
                        if code_stack[-1].get_type() == NodeType.PARENTHESIS:
                            step_into(NodeType.EXPRESSION, current_token.line, None)
                        step_into(NodeType.PARENTHESIS, current_token.line, None)

                    case TokenType.CLOSE_PAREN:
                        if code_stack[-1].get_type() != NodeType.EXPRESSION:
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): unexpected )")
                        step_out_of(NodeType.EXPRESSION)
                        match code_stack[-1].get_type(): # TODO: update for other uses of parentheses
                            case NodeType.CALL:
                                step_out_of(NodeType.CALL)
                            case NodeType.PARENTHESIS:
                                step_out_of(NodeType.PARENTHESIS)
                                if code_stack[-1].get_type() == NodeType.CONDITION:
                                    bracket = tokens.pop(0)
                                    if bracket.type != TokenType.INDENT:
                                        raise PyScriptSyntaxError(f"{self.path} (line {bracket.line}): expected closure after if statement")
                                    step_into(NodeType.CLOSURE, bracket.line, Closure(ClosureLabel.CONDITIONAL, current_closure))
                            case _:
                                raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected )")

                    case TokenType.COMMA:
                        if code_stack[-1].get_type() != NodeType.EXPRESSION or code_stack[-2].get_type() != NodeType.CALL:
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected ,")
                        else:
                            step_out_of(NodeType.EXPRESSION)
                            step_into(NodeType.EXPRESSION, current_token.line, None)

                    case TokenType.SEMICOLON:
                        match code_stack[-1].get_type(): # TODO: update for other uses of semicolon
                            case NodeType.CLOSURE:
                                pass # end of an instruction
                            case NodeType.EXPRESSION:
                                step_out_of(NodeType.EXPRESSION)
                                match current_node.get_type(): # handle the EXPRESSION's parent node
                                    case NodeType.CLOSURE:
                                        pass # expression in script/loop/function body
                                    case NodeType.DEFINE:
                                        step_out_of(NodeType.DEFINE)
                                    case NodeType.WRITE:
                                        step_out_of(NodeType.WRITE)
                                    case NodeType.RETURN:
                                        step_out_of(NodeType.RETURN)
                                    case _:
                                        raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected ;")
                            case NodeType.RETURN:
                                step_out_of(NodeType.RETURN)
                            case _:
                                raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected ;")

                    case TokenType.INDENT:
                        require_closure(current_token.line, "create a closure")
                        step_into(NodeType.CLOSURE, current_token.line, Closure(ClosureLabel.MISC, current_closure))
                    
                    case TokenType.DEINDENT:
                        if current_closure.label == ClosureLabel.GLOBAL:
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected {'}'}") # why
                        elif current_closure.label == ClosureLabel.CONDITIONAL:
                            # just making sure; (index -2 bc we haven't left the closure yet)
                            assert code_stack[-2].get_type() == NodeType.CONDITION
                        try:
                            step_out_of(NodeType.CLOSURE)
                        except AssertionError as e:
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected {'}'}") from e
                        parent_node = code_stack[-1]
                        if parent_node.get_type() == NodeType.DEFINE:
                            step_out_of(NodeType.DEFINE)
                        elif parent_node.get_type() == NodeType.CONDITION:
                            # just making sure I didn't mess up elsewhere
                            components = parent_node.get_children()
                            assert 2 <= len(components) <= 3
                            assert components[0].get_type() == NodeType.PARENTHESIS
                            assert components[1].get_type() == NodeType.CLOSURE
                            if len(components) == 3:
                                assert components[2].get_type() == NodeType.CLOSURE
                                step_out_of(NodeType.CONDITION)
                            else:
                                if is_next_token(TokenType.KEYWORD) and tokens[0].value == Keyword.ELSE:
                                    tokens.pop(0) # pop the else (no need to verify bc we just checked)
                                    bracket = tokens.pop(0)
                                    if bracket.type != TokenType.INDENT:
                                        raise PyScriptSyntaxError(f"{self.path} (line {bracket.line}): expected closure after else statement")
                                    step_into(NodeType.CLOSURE, bracket.line, Closure(ClosureLabel.CONDITIONAL, current_closure))
                                else:
                                    parent_node.add_child(ProcessNode(parent_node, NodeType.CLOSURE, parent_node.get_line(), Closure(ClosureLabel.CONDITIONAL, current_closure))) # add an empty else block

                    case TokenType.INT_LIT:
                        ensure_expression(current_token.line)
                        current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))
                    
                    case TokenType.FLOAT_LIT:
                        ensure_expression(current_token.line)
                        current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))

                    case TokenType.STRING_LIT:
                        ensure_expression(current_token.line)
                        current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))
                    
                    case TokenType.BOOL_LIT:
                        ensure_expression(current_token.line)
                        current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))

                    case TokenType.OPERATOR:
                        ensure_expression(current_token.line)
                        current_node.add_child(ProcessNode(current_node, NodeType.OPERATION, current_token.line, current_token.value))

                    case TokenType.KEYWORD:
                        match current_token.value:
                            case Keyword.VAR:
                            # \begin{word soup}
                                require_closure(current_token.line, "define a variable")
                                var_type: Type = Any # idek what Pylance is complaining about here
                                var_token = tokens.pop(0) # declared variable name
                                if var_token.type != TokenType.REFERENCE:
                                    raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): var must be followed by a valid name")
                                var_name: str = var_token.value
                                if current_closure.has(var_name):
                                    raise PyScriptNameError(f"{self.path} (line {var_token.line}): {var_name} is already defined in the current scope")
                                if is_next_token(TokenType.COLON):
                                    tokens.pop(0) # consume the :
                                    type_token = tokens.pop(0)
                                    if type_token.type != TokenType.REFERENCE:
                                        raise PyScriptSyntaxError(f"{self.path} (line {var_token.line}): incomplete type declaration of var {var_name}")
                                    type_ref = current_closure.find(type_token.value)
                                    if type_ref is None:
                                        raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown type {current_token.value}")
                                    elif not isinstance(type_ref, DataType):
                                        raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {type_token.value} is not a data type")
                                    var_type = type_ref.type
                                variable = Variable(var_name, var_type, None)
                                current_closure.add(variable)
                                step_into(NodeType.DEFINE, var_token.line, variable)
                                if not is_next_token(TokenType.ASSIGN):
                                    raise PyScriptSyntaxError(f"{self.path} (line {var_token.line}): var {var_name} must be followed by assignment operator: =")
                                step_into(NodeType.EXPRESSION, tokens.pop(0).line, None) # consumes the '='
                            
                            # word soup 2: electric boogaloo
                            case Keyword.CONST: # literally copy-pasted the case for var
                                require_closure(current_token.line, "define a constant")
                                var_type: Type = Any # idek what Pylance is complaining about here
                                var_token = tokens.pop(0) # declared variable name
                                if var_token.type != TokenType.REFERENCE:
                                    raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): const must be followed by a valid name")
                                var_name: str = var_token.value
                                if current_closure.has(var_name):
                                    raise PyScriptNameError(f"{self.path} (line {var_token.line}): {var_name} is already defined in the current scope")
                                if is_next_token(TokenType.COLON):
                                    tokens.pop(0) # consume the :
                                    type_token = tokens.pop(0)
                                    if type_token.type != TokenType.REFERENCE:
                                        raise PyScriptSyntaxError(f"{self.path} (line {var_token.line}): incomplete type declaration of const {var_name}")
                                    type_ref = current_closure.find(type_token.value)
                                    if type_ref is None:
                                        raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown type {current_token.value}")
                                    elif not isinstance(type_ref, DataType):
                                        raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {type_token.value} is not a data type")
                                    var_type = type_ref.type
                                variable = Constant(var_name, var_type, None)
                                current_closure.add(variable)
                                step_into(NodeType.DEFINE, var_token.line, variable)
                                if not is_next_token(TokenType.ASSIGN):
                                    raise PyScriptSyntaxError(f"{self.path} (line {var_token.line}): const {var_name} must be followed by assignment operator: =")
                                step_into(NodeType.EXPRESSION, tokens.pop(0).line, None) # consumes the '='

                            # I should be banned from using Pathon again
                            case Keyword.FUNC:
                                require_closure(current_token.line, "define a function")
                                name_token = tokens.pop(0) # function name
                                func_name = name_token.value
                                logger.debug(f"Defining func {func_name}")
                                # Verify that name is free
                                if name_token.type != TokenType.REFERENCE:
                                    raise PyScriptSyntaxError(f"{self.path} (line {name_token.line}): func must be followed by a valid name")
                                if current_closure.has(func_name):
                                    raise PyScriptNameError(f"{self.path} (line {name_token.line}): {func_name} is already defined in the current scope")
                                # Find arguments
                                arguments: list[FunctionArg] = []
                                open_paren = tokens.pop(0)
                                if open_paren.type != TokenType.OPEN_PAREN:
                                    raise PyScriptSyntaxError(f"{self.path} (line {open_paren.line}): func {name_token.value} must be followed by a parenthesis with function arguments")
                                while True:
                                    arg_token = tokens.pop(0)
                                    arg_type: Type = Any
                                    # Verify arg name
                                    if arg_token.type != TokenType.REFERENCE:
                                        raise PyScriptSyntaxError(f"{self.path} (line {arg_token.line}): '{arg_token.value}' is not a valid argument name")
                                    arg_name = arg_token.value
                                    # check for type declaration
                                    if is_next_token(TokenType.COLON):
                                        tokens.pop(0) # consume :
                                        type_token = tokens.pop(0)
                                        # Verify that it's a valid type
                                        if type_token.type != TokenType.REFERENCE:
                                            raise PyScriptSyntaxError(f"{self.path} (line {arg_token.line}): incomplete type declaration of argument {arg_name}")
                                        type_ref = current_closure.find(type_token.value)
                                        if type_ref is None:
                                            raise PyScriptNameError(f"{self.path} (line {type_token.line}): Unknown type {type_token.value}")
                                        elif not isinstance(type_ref, DataType):
                                            raise PyScriptTypeError(f"{self.path} (line {type_token.line}): {type_token.value} is not a data type")
                                        arg_type = type_ref.type
                                    # finalize argument
                                    arguments.append((arg_name, arg_type))
                                    # check if there's another one
                                    separator_token = tokens.pop(0)
                                    if separator_token.type == TokenType.CLOSE_PAREN:
                                        break
                                    elif separator_token.type == TokenType.COMMA:
                                        continue
                                    else:
                                        raise PyScriptSyntaxError(f"{self.path} (line {separator_token.line}): expected ',' or ')' in function definition")
                                logger.debug(f"Found arguments: {arguments}")
                                # check for the arrow: func name(args) -> (return_type)
                                arrow_token = tokens.pop(0)
                                if arrow_token.type != TokenType.OPERATOR or arrow_token.value != Operator.ARROW:
                                    raise PyScriptSyntaxError(f"{self.path} (line {arrow_token.line}): expected '->' after function arguments")
                                # check for the return type
                                open_paren = tokens.pop(0)
                                if open_paren.type != TokenType.OPEN_PAREN:
                                    raise PyScriptSyntaxError(f"{self.path} (line {open_paren.line}): expected parenthesis with function return type")
                                return_type_token = tokens.pop(0)
                                if return_type_token.type != TokenType.REFERENCE:
                                    raise PyScriptSyntaxError(f"{self.path} (line {return_type_token.line}): expected function return type")
                                type_ref = current_closure.find(return_type_token.value)
                                if type_ref is None:
                                    raise PyScriptNameError(f"{self.path} (line {return_type_token.line}): Unknown type {return_type_token.value}")
                                elif not isinstance(type_ref, DataType):
                                    raise PyScriptTypeError(f"{self.path} (line {return_type_token.line}): {return_type_token.value} is not a data type")
                                return_type = type_ref.type
                                logger.debug(f"found return type: {return_type}")
                                close_paren = tokens.pop(0)
                                if close_paren.type != TokenType.CLOSE_PAREN:
                                    raise PyScriptSyntaxError(f"{self.path} (line {close_paren.line}): expected ')' after return type")
                                # check for function body
                                open_closure = tokens.pop(0)
                                if open_closure.type != TokenType.INDENT:
                                    raise PyScriptSyntaxError(f"{self.path} (line {open_closure.line}): expected function body after definition")
                                # create function with values found above
                                function = Function(func_name, return_type, None, arguments)
                                current_closure.add(function)
                                step_into(NodeType.DEFINE, current_token.line, function)
                                # set up closure
                                function_closure = Closure(ClosureLabel.FUNCTION, current_closure)
                                for arg in arguments:
                                    function_closure.add(Variable(arg[0], arg[1], None))
                                step_into(NodeType.CLOSURE, open_closure.line, function_closure)
                                current_closure = function_closure
                            
                            case Keyword.RETURN:
                                for node in reversed(code_stack): # make sure we're in a function
                                    if node.get_type() == NodeType.CLOSURE:
                                        if node.get_value().label == ClosureLabel.FUNCTION:
                                            break
                                else:
                                    raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): unexpected return outside function definition")
                                step_into(NodeType.RETURN, current_token.line, None)
                            
                            case Keyword.IF:
                                step_into(NodeType.CONDITION, current_token.line, None)
                                paren = tokens.pop(0)
                                if paren.type != TokenType.OPEN_PAREN:
                                    raise PyScriptSyntaxError(f"{self.path} (line {paren.line}): expected (condition) after if statement")
                                step_into(NodeType.PARENTHESIS, paren.line, None)
                                step_into(NodeType.EXPRESSION, paren.line, None)
                                # handle the rest when exiting
                                # honestly could have done something similar for Functions
                                # and I *thought* about it... should've listened to myself

                            case Keyword.ELSE:
                                raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): unexpected else statement")

                            # TODO add other keywords
                            case _:
                                raise NotImplementedError(f"{self.path} (line {current_token.line}): Unimplemented keyword {current_token.value}")

                    case _:
                        raise NotImplementedError(f"{self.path} (line {current_token.line}): Unimplemented token {current_token.type}")
            for expression in expressions:
                Parser.parse_expression(expression)
        except Exception as err:
            logger.error(f"Parsing failed due to an exception:\n\n{err.__class__.__name__}: {err}\n\nCurrent ProcessTree:\n{repr(process_tree)}")
            raise
        logger.info(f"Finished parsing '{self.path}'")
        logger.debug(f"Program structure:\n{repr(process_tree)}")
        return process_tree

    def compile(self, tree: ProcessTree) -> Program:
        """"Compile" the parsers result into a list of Instructions that can be executed by the Player's processor."""
        logger.info(f"Start compiling '{self.path}'")

        def compile_subprogram(closure_node: ProcessNode, initial_references: list[AnyFrozenRef]) -> SubprogramProvider:
            assert closure_node.get_type() == NodeType.CLOSURE
            program = [
                # Instruction(PPUInstruction.STRT, None, 0) # it *should* get replaced at runtime
            ]
            for child in closure_node.get_children():
                program += _r_compile(child)
            if program[-1].instruction != PPUInstruction.EXIT:
                last_line = closure_node.get_children()[-1].get_line()
                program.append(Instruction(PPUInstruction.EXIT, False, last_line)) # EXIT needed to exit closure; False = no return value

            # It's fine to pass the refs directly since they're only placeholders and will be replaced at runtime by the Processor
            return SubprogramProvider(program, closure_node.get_value().label, initial_references)

        def _r_compile(node: ProcessNode) -> list[Instruction]:
            logger.debug(f"Now compiling {node}")
            instructions: list[Instruction] = []
            match node.get_type():
                case NodeType.CLOSURE:
                    instructions.append(Instruction(
                        PPUInstruction.EXEC,
                        compile_subprogram(node, []),
                        node.get_line()
                    ))
                case NodeType.EXPRESSION:
                    for child in node.get_children():
                        instructions += _r_compile(child)
                case NodeType.READ:
                    instructions.append(Instruction(PPUInstruction.READ, node.get_value(), node.get_line()))
                case NodeType.WRITE:
                    instructions += _r_compile(node.get_children()[0])
                    instructions.append(Instruction(PPUInstruction.WRIT, node.get_value(), node.get_line()))
                case NodeType.DEFINE:
                    match node.get_value():
                        case Constant():
                            instructions += _r_compile(node.get_children()[0])
                            instructions.append(Instruction(PPUInstruction.DEFC, node.get_value(), node.get_line()))
                        case Variable():
                            instructions += _r_compile(node.get_children()[0])
                            instructions.append(Instruction(PPUInstruction.DEFV, node.get_value(), node.get_line()))
                        case Function():
                            function: Function = node.get_value()
                            closure_node: ProcessNode = node.get_children()[0] # DEFINE Function should only have one child
                            args = []
                            for arg in function.args:
                                args.append(Variable(arg[0], arg[1], None))
                            function_body = compile_subprogram(closure_node, args)
                            function.program = function_body
                            instructions.append(Instruction(PPUInstruction.DEFF, function, node.get_line()))
                        case _:
                            raise NotImplementedError
                case NodeType.LITERAL:
                    instructions.append(Instruction(PPUInstruction.PUSH, node.get_value(), node.get_line()))
                case NodeType.CALL:
                    arg_count = 0
                    for child in node.get_children():
                        instructions += _r_compile(child)
                        arg_count += 1
                    match node.get_value():
                        case ExternalFunction():
                            instructions.append(Instruction(PPUInstruction.CALL, (node.get_value(), arg_count), node.get_line()))
                        case Function():
                            # remember to make the processor assign the values
                            instructions.append(Instruction(PPUInstruction.CALL, (node.get_value(), arg_count), node.get_line()))
                            instructions.append(Instruction(PPUInstruction.EXEC, node.get_value().program, node.get_line()))
                        case _:
                            raise NotImplementedError
                case NodeType.OPERATION:
                    instructions.append(Instruction(PPUInstruction.EVAL, node.get_value(), node.get_line()))
                case NodeType.PARENTHESIS: # tuples aren't planned; parser should ensure there's only one child (EXPRESSION)
                    instructions += _r_compile(node.get_children()[0])
                case NodeType.RETURN:
                    if node.has_children():
                        instructions += _r_compile(node.get_children()[0])
                        instructions.append(Instruction(PPUInstruction.EXIT, True, node.get_line()))
                    else:
                        instructions.append(Instruction(PPUInstruction.EXIT, False, node.get_line()))
                case NodeType.CONDITION:
                    # if not node.has_children(): # nah, this should get caught by the parser
                    components = node.get_children()
                    assert len(components) == 3
                    instructions += _r_compile(components[0]) # condition
                    instructions.append(Instruction(PPUInstruction.IFEL, None, node.get_line()))
                    instructions.append(Instruction( # if True
                        PPUInstruction.EXEC,
                        compile_subprogram(components[1], []),
                        components[1].get_line()
                    ))
                    instructions.append(Instruction( # if False
                        PPUInstruction.EXEC,
                        compile_subprogram(components[2], []),
                        components[2].get_line()
                    ))
                case _:
                    raise NotImplementedError(f"{self.path} (line {node.get_line()}): Unimplemented node {node.get_type()}")
            return instructions
        
        root = tree.get_root()
        lst = []
        for branch in root.get_children():
            lst += _r_compile(branch)
        program = Program(lst, ClosureLabel.GLOBAL, self.external_references)
        logger.info(f"Finish compiling '{self.path}'")
        logger.debug(f"Compiled program:\n{str(program)}")
        return program
    
    def compile_from_file(self) -> Program:
        source = self.get_source()
        tokens = self.tokenize(source)
        tree   = self.parse(tokens)
        return   self.compile(tree)


if __name__ == "__main__":
    from processor import Processor # conditional import at the bottom of a script >:)
    # clear the log file (doesn't happen otherwise, idk why)
    with open("latest.log", "wt") as _:
        pass
    logging.basicConfig(
        filename='latest.log',
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)03d | %(levelname)-5s | %(name)-10s | %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
        )

    def hello_world() -> None:
        print("Hello World!")

    NoneType = type(None)
    external_functions = [
        ExternalFunction('hello', NoneType, hello_world, False),
        ExternalFunction('print', NoneType, print, False)
    ]
    PPU = Processor()

    parser  = Parser(external_references=external_functions)
    source  = parser.get_source()
    tokens  = parser.tokenize(source)
    tree    = parser.parse(tokens)
    program = parser.compile(tree)
    PPU.load(program)
    PPU.advance(None)
    PPU.advance(None)
    print("\n<Parser test finished>")
