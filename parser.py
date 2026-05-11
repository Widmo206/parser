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
from typing import Callable, Type, Any

from enums import TileAction, TokenType, NodeType, Operators
from errors import UnknownTokenError
import events
from matrix import Matrix
from pyscript_dataclasses import Token, ProcessNode, ProcessTree, Instruction, Function, FunctionHolder
from tile_data import TileData


logger = logging.getLogger(__name__)
REFERENCE_CHARS = ascii_letters + digits + "_"
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
# OPERATORS = (
#     '**',
#     '//',
#     '==',
#     '!=',
#     '<=',
#     '>=',
#     '+',
#     '-',
#     '*',
#     '/',
#     '%',
#     '<',
#     '>',
#     )
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
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    }
operator_map = {op.value[0]: op for op in Operators}                  # string -> operator lookup table
operator_initial_characters = {key[0] for key in operator_map.keys()} # chars that prompt the tokenizer to look for operators


class PyScriptSyntaxError(ValueError):
    pass


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


@dataclass
class Parser(object):
    # functions: FunctionHolder
    # variables: dict
    # constants: dict
    file: str
    path: Path

    def __init__(
        self,
        fh: FunctionHolder,
        path: Path = Path("pyscript/test.pyscript")
    ):
        # self.functions = fh
        with open(path, "rt") as file:
            self.file = file.read()
        self.path = path

    def tokenize(self) -> list[Token]:
        tokens = []
        current_token = ""
        token_type = TokenType.NOP
        logger.info(f"Start tokenizing '{self.path}'")
        line = 1
        c = 0
        def add_token(token_type: TokenType, value: Any=None, offset: int=1) -> None:
            nonlocal line
            nonlocal c
            logger.debug(f"Line {line}: found {token_type._name_}")
            tokens.append(Token(token_type, value))
            c += offset
        # if you have a token (like "=") that starts with the same char as an operator (like "=="),
        # one of them will claim that character, even if it's not the correct one
        # solution: put operators first and raise this flag if the check fails
        # flag is lowered immediately after the operator section
        skip_operators = False
        while c < len(self.file):
            current_token = ""
            char = self.file[c]

            if char == "\n":
                # TODO: store line numbers in tokens
                line += 1
                c += 1

            elif char in whitespace:
                #logger.debug(f"Found whitespace at {c}")
                c += 1

            elif char == SINGLE_COMMENT:
                i = 1
                while char != "\n":
                    i += 1
                    char = self.file[c+i]
                c += i+1

            elif char in REFERENCE_START_CHARS:
                i = 0
                while char in REFERENCE_CHARS:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = self.file[c + i]
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
                    char = self.file[c + i]
                if char == ".":
                    # it's a float, it seems
                    is_int = False
                    current_token += char
                    i+=1
                    char = self.file[c + i]
                    while char in digits:
                        # get the decimal part
                        current_token += char
                        i += 1
                        char = self.file[c + i]
                if char == "e":
                    # exponent
                    is_int = False
                    current_token += char
                    i+=1
                    char = self.file[c + i]
                    if char in "+-":
                        current_token += char
                        i += 1
                        char = self.file[c + i]
                    if char in digits:
                        while char in digits:
                            # get the exponent
                            current_token += char
                            i += 1
                            char = self.file[c + i]
                    else:
                        raise SyntaxError(f"Invalid float literal in line {line}: '{current_token}'")

                if is_int:
                    add_token(TokenType.INT_LIT, int(current_token), i)
                else:
                    add_token(TokenType.FLOAT_LIT, float(current_token), i)

            elif char in QUOTES:
                start_quote = char
                for i in range(c+1, len(self.file)-1):
                    char = self.file[i]
                    if char == start_quote:
                        # logger.debug("Found endquote")
                        # TODO: Rework handling of escape characters
                        escaped = False
                        for j in range(i-1, c+1, -1):
                            if self.file[j] == ESCAPE_CHAR:
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
                    char = self.file[c + i]
                if current_token not in operator_map:
                    # prevent infinite loop
                    skip_operators = True
                    continue
                add_token(TokenType.OPERATOR, operator_map[current_token], i)

            elif char in SINGLE_CHAR_TOKENS.keys():
                add_token(SINGLE_CHAR_TOKENS[char])

            else:
                raise UnknownTokenError(f"There are no tokens that start with {repr(char)} (line {line} in '{self.path}')")
            skip_operators = False
        logger.info(f"Finished tokenizing '{self.path}' into {len(tokens)} tokens")
        events.TokenizingFinished(tokens)
        return tokens

    def parse(self, tokens: list[Token], is_root: bool=True) -> ProcessTree:
        """Make sense of the tokens."""
