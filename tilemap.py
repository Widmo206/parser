"""Tilemap class to manage tiles

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from tile import Tile


@dataclass
class Tilemap:
    master: tk.Misc
    width: int = 16
    height: int = 16

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("Grid dimensions cannot be less than 1x1")

        self.frame = ttk.Frame(self.master)
        for x in range(self.width):
            self.frame.columnconfigure(x, minsize=Tile.SIZE)
        for y in range(self.height):
            self.frame.rowconfigure(y, minsize=Tile.SIZE)

        self.tiles = []
        for x in range(self.width):
            self.tiles.append([])
            for y in range(self.height):
                tile = Tile(self.frame)
                tile.label.grid(column=x, row=y, sticky=NSEW)
                tile.label.config(text=f"{x};{y}")
                self.tiles[x].append(tile)
