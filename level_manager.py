"""LevelManager class that links LevelPlayer and LevelSelect

Created on 2026.02.06
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events
from level_player import LevelPlayer
from level_select import LevelSelect

logger = logging.getLogger(__name__)


class LevelManager(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.level_select: LevelSelect | None = None
        self.level_player: LevelPlayer | None = None

        events.LevelSelected.connect(self._on_level_selected)
        events.LevelSelectButtonPressed.connect(self._on_level_select_button_pressed)

        self.open_level_select()

    def open_level(self, level_path: Path) -> None:
        logger.debug(f"Opening level '{level_path}'")

        if self.level_select is not None:
            self.level_select.pack_forget()
            self.level_select.destroy()
            self.level_select = None

        self.level_player = LevelPlayer(self, level_path)
        self.level_player.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

        events.LevelOpened(self.level_player.level)

    def open_level_select(self) -> None:
        logger.debug(f"Opening level select")

        if self.level_player is not None:
            self.level_player.pack_forget()
            self.level_player.destroy()
            self.level_player = None

        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

        events.LevelSelectOpened()

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.open_level(event.path)

    def _on_level_select_button_pressed(self, _event: events.LevelSelectButtonPressed) -> None:
        self.open_level_select()