#         linebreaks = (TokenType.SEMICOLON, TokenType.INDENT, TokenType.DEINDENT)
#         lines = []
#         line = []
#         for token in tokens:
#             line.append(token)
#             if token.type in linebreaks:
#                 lines.append(line)
#                 line = []
#         return lines
        process_tree = ProcessTree()
        code_stack = [process_tree.get_root()]
        current_node = code_stack[0]

        while len(tokens) > 0:
            current_token = tokens.pop(0)
            match current_token.type:
                case TokenType.REFERENCE:
                    match tokens[0].type:
                        case TokenType.OPEN_PAREN:
                            # looks like a function call
                            tokens.pop(0) # consume the OPEN_PAREN
                            current_node.add_child(ProcessNode(current_node, NodeType.CALL, current_token))
                            if tokens[0].type == TokenType.CLOSE_PAREN:
                                tokens.pop(0) # no arguments; consume the CLOSE_PAREN
                            else:
                                # step into function arguments
                                current_node = current_node.get_children()[-1]
                                code_stack.append(current_node)
                                # create and step into expression for first arg
                                current_node.add_child(ProcessNode(current_node, NodeType.EXPRESSION, None))
                                current_node = current_node.get_children()[-1]
                                code_stack.append(current_node)
                        case TokenType.ASSIGN:
                            variable = current_token
                            # TODO: check that parent is a CLOSURE
                            # TODO: check if refrence exists and is a variable
                            current_node.add_child(ProcessNode(current_node, NodeType.WRITE, variable))
                            current_node = current_node.get_children()[-1] # step into variable assignment
                            code_stack.append(current_node)
                            tokens.pop(0) # consume the '='
                            # create and step into expression
                            current_node.add_child(ProcessNode(current_node, NodeType.EXPRESSION, None))
                            current_node = current_node.get_children()[-1]
                            code_stack.append(current_node)
                        case _:
                            variable = current_token
                            # TODO: check if reference exists and is a variable or constant
                            current_node.add_child(ProcessNode(current_node, NodeType.READ, variable))
                
                case TokenType.CLOSE_PAREN:
                    match code_stack[-1].get_type(): # TODO: update for other uses of parentheses
                        case NodeType.EXPRESSION:
                            match code_stack[-2].get_type():
                                case NodeType.CALL:
                                    code_stack.pop(-1) # exit EXPRESSION
                                    code_stack.pop(-1) # exit CALL
                                    current_node = code_stack[-1]
                                case _:
                                    code_stack.pop(-1) # exit EXPRESSION
                                    current_node = code_stack[-1]
                        case _:
                            print(f"Current ProcessTree:\n{repr(process_tree)}")
                            raise PyScriptSyntaxError(f"Encountered unmatched parenthesis ({current_token}) while parsing {self.path}.")

                case TokenType.SEMICOLON:
                    match code_stack[-1].get_type(): # TODO: update for other uses of semicolon
                        case NodeType.CLOSURE:
                            pass # end of an instruction
                        case NodeType.EXPRESSION:
                            code_stack.pop(-1) # exit EXPRESSION
                            current_node = code_stack[-1]
                            match current_node.get_type(): # handle the EXPRESSION's parent node
                                case NodeType.CLOSURE:
                                    pass # expression in script/loop/function body
                                case NodeType.DEFINE:
                                    code_stack.pop(-1) # exit DEFINE
                                    current_node = code_stack[-1]
                                case _:
                                    print(f"Current ProcessTree:\n{repr(process_tree)}")
                                    raise PyScriptSyntaxError(f"{self.path} (line X): Unexpected ;")
                        case _:
                            print(f"Current ProcessTree:\n{repr(process_tree)}")
                            raise PyScriptSyntaxError(f"Encountered SEMICOLON ({current_token}) inside an instruction while parsing {self.path}.")
                
                case TokenType.INT_LIT:
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token))
                
                case TokenType.FLOAT_LIT:
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token))

                case TokenType.STRING_LIT:
                    current_node.add_child(ProcessNode(current_node, NodeType.LITERAL, current_token))

                case TokenType.OPERATOR:
                    current_node.add_child(ProcessNode(current_node, NodeType.OPERATION, current_token))

                case TokenType.KEYWORD:
                    match current_token.value:
                        case "var":
                            variable = tokens.pop(0) # declared variable name
                            if variable.type != TokenType.REFERENCE:
                                print(f"Current ProcessTree:\n{repr(process_tree)}")
                                raise PyScriptSyntaxError(f"Line {'n'}: VAR must be followed by a valid variable name")
                            current_node.add_child(ProcessNode(current_node, NodeType.DEFINE, variable))
                            current_node = current_node.get_children()[-1] # step into variable definition
                            code_stack.append(current_node)
                            if tokens[0].type != TokenType.ASSIGN:
                                print(f"Current ProcessTree:\n{repr(process_tree)}")
                                raise PyScriptSyntaxError(f"Line {'n'}: VAR <variable name> must be followed by an assignment operator ('=')")
                            tokens.pop(0) # consume the '='
                            # create and step into expression
                            current_node.add_child(ProcessNode(current_node, NodeType.EXPRESSION, None))
                            current_node = current_node.get_children()[-1]
                            code_stack.append(current_node)
                            

                case _:
                    print(f"Current ProcessTree:\n{repr(process_tree)}")
                    raise NotImplementedError(f"Encountered unimplemented token ({current_token}) while parsing {self.path}.")
        return process_tree


    def compile(self):
        """"Compile" the parsers result into a python-based pseudo-assembly format that can be executed
        by the Player's processor.

        see /pyscript/test.ass for prototype
        """
        raise NotImplementedError("NYI; get the parser done first")


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

    fh = FunctionHolder()
    def hello_world() -> None:
        print("Hello World!")
    fh.add(Function(hello_world), "hello")
    fh.add(Function(print, str))
    fh.add(Function(lambda: print("Failed to give up")), "exit")

    #fh.run("hello")

    parser = Parser(fh)
    tokenized = parser.tokenize()
    #print(tokenized)
    parsed = parser.parse(tokenized)
    print(parsed)
