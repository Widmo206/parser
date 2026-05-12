"""Centralized location for easy error access

Created on 2026.01.31
Contributors:
    Romcode
    Widmo
"""

class EditorTabCreationError(ValueError):
    """Raised when trying to create an editor tab from an invalid file."""
    pass


class UnknownDirectionError(ValueError):
    """Raised when trying to convert a character to a direction that doesn't exist."""
    pass


class UnknownTileTypeError(ValueError):
    """Raised when trying to convert a character to a tile type that doesn't exist."""
    pass


class PyScriptSyntaxError(ValueError):
    """Raised when any step of the parser finds an issue with the user's code."""
    pass
