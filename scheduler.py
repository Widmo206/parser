"""Scheduler class that serves as an abstraction layer for tkinter timed tasks.

Created on 2026.03.04
Contributors:
    Romcode
"""

import tkinter as tk
from typing import Any, Callable


class Scheduler:
    """Schedule timed callbacks on a tkinter root widget."""

    _root: tk.Misc

    def __init__(self, root: tk.Misc) -> None:
        self._root = root

    def after(self, ms: int, callback: Callable[[], Any]) -> str:
        """Schedule a callback to run after the given delay in milliseconds."""
        return self._root.after(ms, callback)

    def after_cancel(self, after_id: str) -> None:
        """Cancel a callback previously scheduled with after()."""
        self._root.after_cancel(after_id)
