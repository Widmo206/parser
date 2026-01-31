"""Centralized location for easy enum access

Created on 2026.01.30
Contributors:
    Romcode
"""

from enum import auto, Enum
from pathlib import Path
from PIL import Image
from PIL.ImageFile import ImageFile
from typing import NamedTuple


class TileTypeMixin(NamedTuple):
    character: str
    background_image: ImageFile | None
    foreground_image: ImageFile | None
    walkable: bool


class TileType(TileTypeMixin, Enum):
    BLOCKED = ("X", None, None, False)
    EMPTY   = (" ", Image.open(Path("sprites") / "tile_background.png"), None, True)
    PLAYER  = ("P", Image.open(Path("sprites") / "tile_background.png"), None, False)
    GOAL    = ("G", Image.open(Path("sprites") / "tile_background.png"), None, True)
    KEY     = ("K", Image.open(Path("sprites") / "tile_background.png"), None, True)
    LOCK    = ("L", Image.open(Path("sprites") / "tile_background.png"), None, False)
    ENEMY   = (" ", Image.open(Path("sprites") / "tile_background.png"), None, False)


class TokenType(Enum):
    NOP         = auto()
    KEYWORD     = auto()
    REFERENCE   = auto()
    OPEN_PAREN  = auto()
    CLOSE_PAREN = auto()
    SEMICOLON   = auto()
    ASSIGN      = auto()
    STRING_LIT  = auto()
    INT_LIT     = auto()
    FLOAT_LIT   = auto()
    COMMA       = auto()
    PLUS        = auto()
    DASH        = auto()
    STAR        = auto()
    SLASH       = auto()
