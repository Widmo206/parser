"""LevelPlayer class that contains LevelController and LevelView

Created on 2026.02.05
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from common import get_solution_path
from level import Level
from level_controller import LevelController
from level_view import LevelView
from parser import FunctionHolder, Parser

logger = logging.getLogger(__name__)


class LevelPlayer(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        level_path: Path,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.level_path = level_path
        self.level = Level.from_path(self.level_path)

        logger.debug(f"Creating level view from layout\n{self.level.tilemap_layout}")
        self.level_view = LevelView(self, self.level.tilemap_layout)
        self.level_view.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.level_controller = LevelController(self)
        self.level_controller.grid(column=0, row=1, sticky=ttkc.NSEW)
