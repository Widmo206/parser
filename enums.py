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
from menu_command import MenuCommand


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


class VirtualEventSequence(str, Enum):
    @staticmethod
    def _generate_next_value_(name: str, *_args) -> str:
        return f"<<{name.title().replace("_", "")}>>"

    CLICKED             = auto()
    EXIT                = auto()
    FILE_NEW            = auto()
    FILE_OPEN           = auto()
    FILE_SAVE           = auto()
    FILE_SAVE_AS        = auto()
    LEVEL_SELECTED      = auto()
    LEVEL_OPENED        = auto()
    LEVEL_SELECT_OPENED = auto()


class FileMenuCommand(MenuCommand, Enum):
    NEW     = ("New", VirtualEventSequence.FILE_NEW, "Ctrl+N", "<Control-n>")
    OPEN    = ("Open...", VirtualEventSequence.FILE_OPEN, "Ctrl+O", "<Control-o>")
    SAVE    = ("Save", VirtualEventSequence.FILE_SAVE, "Ctrl+S", "<Control-s>")
    SAVE_AS = ("Save as...", VirtualEventSequence.FILE_SAVE_AS, "Ctrl+Shift+S", "<Control-Shift-n>")
    EXIT    = ("Exit", VirtualEventSequence.EXIT, "Ctrl+Q", "<Control-q>")


def _test() -> None:
    print()
    print_enum(VirtualEventSequence)
    print()
    print_enum(FileMenuCommand)


if __name__ == "__main__":
    _test()
