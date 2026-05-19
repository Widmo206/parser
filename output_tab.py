"""OutputTab class to display output from one processor.

Created on 2026.02.08
Contributors:
    Romcode
"""

from math import ceil, floor
import tkinter as tk
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText

from enums import OutputType


class OutputTab(ScrolledText):
    DELTA_PER_ZOOM = 120

    font: str
    font_size: int
    min_font_size: int
    max_font_size: int
    padx_ratio: float
    zoom_factor: float

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        font: str = "Consolas",
        font_size: int = 11,
        min_font_size: int = 1,
        max_font_size: int = 128,
        padx_ratio: float = 0.5,
        zoom_factor: float = 1.1,
        **kwargs,
    ) -> None:
        kwargs.setdefault("hbar", True)
        kwargs.setdefault("autohide", True)
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.font = font
        self.font_size = font_size
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.padx_ratio = padx_ratio
        self.zoom_factor = zoom_factor

        self.text.configure(
            state=tk.DISABLED,
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            bg=style.colors.bg,
        )
        self.text.tag_config(OutputType.NORMAL.name, foreground=style.colors.fg)
        self.text.tag_config(OutputType.INFO.name, foreground=style.colors.info)
        self.text.tag_config(OutputType.WARNING.name, foreground=style.colors.warning)
        self.text.tag_config(OutputType.ERROR.name, foreground=style.colors.danger)
        self.text.bind("<Control-MouseWheel>", self._on_zoom)

    def clear(self) -> None:
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=tk.DISABLED)

    def print(self, text: Any = "", output_type: OutputType = OutputType.NORMAL) -> None:
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, str(text) + "\n", output_type.name)
        self.text.configure(state=tk.DISABLED)

    def _zoom(self, zoom_delta: int) -> None:
        if zoom_delta == 0:
            return

        raw_font_size = self.font_size * self.zoom_factor ** zoom_delta
        if abs(raw_font_size - self.font_size) < 1:
            if zoom_delta < 0:
                raw_font_size = floor(raw_font_size)
            else:
                raw_font_size = ceil(raw_font_size)
        else:
            raw_font_size = round(raw_font_size)
        self.font_size = min(max(raw_font_size, self.min_font_size), self.max_font_size)

        self.text.config(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
        )

    def _on_zoom(self, event: tk.Event) -> str:
        self._zoom(round(event.delta / self.DELTA_PER_ZOOM))
        return "break"
