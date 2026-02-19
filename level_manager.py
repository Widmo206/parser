"""LevelManager class that links LevelPlayer and LevelSelect

Created on 2026.02.06
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events
from level import Level
from level_player import LevelPlayer
from level_select import LevelSelect

logger = logging.getLogger(__name__)


class LevelManager(ttk.Frame):
    level_player: LevelPlayer | None
    level_select: LevelSelect | None

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)

        events.LevelClosed.connect(self._on_level_closed)
        events.LevelOpened.connect(self._on_level_opened)

        self.open_level_select()

    def open_level_player(self, level: Level) -> None:
        logger.debug(f"Opening level player for '{level.name}'")

        if self.level_select is not None:
            self.level_select.pack_forget()
            self.level_select.destroy()
            self.level_select = None

        self.level_player = LevelPlayer(self, level)
        self.level_player.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

    def open_level_select(self) -> None:
        logger.debug(f"Opening level select")

        if self.level_player is not None:
            self.level_player.pack_forget()
            self.level_player.destroy()
            self.level_player = None

        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

        events.LevelSelectOpened()

    def _on_level_closed(self, _event: events.LevelClosed) -> None:
        self.open_level_select()

    def _on_level_opened(self, event: events.LevelOpened) -> None:
        self.open_level_player(event.level)
