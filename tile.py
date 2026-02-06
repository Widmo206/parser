"""Tile class for display

Created on 2026.01.28
Contributors:
    Romcode
"""

from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from enums import TileType
from errors import UnknownTileTypeError


class Tile(ttk.Label):
    MIN_SIZE = 32
    PADDING_RATIO = 0.05

    def __init__(
        self,
        master: tk.Misc,
        tile_type: TileType | str = TileType.EMPTY,
        **kwargs,
    ) -> None:
        if isinstance(tile_type, str):
            try:
                self.tile_type = TileType(tile_type)
            except ValueError as e:
                raise UnknownTileTypeError(
                    f"No tile type matching character: '{self.tile_type}'"
                ) from e
        else:
            self.tile_type = tile_type

        self.image_tk = ImageTk.PhotoImage(self.tile_type.image) if self.tile_type.image else None

        kwargs.setdefault("image", self.image_tk)
        kwargs.setdefault("borderwidth", 0)
        super().__init__(master, **kwargs)

    def resize(self, tile_size: int) -> None:
        tile_size = max(tile_size, self.MIN_SIZE)

        if tile_size < 1:
            raise ValueError(f"Tile size ({tile_size}) cannot be less than 1")

        image_size = round(tile_size * (1 - self.PADDING_RATIO))
        pad_size = round(tile_size * self.PADDING_RATIO / 2)
        self.image_tk = ImageTk.PhotoImage(self.tile_type.image.resize(
            (image_size, image_size),
            Image.Resampling.LANCZOS,
        )) if self.tile_type.image else None
        self.configure(image=self.image_tk, padding=pad_size)
