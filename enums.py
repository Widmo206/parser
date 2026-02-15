"""Centralized location for easy enum access

Created on 2026.01.30
Contributors:
    Romcode
"""

from enum import auto, Enum
from pathlib import Path
from PIL import Image

from common import print_enum
from errors import UnknownTileTypeError
import events
from menu_command import MenuCommand


class FileMenuCommand(MenuCommand, Enum):
    NEW     = ("New", events.FileNewRequested, "Ctrl+N", "<Control-n>")
    OPEN    = ("Open...", events.FileOpenRequested, "Ctrl+O", "<Control-o>")
    SAVE    = ("Save", events.FileSaveRequested, "Ctrl+S", "<Control-s>")
    SAVE_AS = ("Save as...", events.FileSaveAsRequested, "Ctrl+Shift+S", "<Control-Shift-n>")
    EXIT    = ("Exit", events.ExitRequested, "Ctrl+Q", "<Control-q>")


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

    @classmethod
    def _missing_(cls, value):
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
    print()
    print_enum(FileMenuCommand)
    print()
    print_enum(TileType)


if __name__ == "__main__":
    _test()
