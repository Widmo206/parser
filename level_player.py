"""LevelPlayer class that contains LevelBottomBar and LevelView

Created on 2026.02.05
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from level import Level
from level_bottom_bar import LevelBottomBar
from level_top_bar import LevelTopBar
from level_view import LevelView

logger = logging.getLogger(__name__)


class LevelPlayer(ttk.Frame):
    level: Level

    level_bottom_bar: LevelBottomBar
    level_top_bar: LevelTopBar
    level_view: LevelView

    def __init__(
        self,
        master: tk.Misc,
        level: Level,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.level = level

        logger.debug("Creating level view from layout")
        for line in self.level.layout.splitlines():
            logger.debug("'%s'", line)
        logger.debug("and direction layout")
        for line in self.level.direction_layout.splitlines():
            logger.debug("'%s'", line)

        self.level_view = LevelView(self, level)
        self.level_view.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.level_bottom_bar = LevelBottomBar(self)
        self.level_bottom_bar.grid(column=0, row=1, sticky=ttkc.NSEW)
