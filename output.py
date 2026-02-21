"""Output class to display the output of running PyScript programs

Created on 2026.02.08
Contributors:
    Romcode
"""

import logging
import tkinter as tk
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
from ttkbootstrap import constants as ttkc

import events

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
            state=ttkc.DISABLED,
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            bg=style.colors.bg,
        )

        events.RunRequested.connect(self._on_run_requested)
        events.TokenizingFinished.connect(self._on_tokenizing_finished)

    def clear(self) -> None:
        self.text.configure(state=ttkc.NORMAL)
        self.text.delete("1.0", ttkc.END)
        self.text.configure(state=ttkc.DISABLED)

    def print(self, text: Any = "") -> None:
        self.text.configure(state=ttkc.NORMAL)
        self.text.insert(ttkc.END, str(text) + "\n")
        self.text.configure(state=ttkc.DISABLED)

    def _on_run_requested(self, event: events.RunRequested) -> None:
        self.clear()
        self.print(str(event.path))

    def _on_tokenizing_finished(self, event: events.TokenizingFinished) -> None:
        self.print()
        self.print(event.tokens)
