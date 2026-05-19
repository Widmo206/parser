"""LevelView class to manage TileLabels and obey LevelModel.

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
    """Display a level grid and keep tile labels in sync with tile data."""
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

        self.bind("<Configure>", lambda _: self._update_tile_size())

        events.TileDataMatrixChanged.connect(self._on_tile_data_matrix_changed)

    def destroy(self) -> None:
        """Disconnect event handlers before destroying the widget."""
        events.TileDataMatrixChanged.disconnect(self._on_tile_data_matrix_changed)
        ttk.Frame.destroy(self)

    def _update_tile_size(self) -> None:
        padding_value = self.cget("padding")[0]
        padding = self.tk.getint(padding_value)
        tile_size = floor(min(
            (self.winfo_width() - padding * 2) / self.tile_label_matrix.width,
            (self.winfo_height() - padding * 2) / self.tile_label_matrix.height,
        ))

        for x in range(self.tile_label_matrix.width):
            self.grid_frame.columnconfigure(x, minsize=tile_size)

        for y in range(self.tile_label_matrix.height):
            self.grid_frame.rowconfigure(y, minsize=tile_size)

        for tile_label in self.tile_label_matrix:
            tile_label.set_tile_size(tile_size)

    def _on_tile_data_matrix_changed(self, event: events.TileDataMatrixChanged) -> None:
        if (
            self.tile_label_matrix.width != event.tile_data_matrix.width
            or self.tile_label_matrix.height != event.tile_data_matrix.height
        ):
            logger.error(
                "Mismatched dimensions in tile label matrix (%dx%d) and tile data matrix (%dx%d)",
                event.tile_data_matrix.width,
                self.tile_label_matrix.height,
                event.tile_data_matrix.width,
                event.tile_data_matrix.height,
            )
            return

        for x, y, tile_data in event.tile_data_matrix.iter_xy():
            self.tile_label_matrix.get(x, y).set_tile_data(tile_data)
