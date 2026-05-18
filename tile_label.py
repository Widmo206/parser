"""TileLabel class for tile image display.

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk

from tile_data import TileData

logger = logging.getLogger(__name__)


class TileLabel(ttk.Label):
    MIN_SIZE = 32
    PADDING_RATIO = 0.05

    tile_data: TileData
    tile_size: int
    image_tk: ImageTk.PhotoImage

    def __init__(
        self,
        master: tk.Misc,
        tile_data: TileData | None = None,
        tile_size: int = MIN_SIZE,
        **kwargs,
    ) -> None:
        kwargs.setdefault("borderwidth", 0)
        super().__init__(master, **kwargs)

        self.tile_data = TileData() if tile_data is None else tile_data
        self.tile_size = tile_size
        self._update_image()

    def set_tile_data(self, tile_data: TileData) -> None:
        self.tile_data = tile_data
        self._update_image()

    def set_tile_size(self, tile_size: int) -> None:
        self.tile_size = max(tile_size, self.MIN_SIZE)
        self._update_image()

    def _update_image(self) -> None:
        image_size = round(self.tile_size * (1 - self.PADDING_RATIO))
        pad_size = round(self.tile_size * self.PADDING_RATIO / 2)

        if self.tile_data.tile_type.image is None:
            self.image_tk = None
        else:
            image = self.tile_data.tile_type.image.resize(
                (image_size, image_size),
                Image.Resampling.LANCZOS,
            )
            if self.tile_data.tile_direction.image_transpose is not None:
                image = image.transpose(self.tile_data.tile_direction.image_transpose)
            self.image_tk = ImageTk.PhotoImage(image)

        self.config(image=self.image_tk, padding=pad_size)
