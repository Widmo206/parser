"""Attempt at making a simple code parser

Created on 2026.01.14
Contributors:
    Widmo
"""


from typing import Callable, Type, Any
from dataclasses import dataclass
from string import ascii_letters, digits, whitespace
from enum import Enum
import logging


logger = logging.getLogger(__name__)
ESCAPE_CHAR = "\\"
QUOTES = "\"'"
KEYWORDS = (
    "return",
    )


class UnknownTokenError(ValueError):
    """Raised when the Parser finds a token that is broken or doesn't exist."""
    pass


def hello_world() -> None:
    print("Hello World!")


class TokenType(Enum):
    NOP         = 0
    KEYWORD     = 1
    REFERENCE   = 2
    OPEN_PAREN  = 3
    CLOSE_PAREN = 4
    NEWLINE     = 5
    STRING_LIT  = 6
    INT_LIT     = 7
    FLOAT_LIT   = 8
    COMMA       = 9
    PLUS        = 10
    DASH        = 11
    STAR        = 12
    SLASH       = 13


def log_token(token_type: TokenType, char: int) -> None:
    logger.debug(f"Found token {token_type._name_} at {char}")


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


@dataclass(frozen=True)
class Token(object):
    type: TokenType
    value: Any

    def __repr__(self):
        if self.value is None:
            return f"Token({self.type.name})"
        else:
            return f"Token({self.type.name}, {repr(self.value)})"


@dataclass
class Parser(object):
    functions: FunctionHolder
    file: str
    path: str

    def __init__(self, fh: FunctionHolder, path: str="code.txt"):
        self.functions = fh
        with open(path, "rt") as file:
            self.file = file.read()
        self.path = path

    def tokenize(self) -> list[Token]:
        tokens = []
        current_token = ""
        token_type = TokenType.NOP

        logger.info(f"Start tokenizing {self.path}")

        c = 0
        while c < len(self.file):
            current_token = ""
            char = self.file[c]

            if char in whitespace:
                logger.debug(f"Found whitespace at {c}")
                c += 1
                continue

            elif char in ascii_letters:
                i = 0
                while char in ascii_letters:
                    # get the rest of the token
                    current_token += char
                    i += 1
                    char = self.file[c + i]
                if current_token in KEYWORDS:
                    token_type = TokenType.KEYWORD
                    log_token(TokenType.KEYWORD, c)
                else:
                    token_type = TokenType.REFERENCE
                    log_token(TokenType.REFERENCE, c)
                tokens.append(Token(token_type, current_token))
                c += i
                continue

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
                        raise SyntaxError(f"Invalid float literal at position {c + i}")

                if is_int:
                    tokens.append(Token(TokenType.INT_LIT, int(current_token)))
                    log_token(TokenType.INT_LIT, c)
                else:
                    tokens.append(Token(TokenType.FLOAT_LIT, float(current_token)))
                    log_token(TokenType.FLOAT_LIT, c)
                c += i
                continue

            elif char in QUOTES:
                start_quote = char
                for i in range(c+1, len(self.file)-1):
                    char = self.file[i]
                    if char == start_quote:
                        logger.debug("Found endquote")
                        escaped = False
                        for j in range(i-1, c+1, -1):
                            if self.file[j] == ESCAPE_CHAR:
                                escaped = not escaped
                            else:
                                break
                        if escaped:
                            logger.debug("Quote escaped")
                            current_token += char
                        else:
                            logger.debug(f"length of str is {i - c - 1}")
                            c = i + 1
                            break
                    else:
                        current_token += char
                tokens.append(Token(TokenType.STRING_LIT, current_token))
                log_token(TokenType.STRING_LIT, c)
                continue

            elif char == "(":
                log_token(TokenType.OPEN_PAREN, c)
                tokens.append(Token(TokenType.OPEN_PAREN, None))
                c += 1
                continue

            elif char == ")":
                log_token(TokenType.CLOSE_PAREN, c)
                tokens.append(Token(TokenType.CLOSE_PAREN, None))
                c += 1
                continue

            elif char == "\n":
                log_token(TokenType.NEWLINE, c)
                tokens.append(Token(TokenType.NEWLINE, None))
                c += 1
                continue

            elif char == "+":
                log_token(TokenType.PLUS, c)
                tokens.append(Token(TokenType.PLUS, None))
                c += 1
                continue

            elif char == "-":
                log_token(TokenType.DASH, c)
                tokens.append(Token(TokenType.DASH, None))
                c += 1
                continue

            elif char == "*":
                log_token(TokenType.STAR, c)
                tokens.append(Token(TokenType.STAR, None))
                c += 1
                continue

            elif char == "/":
                log_token(TokenType.SLASH, c)
                tokens.append(Token(TokenType.SLASH, None))
                c += 1
                continue

            elif char == ",":
                log_token(TokenType.COMMA, c)
                tokens.append(Token(TokenType.COMMA, None))
                c += 1
                continue

            else:
                raise UnknownTokenError(f"There are no tokens that start with '{char}' (character no. {c} in {self.path})")
        logger.info(f"Finished tokenizing {self.path} into {len(tokens)} tokens")
        return tokens


if __name__ == "__main__":
    # clear the log file (doesn't happen otherwise, idk why)
    with open("latest.log", "wt") as _:
        pass
    logging.basicConfig(filename='latest.log', level=logging.DEBUG)

    fh = FunctionHolder()

    fh.add(Function(hello_world), "hello")
    fh.add(Function(print, str))
    fh.add(Function(lambda: print("Failed to give up")), "exit")

    #fh.run("hello")

    parser = Parser(fh)
    print(parser.tokenize())
