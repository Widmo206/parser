"""Tile class for display

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
from pathlib import Path
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc


@dataclass
class Tile:
    master: tk.Misc
    padding_ratio: float = 0.05

    def __post_init__(self) -> None:
        self.image = Image.open(Path("sprites") / "tile_background.png")
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.label = ttk.Label(self.master, image=self.image_tk, borderwidth=0)

    def resize(self, tile_size: int) -> None:
        if tile_size < 1:
            raise ValueError("Tile size cannot be less than 1")

        image_size = round(tile_size * (1 - self.padding_ratio))
        pad_size = round(tile_size * self.padding_ratio / 2)
        self.image_tk = ImageTk.PhotoImage(self.image.resize(
            (image_size, image_size),
            Image.LANCZOS,
        ))
        self.label.configure(image=self.image_tk, padding=pad_size)
