"""Tile class for display

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


@dataclass
class Tile:
    SIZE = 64

    master: tk.Misc

    def __post_init__(self) -> None:
        self.label = ttk.Label(self.master, anchor=CENTER, bootstyle=INVERSE)
