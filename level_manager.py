"""LevelManager class that links LevelPlayer and LevelSelect

Created on 2026.02.06
Contributors:
    Romcode
"""

from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from level_player import LevelPlayer
from level_select import LevelSelect


class LevelManager(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)
        self.level_player = None

    def open_level(self, level_path: Path) -> None:
        self.level_select.destroy()
        self.level_player = LevelPlayer(self, level_path)
        self.level_player.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

    def open_level_select(self) -> None:
        self.level_player.destroy()
        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)
