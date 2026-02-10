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

from enums import VirtualEventSequence as Ves
from level_player import LevelPlayer
from level_select import LevelSelect

logger = logging.getLogger(__name__)


class LevelManager(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.level_select: LevelSelect | None = None
        self.level_player: LevelPlayer | None = None

        self.open_level_select()

    def open_level(self, level_path: Path) -> None:
        logger.debug(f"Opening level '{level_path}'")

        if self.level_select is not None:
            self.level_select.pack_forget()
            self.level_select.destroy()
            self.level_select = None

        self.level_player = LevelPlayer(self, level_path)
        self.level_player.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)
        self.level_player.level_bar.level_select_button.config(command=self.open_level_select)

        self.event_generate(Ves.LEVEL_OPENED)

    def open_level_select(self) -> None:
        logger.debug(f"Opening level select")

        if self.level_player is not None:
            self.level_player.pack_forget()
            self.level_player.destroy()
            self.level_player = None

        self.level_select = LevelSelect(self)
        self.level_select.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)
        self.level_select.bind(Ves.LEVEL_SELECTED, self._on_level_select_level_selected)

        self.event_generate(Ves.LEVEL_SELECT_OPENED)

    def _on_level_select_level_selected(self, _event: tk.Event) -> None:
        self.open_level(self.level_select.selected_level_path)
