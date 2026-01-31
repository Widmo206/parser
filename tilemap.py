"""Tilemap class to manage tiles

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from math import floor
from tile import Tile


@dataclass
class Tilemap:
    master: tk.Misc
    width: int = 16
    height: int = 16
    padding: int = 32

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("Grid dimensions cannot be less than 1x1")

        self.frame = ttk.Frame(self.master, padding=self.padding)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        self.grid_frame = ttk.Frame(self.frame)
        self.grid_frame.grid()

        self.frame.bind("<Configure>", lambda _: self.update_tile_size())

        self.tiles = []
        for x in range(self.width):
            for y in range(self.height):
                tile = Tile(self.grid_frame)
                tile.label.grid(column=x, row=y)
                self.tiles.append(tile)

    def update_tile_size(self) -> None:
        tile_size = floor(min(
            (self.frame.winfo_width() - self.padding * 2) / self.width,
            (self.frame.winfo_height() - self.padding * 2) / self.height,
        ))

        for tile in self.tiles:
            tile.resize(tile_size)
