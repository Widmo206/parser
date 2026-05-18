"""Centralized location for easy error access.

Created on 2026.01.31
Contributors:
    Romcode
    Widmo
"""

class EditorTabCreationError(ValueError):
    """Raised when trying to create an editor tab from an invalid file."""
    pass


class InvalidSpecialMoveError(ValueError):
    """Raised when trying to execute a special move that doesn't exist."""
    pass


class UnknownDirectionError(ValueError):
    """Raised when trying to convert a character to a direction that doesn't exist."""
    pass


class UnknownTileTypeError(ValueError):
    """Raised when trying to convert a character to a tile type that doesn't exist."""
    pass


class PyScriptError(ValueError):
    """Base class for all PyScript errors."""


class PyScriptSyntaxError(PyScriptError):
    """Raised when any step of the parser finds an issue with the user's code."""
    pass


class PyScriptNameError(PyScriptError):
    """Raised when the code refers to an undefined reference or tries to redefine a reference in the same scope."""
    pass


class PyScriptTypeError(PyScriptError):
    """Raised when the code tries to perform an operation that isn't valid for a given type.
    
    e.g. trying to call a variable
    """
    pass


class EndOfProgram(PyScriptError):
    """Raised when a PyScript Program runs out of instructions.
    
    This includes subprograms.
    """


class PyScriptRuntimeError(PyScriptError):
    """Raised when the Processor detects that something went wrong, but the cause isn't clear."""
