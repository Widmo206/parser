"""LevelView class to manage TileLabels and obey LevelModel

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from math import floor
import tkinter as tk

import ttkbootstrap as ttk

import events
from matrix import Matrix
from tile_data import TileData
from tile_label import TileLabel

logger = logging.getLogger(__name__)


class LevelView(ttk.Frame):
    grid_frame: ttk.Frame
    tile_label_matrix: Matrix[TileLabel]

    def __init__(
        self,
        master: tk.Misc,
        tile_data_matrix: Matrix[TileData],
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 64)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.grid()

        self.tile_label_matrix = tile_data_matrix.map(
            lambda tile_data: TileLabel(self.grid_frame, tile_data)
        )

        for x, y, tile_label in self.tile_label_matrix.iter_xy():
            tile_label.grid(column=x, row=y)

        self.bind("<Configure>", lambda _: self.update_tile_size())

        events.TileDataChanged.connect(self._on_tile_data_changed)

    def destroy(self) -> None:
        events.TileDataChanged.disconnect(self._on_tile_data_changed)
        ttk.Frame.destroy(self)

    def update_tile_size(self) -> None:
        padding = int(str(self.cget("padding")[0])) # TODO: clean up this weird conversion issue
        tile_size = floor(min(
            (self.winfo_width() - padding * 2) / self.tile_label_matrix.width,
            (self.winfo_height() - padding * 2) / self.tile_label_matrix.height,
        ))

        for tile_label in self.tile_label_matrix:
            tile_label.set_tile_size(tile_size)

    def _on_tile_data_changed(self, event: events.TileDataChanged) -> None:
        try:
            tile_label = self.tile_label_matrix.get(event.x, event.y)
        except IndexError:
            logger.error(f"No tile label at ({event.x}, {event.y})")
            return

        tile_label.set_tile_data(event.tile_data)
