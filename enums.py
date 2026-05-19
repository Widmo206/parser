"""Centralized location for easy enum access.

Created on 2026.01.30
Contributors:
    Widmo
    Romcode
"""

from __future__ import annotations

from enum import auto, Enum
import logging
from pathlib import Path
from typing import Any, NamedTuple

from PIL import Image
from PIL.Image import Image as PILImage

from common import print_enum
from errors import UnknownDirectionError, UnknownTileTypeError


logger = logging.getLogger(__name__)


class Direction(Enum):
    UP    = ("U",  0, -1, Image.Transpose.ROTATE_90)
    DOWN  = ("D",  0,  1, Image.Transpose.ROTATE_270)
    LEFT  = ("L", -1,  0, Image.Transpose.ROTATE_180)
    RIGHT = ("R",  1,  0, None)

    character: str
    x: int
    y: int
    image_transpose: Image.Transpose | None

    def __new__(
        cls,
        character: str,
        x: int,
        y: int,
        image_transpose: Image.Transpose | None = None,
    ) -> Direction:
        obj = object.__new__(cls)
        obj._value_ = character

        obj.character = character
        obj.x = x
        obj.y = y
        obj.image_transpose = image_transpose

        return obj

    @classmethod
    def normalize(cls, value: Direction | str) -> Direction:
        """Safely convert a Direction or character string to a Direction."""
        if isinstance(value, cls):
            return value
        try:
            return Direction(value)
        except UnknownDirectionError:
            logger.error("No direction matching value %s", value)
            return cls.RIGHT

    @classmethod
    def _missing_(cls, value: Any) -> Direction:
        raise UnknownDirectionError("No direction matching value %s", value)

    def __neg__(self) -> Direction:
        for direction in Direction:
            if direction.x == -self.x and direction.y == -self.y:
                return direction

        raise ValueError("Invalid direction negation")

    def rotate(self, clockwise: bool = False) -> Direction:
        if clockwise:
            new_x, new_y = -self.y, self.x
        else:
            new_x, new_y = self.y, -self.x

        for direction in Direction:
            if direction.x == new_x and direction.y == new_y:
                return direction

        raise ValueError("Invalid direction rotation")


class TileAction(Enum):
    MOVE_FORWARD = auto()
    MOVE_BACK    = auto()
    TURN_LEFT    = auto()
    TURN_RIGHT   = auto()
    ATTACK       = auto()
    DECAY        = auto()


class TileType(Enum):
    BLOCKED    = ("X", None,                          None,                     False, 2)
    EMPTY      = ("O", "sprites/tile_background.png", None,                     True,  2)
    PLAYER     = ("P", "sprites/tile_background.png", "sprites/player.png",     False, 0)
    PLAYER_KEY = ("p", "sprites/tile_background.png", "sprites/player_key.png", False, 0)
    ENEMY      = ("E", "sprites/tile_background.png", "sprites/enemy.png",      False, 1)
    ENEMY_KEY  = ("e", "sprites/tile_background.png", "sprites/enemy_key.png",  False, 1)
    FLAG       = ("F", "sprites/tile_background.png", "sprites/flag.png",       True,  2)
    KEY        = ("K", "sprites/tile_background.png", "sprites/key.png",        True,  2)
    DOOR       = ("D", "sprites/tile_background.png", "sprites/door.png",       False, 2)
    ATTACK     = ("A", "sprites/tile_background.png", "sprites/attack.png",     True,  2)
    WIN        = ("W", "sprites/tile_background.png", "sprites/win.png",        True,  2)

    character: str
    image: PILImage | None
    is_walkable: bool
    action_priority: int # smaller number = higher priority

    def __new__(
        cls,
        character: str,
        background_path: str | None,
        foreground_path: str | None,
        is_walkable: bool,
        action_priority: int,
    ) -> TileType:
        bg = Image.open(Path(background_path)).convert("RGBA") if background_path else None
        fg = Image.open(Path(foreground_path)).convert("RGBA") if foreground_path else None

        if bg is None:
            image = fg
        elif fg is None:
            image = bg
        else:
            image = bg.copy()
            image.alpha_composite(fg)

        obj = object.__new__(cls)
        obj._value_ = character

        obj.character = character
        obj.image = image
        obj.is_walkable = is_walkable
        obj.action_priority = action_priority

        return obj

    @classmethod
    def normalize(cls, value: TileType | str) -> TileType:
        """Safely convert a TileType or character string to a TileType."""
        if isinstance(value, cls):
            return value
        try:
            return TileType(value)
        except UnknownTileTypeError:
            logger.error("No tile type matching value %s", value)
            return cls.EMPTY

    @classmethod
    def _missing_(cls, value: Any) -> TileType:
        raise UnknownTileTypeError("No tile type matching value %s", value)


