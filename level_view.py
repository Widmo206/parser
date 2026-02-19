"""LevelView class to manage TileLabels and obey LevelModel

Created on 2026.01.28
Contributors:
    Romcode
"""

from math import floor
import tkinter as tk

import ttkbootstrap as ttk

from enums import TileType
import events
from level import Level
from tile_label import TileLabel


class LevelView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        level: Level,
        **kwargs,
    ) -> None:
        self.level = level

        rows = self.level.layout.splitlines()
        self.width = len(rows[0])
        self.height = len(rows)

        if any(len(row) != self.width for row in rows):
            raise ValueError(f"Mismatched row length in tilemap layout\n{self.level.layout}")

        kwargs.setdefault("padding", 64)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.grid()

        self.bind("<Configure>", lambda _: self.update_tile_size())

        self.tile_labels = []
        for y in range(self.height):
            for x in range(self.width):
                tile_label = TileLabel(self.grid_frame, rows[y][x])
                tile_label.grid(column=x, row=y)
                self.tile_labels.append(tile_label)

        events.TileTypeChanged.connect(self._on_model_tile_type_changed)

    def destroy(self) -> None:
        events.TileTypeChanged.disconnect(self._on_model_tile_type_changed)
        ttk.Frame.destroy(self)

    def set_tile_type(self, x: int, y: int, tile_type: TileType) -> None:
        self.tile_labels[y * self.width + x].set_tile_type(tile_type)

    def update_tile_size(self) -> None:
        padding = int(str(self.cget("padding")[0])) # TODO: clean up this weird conversion issue
        tile_size = floor(min(
            (self.winfo_width() - padding * 2) / self.width,
            (self.winfo_height() - padding * 2) / self.height,
        ))

        for tile in self.tile_labels:
            tile.resize(tile_size)

    def _on_model_tile_type_changed(self, event: events.TileTypeChanged) -> None:
        self.set_tile_type(event.x, event.y, event.tile_type)
