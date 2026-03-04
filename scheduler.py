"""Scheduler class that serves as an abstraction layer for tkinter timed tasks

Created on 2026.03.04
Contributors:
    Romcode
"""

import tkinter as tk
from typing import Any, Callable


class Scheduler:
    _root: tk.Misc

    def __init__(self, root: tk.Misc) -> None:
        self._root = root

    def after(self, ms: int, callback: Callable[[], Any]) -> str:
        return self._root.after(ms, callback)

    def after_cancel(self, after_id: str) -> None:
        self._root.after_cancel(after_id)
