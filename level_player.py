"""LevelPlayer class that links LevelBar and Tilemap

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
from level_bar import LevelBar
from parser import FunctionHolder, Parser
from tilemap import Tilemap

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

        logger.debug(f"Creating tilemap from layout\n{self.level.tilemap_layout}")
        self.tilemap = Tilemap(self, self.level.tilemap_layout)
        self.tilemap.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.level_bar = LevelBar(self)
        self.level_bar.grid(column=0, row=1, sticky=ttkc.NSEW)

        self.level_bar.play_button.config(command=self.play)

    def play(self) -> None:
        # TODO: Hook up LevelPlayer.play to events and stuff
        logger.debug(f"Playing level '{self.level.name}'")

        parser = Parser(FunctionHolder(), get_solution_path(self.level_path))
        print(parser.tokenize())
