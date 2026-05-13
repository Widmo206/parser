"""Attempt at making a simple code parser

Created on 2026.01.14
Contributors:
    Widmo
"""

# TODO: Please refactor into one file per class.

from __future__ import annotations
from dataclasses import dataclass
import logging
from string import ascii_letters, digits, whitespace
from pathlib import Path
from typing import Callable, Type, Any, Collection

from enums import TileAction, TokenType, NodeType, Operator, ClosureLabel
from errors import PyScriptSyntaxError, PyScriptNameError, PyScriptTypeError
import events
from matrix import Matrix
from pyscript_types import Constant, Variable, ExternalFunction, AnyValue, AnyFunction, AnyReference, DataType
from pyscript_dataclasses import Token, ProcessNode, ProcessTree, Instruction, Closure
from tile_data import TileData


logger = logging.getLogger(__name__)
REFERENCE_CHARS = ascii_letters + digits + "_" # should these be sets?
REFERENCE_START_CHARS = ascii_letters + "_"
SINGLE_COMMENT = "#"
ESCAPE_CHAR = "\\"
QUOTES = "\"'"
KEYWORDS = (
    "const",
    "var",
    "return",
    "exit",
    )
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
)
operator_map = {op.value[0]: op for op in Operator}                   # string -> operator lookup table
operator_initial_characters = {key[0] for key in operator_map.keys()} # chars that prompt the tokenizer to look for operators



class Processor(object):
    program: list
    stack: list

    def __init__(self, program: list):
        self.program = program
        self.stack = []

    def advance(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData],
    ) -> TileAction | None:
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        logger.debug(
            "Advancing processor for tile %s at (%s, %s)",
            tile_data_matrix.get(self_x, self_y).tile_type,
            self_x,
            self_y,
        )

        # TODO: Advance program based on level state, block at next player action and return it.

        return TileAction.MOVE_FORWARD
        # TileAction.MOVE_BACK
        # TileAction.TURN_LEFT
        # TileAction.TURN_RIGHT
        # TileAction.ATTACK
        # None (idle)


def read_file(path: Path) -> str:
    """Read a file from disk and return the contents as plaintext."""
    text = ""
    with open(path, "rt") as file:
        text = file.read()
    return text


