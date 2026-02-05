"""Tilemap class to manage tiles

Created on 2026.01.28
Contributors:
    Romcode
"""

from math import floor
import tkinter as tk

import ttkbootstrap as ttk

from tile import Tile


class Tilemap(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        layout: str,
        **kwargs,
    ) -> None:
        if layout == "":
            raise ValueError("Tilemap layout cannot be empty")

        self.layout = layout

        rows = self.layout.splitlines()
        self.width = len(rows[0])
        self.height = len(rows)

        if any(len(row) != self.width for row in rows):
            raise ValueError(f"Mismatched row length in tilemap layout '{self.layout}'")
        if self.width < 1 or self.height < 1:
            raise ValueError(f"Grid dimensions ({self.width}x{self.height}) cannot be less than 1x1")

        kwargs.setdefault("padding", 64)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.grid()

        self.bind("<Configure>", lambda _: self.update_tile_size())

        self.tiles = []
        for x in range(self.width):
            for y in range(self.height):
                tile = Tile(self.grid_frame, rows[y][x])
                tile.grid(column=x, row=y)
                self.tiles.append(tile)

    def update_tile_size(self) -> None:
        padding = self.cget("padding")[0]
        tile_size = floor(min(
            (self.winfo_width() - padding * 2) / self.width,
            (self.winfo_height() - padding * 2) / self.height,
        ))

        for tile in self.tiles:
            tile.resize(tile_size)
