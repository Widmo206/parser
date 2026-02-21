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
from typing import NamedTuple

from common import print_enum
from errors import UnknownTileTypeError

logger = logging.getLogger(__name__)


class DirectionMixin(NamedTuple):
    x: int
    y: int


class Direction(DirectionMixin, Enum):
    UP    = (0, -1)
    DOWN  = (0, 1)
    LEFT  = (-1, 0)
    RIGHT = (1, 0)


class TileActionType(Enum):
    MOVE   = auto()
    ATTACK = auto


class TileType(Enum):
    BLOCKED = ("X", None, None, False)
    EMPTY   = ("O", Path("sprites/tile_background.png"), None, True)
    PLAYER  = ("P", Path("sprites/tile_background.png"), Path("sprites/player.png"), False)
    FLAG    = ("F", Path("sprites/tile_background.png"), Path("sprites/flag.png"), True)
    KEY     = ("K", Path("sprites/tile_background.png"), None, True)
    LOCK    = ("L", Path("sprites/tile_background.png"), None, False)
    ENEMY   = ("E", Path("sprites/tile_background.png"), None, False)

    character: str
    image: PILImage | None
    is_walkable: bool

    def __new__(
        cls,
        character: str,
        background_path: Path | None,
        foreground_path: Path | None,
        is_walkable: bool,
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
            return TileType.EMPTY

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
        TileType,
        TokenType,
    ):
        print()
        print_enum(enum)


if __name__ == "__main__":
    _test()
