"""Tile class for display

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from enums import TileType
from errors import UnknownTileTypeError


@dataclass
class Tile:
    master: tk.Misc
    tile_type: TileType | str = TileType.EMPTY
    padding_ratio: float = 0.05

    def __post_init__(self) -> None:
        if isinstance(self.tile_type, str):
            try:
                self.tile_type = TileType(self.tile_type)
            except ValueError as e:
                raise UnknownTileTypeError(
                    f"No tile type matching character: '{self.tile_type}'"
                ) from e

        self.image_tk = ImageTk.PhotoImage(self.tile_type.image) if self.tile_type.image else None
        self.label = ttk.Label(self.master, image=self.image_tk, borderwidth=0)

    def resize(self, tile_size: int) -> None:
        if tile_size < 1:
            raise ValueError(f"Tile size ({tile_size}) cannot be less than 1")

        image_size = round(tile_size * (1 - self.padding_ratio))
        pad_size = round(tile_size * self.padding_ratio / 2)
        self.image_tk = ImageTk.PhotoImage(self.tile_type.image.resize(
            (image_size, image_size),
            Image.LANCZOS,
        )) if self.tile_type.image else None
        self.label.configure(image=self.image_tk, padding=pad_size)