class Parser(object):
    """Handles parsing of PyScript files."""
    path: Path
    external_references: Collection[Constant | ExternalFunction]

    def __init__(
        self,
        path: Path = Path("pyscript/test.pyscript"),
        external_references: Collection[Constant | ExternalFunction] | None=None
    ):
        self.path = path
        if external_references is None:
            self.external_references = []
        else:
            self.external_references = *DATATYPES, *external_references

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
            nonlocal line
            nonlocal c
            token = Token(token_type, value, line)
            tokens.append(token)
            logger.debug(f"Line {line}: found {str(token)}")
            c += length
        # if you have a token (like "=") that starts with the same char as an operator (like "=="),
        # one of them will claim that character, even if it's not the correct one
        # solution: put operators first and raise this flag if the check fails
        # flag is lowered immediately after the operator section
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
                c += i+1

            elif char in REFERENCE_START_CHARS:
                i = 0
                while char in REFERENCE_CHARS:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = source[c + i]
                if current_token in KEYWORDS:
                    token_type = TokenType.KEYWORD
                else:
                    token_type = TokenType.REFERENCE
                add_token(token_type, current_token, i)

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
                while current_token + char in operator_map:
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
        logger.info(f"Finished tokenizing '{self.path}' into {len(tokens)} tokens")
        events.TokenizingFinished(tokens)
        return tokens

    def parse(self, tokens: list[Token]) -> ProcessTree:
        """Turn a list of tokens created by Parser.tokenize into a ProcessTree.

        Parsing handles some of the syntax checking.
        """
        logger.info(f"Start parsing '{self.path}'")
        process_tree = ProcessTree(self.external_references)
        code_stack = [process_tree.get_root()]
        current_node = code_stack[0] # -> ProcessNode of type CLOSURE
        current_closure: Closure = process_tree.get_root().get_value() # ->  Closure (not Any, bc Pylance isn't smart enough)

        def step_into(node_type: NodeType, line: int, value: Any=None) -> None:
            """Create a new node of the specified type as a child of current_node and step into it."""
            nonlocal code_stack
            nonlocal current_node
            if value is None:
                logger.debug(f"Stepping into   {node_type}")
            else:
                logger.debug(f"Stepping into   {node_type} ({repr(value)})")
            new_node = ProcessNode(current_node, node_type, line, value)
            current_node.add_child(new_node)
            current_node = new_node
            code_stack.append(current_node)

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
            current_node = code_stack[-1]

        def ensure_expression() -> None:
            """Ensure the current node is within an expression. Create a new one if it isn't."""
            nonlocal code_stack
            if code_stack[-1].get_type() != NodeType.EXPRESSION:
                step_into(NodeType.EXPRESSION, None)

        while len(tokens) > 0:
            current_token = tokens.pop(0)
            match current_token.type:
                case TokenType.REFERENCE:
                    match tokens[0].type:
                        case TokenType.OPEN_PAREN:
                            # looks like a function call
                            function = current_closure.find(current_token.value)
                            if function is None:
                                raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference {current_token.value}")
                            elif not isinstance(function, AnyFunction):
                                raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not callable")
                            step_into(NodeType.CALL, current_token.line, function)
                            if tokens[1].type == TokenType.CLOSE_PAREN: # no arguments
                                tokens.pop(0) # consume the OPEN_PAREN
                                tokens.pop(0) # consume the CLOSE_PAREN
                                step_out_of(NodeType.CALL)
                            else:
                                step_into(NodeType.EXPRESSION, tokens.pop(0).line) # consumes the OPEN_PAREN + step into first arg
                        case TokenType.ASSIGN:
                            variable = current_closure.find(current_token.value)
                            # TODO: check that parent is a CLOSURE
                            if variable is None:
                                raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference {current_token.value}")
                            elif not isinstance(variable, Variable):
                                raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not a variable")
                            step_into(NodeType.WRITE, current_token.line, variable)
                            step_into(NodeType.EXPRESSION, tokens.pop(0).line) # consumes the '='
                        case _:
                            value = current_closure.find(current_token.value)
                            if value is None:
                                raise PyScriptNameError(f"{self.path} (line {current_token.line}): Unknown reference {current_token.value}")
                            elif not isinstance(value, AnyValue):
                                raise PyScriptTypeError(f"{self.path} (line {current_token.line}): {current_token.value} is not a constant or variable")
                            current_node.add_child(ProcessNode(current_node, NodeType.READ, current_token.line, value))
                
                case TokenType.CLOSE_PAREN:
                    match code_stack[-1].get_type(): # TODO: update for other uses of parentheses
                        case NodeType.EXPRESSION:
                            match code_stack[-2].get_type(): # could this be a simple if?
                                case NodeType.CALL:
                                    step_out_of(NodeType.EXPRESSION)
                                    step_out_of(NodeType.CALL)
                                case _:
                                    step_out_of(NodeType.EXPRESSION)
                        case _:
                            print(f"Current ProcessTree:\n{repr(process_tree)}")
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected )")

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
                                case _:
                                    print(f"Current ProcessTree:\n{repr(process_tree)}")
                                    raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected ;")
                        case _:
                            print(f"Current ProcessTree:\n{repr(process_tree)}")
                            raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected ;")

                case TokenType.INDENT:
                    step_into(NodeType.CLOSURE, Closure(ClosureLabel.MISC))
                    current_closure = current_node.get_value()
                
                case TokenType.DEINDENT:
                    if current_closure.label == ClosureLabel.GLOBAL:
                        raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected {'}'}") # why
                    try:
                        step_out_of(NodeType.CLOSURE)
                    except AssertionError as e:
                        raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): Unexpected {'}'}") from e
                    current_closure = current_closure.get_parent()

                case TokenType.INT_LIT:
                    ensure_expression()
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))
                
                case TokenType.FLOAT_LIT:
                    ensure_expression()
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))

                case TokenType.STRING_LIT:
                    ensure_expression()
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token.line, current_token.value))

                case TokenType.OPERATOR:
                    ensure_expression()
                    current_node.add_child(ProcessNode(current_node, NodeType.OPERATION, current_token.line, current_token.value))

                case TokenType.KEYWORD:
                    match current_token.value:
                        case "var":
                        # \begin{word soup}
                            var_type: Type = Any
                            var_token = tokens.pop(0) # declared variable name
                            if var_token.type != TokenType.REFERENCE:
                                print(f"Current ProcessTree:\n{repr(process_tree)}")
                                raise PyScriptSyntaxError(f"{self.path} (line {current_token.line}): var must be followed by a valid variable name")
                            var_name: str = var_token.value
                            if current_closure.has(var_name):
                                raise PyScriptNameError(f"{self.path} (line {var_token.line}): {var_name} is already defined in the current scope")
                            if tokens[0].type == TokenType.COLON:
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
                            if tokens[0].type != TokenType.ASSIGN:
                                print(f"Current ProcessTree:\n{repr(process_tree)}")
                                raise PyScriptSyntaxError(f"{self.path} (line {var_token.line}): var {var_name} must be followed by assignment operator: =")
                            tokens.pop(0) # consume the '='
                            step_into(NodeType.EXPRESSION, None)
                        # \end{word soup}
                        
                        # TODO add other keywords

                case _:
                    print(f"Current ProcessTree:\n{repr(process_tree)}")
                    raise NotImplementedError(f"{self.path} (line {current_token.line}): Unimplemented token {current_token.type}")
        logger.info(f"Finished parsing '{self.path}'")
        logger.debug(f"Program structure:\n{repr(process_tree)}")
        return process_tree

    def compile(self, tree: ProcessTree) -> ...:
        """"Compile" the parsers result into a python-based pseudo-assembly format that can be executed
        by the Player's processor.

        see /pyscript/test.ass for prototype
        """
        raise NotImplementedError("NYI; get the parser done first")

    def compile_from_file(self) -> ...:
        source = self.get_source()
        tokens = self.tokenize(source)
        tree   = self.parse(tokens)
        return   self.compile(tree)


if __name__ == "__main__":
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

    external_functions = [
        ExternalFunction('hello', None, hello_world),
        ExternalFunction('print', None, print)
    ]

    parser = Parser(external_references=external_functions)
    source = parser.get_source()
    tokens = parser.tokenize(source)
    tree   = parser.parse(tokens)
    print("finished")
