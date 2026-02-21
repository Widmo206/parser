"""Attempt at making a simple code parser

Created on 2026.01.14
Contributors:
    Widmo
"""

from dataclasses import dataclass
import logging
from string import ascii_letters, digits, whitespace
from pathlib import Path
from typing import Callable, Type, Any

from enums import TokenType
from errors import UnknownTokenError
import events
from pyscript_token import Token

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

    def run(self):
        ...


@dataclass
class Parser(object):
    functions: FunctionHolder
    variables: dict
    constants: dict
    file: str
    path: Path

    def __init__(
        self,
        fh: FunctionHolder,
        path: Path = Path("pyscript/test.pyscript")
    ):
        self.functions = fh
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

            if char == SINGLE_COMMENT:
                i = 1
                while char != "\n":
                    i += 1
                    char = self.file[c]
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
                if char == "\n":
                    # TODO: store line numbers in tokens
                    line += 1
                    c += 1
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
        instruction = []
        while len(tokens) > 0:
            ...
            break

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
    print(tokenized)
    parsed = parser.parse(tokenized)
    print(parsed)
