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

from enums import TileAction, TokenType, NodeType
from errors import UnknownTokenError
import events
from matrix import Matrix
from pyscript_token import Token
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
OPERATORS = (
    '**',
    '//',
    '==',
    '!=',
    '<=',
    '>=',
    '+',
    '-',
    '*',
    '/',
    '%',
    '<',
    '>',
    )
operator_initial_characters = {op[0] for op in OPERATORS}
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


def hello_world() -> None:
    print("Hello World!")


@dataclass
class Function(object):
    func: Callable
    arg_types: tuple

    def __init__(self, func: Callable, arg_types: tuple[Type]|Type|None=None):
        self.func = func
        if arg_types is None:
            self.arg_types = tuple()
        elif type(arg_types) == tuple:
            self.arg_types = arg_types
        else:
            self.arg_types = (arg_types,)

    def __call__(self, *args, **kwargs) -> Any:
        self.func(*args, **kwargs)

    @property
    def name(self) -> str:
        """Return the name of this function"""
        return self.func.__name__


# do we even need this?
@dataclass
class FunctionHolder(object):
    functions: dict[str, Function]

    def __init__(self):
        self.functions = {}

    def add(self, function: Function, name_override: str="") -> None:
        """Add a new function to this FunctionHolder.

        The function can be referenced by its name.
        """
        if name_override == "":
            self.functions[function.name] = function
        else:
            self.functions[name_override] = function

    def has(self, function_name: str) -> bool:
        """Check whether a given function is contained in this FunctionHolder."""
        return function_name in self.functions.keys()

    def get(self, function_name: str) -> Function:
        """Retrieve a function by its name."""
        return self.functions[function_name]

    def run(self, function_name: str, *args) -> Any:
        """Run a stored function.

        Return value is determined by the function itself.
        """
        func = self.get(function_name)
        return func(*args)


@dataclass
class Instruction(object):
    function: Callable
    parameters: list


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
class ProcessNode(object):
    _parent: ProcessNode | None
    _type: NodeType
    _value: Any=None
    _children: tuple[ProcessNode, ...] | None=None

    def get_type(self) -> NodeType:
        return self._type

    def get_parent(self) -> ProcessNode | None:
        return self._parent

    def has_children(self):
        return self._children is None

    def get_children(self) -> tuple[ProcessNode, ...]:
        if self._children is None:
            return tuple()
        else:
            return self._children

    def add_child(self, node: ProcessNode):
        if self._children is None:
            self._children = (node,)
        else:
            self._children += (node,)


@dataclass
class ProcessTree(object):
    _root: ProcessNode

    def __init__(self):
        self._root = ProcessNode(None, NodeType.CLOSURE, None, None)

    def get_root(self):
        return self._root


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
                while current_token + char in OPERATORS:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = self.file[c + i]
                if current_token not in OPERATORS:
                    # prevent infinite loop
                    skip_operators = True
                    continue
                add_token(TokenType.OPERATOR, current_token, i)

            elif char in SINGLE_CHAR_TOKENS.keys():
                add_token(SINGLE_CHAR_TOKENS[char])

            else:
                raise UnknownTokenError(f"There are no tokens that start with {repr(char)} (line {line} in '{self.path}')")
            skip_operators = False
        logger.info(f"Finished tokenizing '{self.path}' into {len(tokens)} tokens")
        events.TokenizingFinished(tokens)
        return tokens

    def parse(self, tokens: list[Token], is_root: bool=True):
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
                    if tokens[0].type == TokenType.OPEN_PAREN:
                        # looks like a function call
                        tokens.pop(0) # consume the OPEN_PAREN
                        current_node.add_child(ProcessNode(current_node, NodeType.CALL, current_token.value))
                        current_node = current_node.get_children()[-1]
                        code_stack.append(current_node)
                    else:
                        raise NotImplementedError(f"Encountered non-function REFERENCE ({current_token}) while parsing {self.path}.\nCurrent ProcessTree: {repr(process_tree)}")
                
                case TokenType.CLOSE_PAREN:
                    if code_stack[-1].get_type() == NodeType.CALL: # TODO: update for other uses of parentheses
                        # exit function call
                        code_stack.pop(-1)
                    else:
                        raise SyntaxError(f"Encountered incorrect parenthesis ({current_token}) while parsing {self.path}.\nCurrent ProcessTree: {repr(process_tree)}")

                case TokenType.SEMICOLON:
                    if code_stack[-1].get_type() == NodeType.CLOSURE: # TODO: update for other uses of semicolon
                        pass # end of an instruction
                    else:
                        raise SyntaxError(f"Encountered SEMICOLON ({current_token}) inside an instruction while parsing {self.path}.\nCurrent ProcessTree: {repr(process_tree)}")

                case _:
                    raise NotImplementedError(f"Encountered unimplemented token ({current_token}) while parsing {self.path}.\nCurrent ProcessTree: {repr(process_tree)}")


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

    fh.add(Function(hello_world), "hello")
    fh.add(Function(print, str))
    fh.add(Function(lambda: print("Failed to give up")), "exit")

    #fh.run("hello")

    parser = Parser(fh)
    tokenized = parser.tokenize()
    #print(tokenized)
    parsed = parser.parse(tokenized)
    print(parsed)