class Keyword(Enum):
    CONST  = auto()
    VAR    = auto()
    FUNC   = auto()
    IF     = auto()
    ELSE   = auto()
    WHILE  = auto()
    RETURN = auto()


class TokenType(Enum):
    NOP         = auto() # pass
    KEYWORD     = auto()
    REFERENCE   = auto()
    # control flow
    SEMICOLON   = auto() # ;
    INDENT      = auto() # {
    DEINDENT    = auto() # }
    # statements
    ASSIGN      = auto() # =
    OPEN_PAREN  = auto() # (
    CLOSE_PAREN = auto() # )
    COMMA       = auto() # ,
    COLON       = auto() # :
    OPERATOR    = auto() # math operators like + * % ==
    # data types
    STRING_LIT  = auto() # "abcd"
    INT_LIT     = auto() # 1234
    FLOAT_LIT   = auto() # 1.2e3
    BOOL_LIT    = auto() # true / false
#     # operators
#     PLUS        = auto() # +
#     MINUS       = auto() # -
#     STAR        = auto() # *
#     SLASH       = auto() # /


class NodeType(Enum):
    """Used by Parser to organize a list of tokens into a ProcessTree."""
    CLOSURE     = auto()
    CONDITION   = auto()
    PARENTHESIS = auto()
    EXPRESSION  = auto()
    READ        = auto()
    WRITE       = auto()
    DEFINE      = auto()
    LITERAL     = auto()
    CALL        = auto()
    RETURN      = auto()
    OPERATION   = auto()


class OperatorMixin(NamedTuple):
    chars:            str
    priority:         int
    # when chaining, whether the rightmost instance should be evaluated first
    is_right_to_left: bool = False
    # whether it only acts on the value immediately after, instead of before and after
    is_unary:         bool = False


class Operator(OperatorMixin, Enum):
    EQUALS    = ('==', 5)
    NOTEQUALS = ('!=', 5)
    LESS_EQ   = ('<=', 5)
    MORE_EQ   = ('>=', 5)
    LESS_THAN = ('<',  5)
    MORE_THAN = ('>',  5)

    POW       = ('**', 1, True)
    NEGATIVE  = ('-',  2, False, True) # N.B.: has to be above SUB, as it uses the same string
    FLOOR_DIV = ('//', 3)
    ADD       = ('+',  4)
    SUB       = ('-',  4)
    MULT      = ('*',  3)
    DIV       = ('/',  3)
    MOD       = ('%',  3)

    ARROW     = ('->', 0) # not exactly an operator, but this was the simplest way to handle it

    def __repr__(self):
        return f"Operator.{self.name}"


class ClosureLabel(Enum):
    GLOBAL      = auto()
    FUNCTION    = auto()
    LOOP        = auto()
    CONDITIONAL = auto()
    MISC        = auto()


class PPUInstruction(Enum):
    # PyScript Processing Unit
    STRT = auto() # start of a subprogram; should be replaced with a corresponding EXEC before it reaches the processor
    PUSH = auto() # push a value onto the stack
    PULL = auto() # pull a value from the stack
    READ = auto() # read from a const or var
    WRIT = auto() # write to a var
    CALL = auto() # call an ExternalFunction
    EVAL = auto() # evaluate a math operation
    DEFC = auto() # define a constant
    DEFV = auto() # define a variable
    DEFF = auto() # define a function
    EXEC = auto() # step into a subprogram (anything in a closure)
    EXIT = auto() # exit a subprogram
    IFEL = auto() # if/else


def _test() -> None:
    for enum in (
        ClosureLabel,
        Direction,
        NodeType,
        Operator,
        PPUInstruction,
        TileAction,
        TileType,
        TokenType,
    ):
        print()
        print_enum(enum)


if __name__ == "__main__":
    _test()
