"""LevelSelect class that displays a list of available levels

Created on 2026.02.06
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc
from ttkbootstrap.widgets.scrolled import ScrolledFrame

from level import Level
from level_entry import LevelEntry


class LevelSelect(ScrolledFrame):
    def __init__(
        self,
        master: tk.Misc,
        separation: int = 4,
        **kwargs,
    ) -> None:
        kwargs.setdefault("autohide", True)
        kwargs.setdefault("padding", 8)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        for i, level_path in enumerate(Level.PATHS * 50):
            level_entry = LevelEntry(self, i + 1, level_path)
            level_entry.bind("<Button-1>", lambda _: print(i, level_path))
            level_entry.grid(row=i * 2, column=0, sticky=tk.EW)

            if i < len(Level.PATHS * 50) - 1:
                self.rowconfigure(i * 2 + 1, minsize=separation)
