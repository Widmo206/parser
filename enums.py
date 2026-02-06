"""Centralized location for easy enum access

Created on 2026.01.30
Contributors:
    Romcode
"""

from enum import auto, Enum
from pathlib import Path
from PIL import Image


class TileType(Enum):
    BLOCKED = ("X", None, None, False)
    EMPTY   = ("O", Path("sprites/tile_background.png"), None, True)
    PLAYER  = ("P", Path("sprites/tile_background.png"), Path("sprites/player.png"), False)
    GOAL    = ("G", Path("sprites/tile_background.png"), Path("sprites/goal.png"), True)
    KEY     = ("K", Path("sprites/tile_background.png"), None, True)
    LOCK    = ("L", Path("sprites/tile_background.png"), None, False)
    ENEMY   = ("E", Path("sprites/tile_background.png"), None, False)

    def __new__(
        cls,
        character: str,
        background_path: Path | None,
        foreground_path: Path | None,
        walkable: bool,
    ):
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
        obj.walkable = walkable

        return obj


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
