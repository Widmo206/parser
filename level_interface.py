"""LevelInterface class that links LevelPlayer and LevelSelect.

Created on 2026.02.06
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk

import events
from level import Level
from level_player import LevelPlayer
from level_select import LevelSelect
from save import Save

logger = logging.getLogger(__name__)


class LevelInterface(ttk.Frame):
    """Container that switches between level select and level player views."""
    save: Save
    level_player: LevelPlayer | None
    level_select: LevelSelect | None

    def __init__(self, master: tk.Misc, save: Save, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.save = save
        self.level_player = None
        self.level_select = None

        events.LevelClosed.connect(self._on_level_closed)
        events.LevelOpened.connect(self._on_level_opened)

        self._open_level_select()

    def _open_level_player(self, level: Level) -> None:
        logger.debug("Opening level player for '%s'", level.name)

        if self.level_select is not None:
            self.level_select.pack_forget()
            self.level_select.destroy()
            self.level_select = None

        self.level_player = LevelPlayer(self, level, self.save)
        self.level_player.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)

    def _open_level_select(self) -> None:
        logger.debug("Opening level select")

        if self.level_player is not None:
            self.level_player.pack_forget()
            self.level_player.destroy()
            self.level_player = None

        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)

        events.LevelSelectOpened()

    def _on_level_closed(self, _event: events.LevelClosed) -> None:
        self._open_level_select()

    def _on_level_opened(self, event: events.LevelOpened) -> None:
        self._open_level_player(event.level)
