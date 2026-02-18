"""TileLabel class for display

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from tile_action import TileAction
from enums import TileActionType, Direction, TileType
from errors import UnknownTileTypeError

logger = logging.getLogger(__name__)


class TileLabel(ttk.Label):
    MIN_SIZE = 32
    PADDING_RATIO = 0.05

    def __init__(
        self,
        master: tk.Misc,
        tile_type: TileType | str = TileType.EMPTY,
        tile_size: int = MIN_SIZE,
        **kwargs,
    ) -> None:
        kwargs.setdefault("borderwidth", 0)
        super().__init__(master, **kwargs)

        self.tile_size = tile_size
        self.resize(self.tile_size)

    def resize(self, tile_size: int) -> None:
        tile_size = max(tile_size, self.MIN_SIZE)

        if tile_size < 1:
            raise ValueError(f"TileLabel size ({tile_size}) cannot be less than 1")

        self.tile_size = tile_size

        image_size = round(tile_size * (1 - self.PADDING_RATIO))
        pad_size = round(tile_size * self.PADDING_RATIO / 2)

        if self.tile_type.image is None:
            self.image_tk = None
        else:
            image = self.tile_type.image.resize(
                (image_size, image_size),
                Image.Resampling.LANCZOS,
            )
            self.image_tk = ImageTk.PhotoImage(image)

        self.configure(image=self.image_tk, padding=pad_size)
