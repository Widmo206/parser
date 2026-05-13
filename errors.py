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


class PyScriptNameError(ValueError):
    """Raised when the code refers to an undefined reference or tries to redefine a reference in the same scope."""
    pass


class PyScriptTypeError(ValueError):
    """Raised when the code tries to perform an operation that isn't valid for a given type.
    
    e.g. trying to call a variable
    """
    pass
