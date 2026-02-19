"""Output class to display the output of running PyScript programs

Created on 2026.02.08
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText

logger = logging.getLogger(__name__)


class Output(ScrolledText):
    DELTA_PER_ZOOM = 120

    font: str
    font_size: int
    padx_ratio: float

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        font: str = "Consolas",
        font_size: int = 11,
        padx_ratio: float = 0.5,
        **kwargs,
    ) -> None:
        kwargs.setdefault("hbar", True)
        kwargs.setdefault("autohide", True)
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.font = font
        self.font_size = font_size
        self.padx_ratio = padx_ratio

        self.text.configure(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            bg=style.colors.bg,
        )
