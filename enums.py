"""Centralized location for easy enum access

Created on 2026.01.30
Contributors:
    Romcode
"""

from __future__ import annotations
from enum import auto, Enum
import logging
from pathlib import Path
from PIL import Image
from PIL.Image import Image as PILImage

from common import print_enum
from errors import UnknownDirectionError, UnknownTileTypeError

logger = logging.getLogger(__name__)


class Direction(Enum):
    UP    = ("U", 0, -1, Image.Transpose.ROTATE_90)
    DOWN  = ("D", 0, 1, Image.Transpose.ROTATE_270)
    LEFT  = ("L", -1, 0, Image.Transpose.ROTATE_180)
    RIGHT = ("R", 1, 0, None)

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
            logger.error(f"No direction matching value '{value}'")
            return cls.RIGHT

    @classmethod
    def _missing_(cls, value: object) -> Direction:
        raise UnknownDirectionError(f"No direction matching value '{value}'")

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


class TileType(Enum):
    BLOCKED = ("X", None                               , None                      , False, 2)
    EMPTY   = ("O", Path("sprites/tile_background.png"), None                      , True , 2)
    PLAYER  = ("P", Path("sprites/tile_background.png"), Path("sprites/player.png"), True , 0)
    FLAG    = ("F", Path("sprites/tile_background.png"), Path("sprites/flag.png")  , True , 2)
    KEY     = ("K", Path("sprites/tile_background.png"), Path("sprites/key.png")   , True , 2)
    GATE    = ("G", Path("sprites/tile_background.png"), Path("sprites/gate.png")  , False, 2)
    ENEMY   = ("E", Path("sprites/tile_background.png"), Path("sprites/enemy.png") , False, 1)
    WIN     = ("W", Path("sprites/tile_background.png"), Path("sprites/win.png")   , False, 2)

    character: str
    image: PILImage | None
    is_walkable: bool

    def __new__(
        cls,
        character: str,
        background_path: Path | None,
        foreground_path: Path | None,
        is_walkable: bool,
        action_priority: int,
    ) -> TileType:
        bg = Image.open(background_path).convert("RGBA") if background_path else None
        fg = Image.open(foreground_path).convert("RGBA") if foreground_path else None

        if bg and fg:
            composed = bg.copy()
            composed.alpha_composite(fg)
        else:
            composed = bg or fg

        obj = object.__new__(cls)
        obj._value_ = character

        obj.character = character
        obj.image = composed
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
            logger.error(f"No tile type matching value '{value}'")
            return cls.EMPTY

    @classmethod
    def _missing_(cls, value: object) -> TileType:
        raise UnknownTileTypeError(f"No tile type matching value '{value}'")


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
    OPERATOR    = auto() # math operators like + * % ==
    # data types
    STRING_LIT  = auto() # "abcd"
    INT_LIT     = auto() # 1234
    FLOAT_LIT   = auto() # 1.2e3
#     # operators
#     PLUS        = auto() # +
#     MINUS       = auto() # -
#     STAR        = auto() # *
#     SLASH       = auto() # /


def _test() -> None:
    for enum in (
        Direction,
        TileAction,
        TileType,
        TokenType,
    ):
        print()
        print_enum(enum)


if __name__ == "__main__":
    _test()
