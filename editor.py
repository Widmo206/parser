"""Editor class for writing pyscript in tkinter

Created on 2026.01.28
Contributors:
    Romcode
"""

from math import ceil, floor
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc
from ttkbootstrap.widgets.scrolled import ScrolledText


class Editor(ttk.Frame):
    DELTA_PER_ZOOM = 120

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        font: str = "Consolas",
        font_size: int = 11,
        min_font_size: int = 1,
        max_font_size: int = 256,
        line_text_width: int = 4,
        padx_ratio: float = 0.5,
        zoom_factor: float = 1.1,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.font = font
        self.font_size = font_size
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.line_text_width = line_text_width
        self.padx_ratio = padx_ratio
        self.zoom_factor = zoom_factor

        self.line_text = tk.Text(self)
        self.line_text.config(
            width=self.line_text_width,
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            takefocus=0,
            state=ttkc.DISABLED,
            bg=style.colors.primary,
            fg=style.colors.secondary,
        )
        self.line_text.tag_config("active_line", foreground=style.colors.info)
        self.line_text.pack(side=ttkc.LEFT, fill=ttkc.Y)

        self.scrolled_text = ScrolledText(self, hbar=True, autohide=True, padding=0)
        self.scrolled_text.pack(side=ttkc.LEFT, fill=ttkc.BOTH, expand=True)

        self.text = self.scrolled_text.text
        self.text.configure(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            bg=style.colors.bg,
        )

        self.text.config(yscrollcommand=self._on_text_scroll)
        self.scrolled_text.vbar.config(command=self._on_scrollbar)

        self.text.bind("<<Modified>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<ButtonRelease-1>", self._on_change)
        self.text.bind("<FocusIn>", self._on_focus_change)
        self.text.bind("<FocusOut>", self._on_focus_change)
        self.text.bind('<Control-MouseWheel>', self._on_zoom)
        self.line_text.bind('<Control-MouseWheel>', self._on_zoom)

        self._update_line_numbers()

    def zoom(self, zoom_delta: int) -> None:
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

        self.line_text.config(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
        )
        self.text.config(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
        )

    def _on_text_scroll(self, *args) -> None:
        self.scrolled_text.vbar.set(*args)
        self.line_text.yview_moveto(args[0])

    def _on_scrollbar(self, *args) -> None:
        self.text.yview(*args)
        self.line_text.yview(*args)

    def _on_change(self, _event: tk.Event | None = None) -> None:
        self.text.edit_modified(False)
        self._update_line_numbers()

    def _on_focus_change(self, _event: tk.Event | None = None) -> None:
        self._update_line_numbers()

    def _on_zoom(self, event: tk.Event) -> None:
        self.zoom(round(event.delta / self.DELTA_PER_ZOOM))

    def _update_line_numbers(self) -> None:
        first, _ = self.line_text.yview()
        self.line_text.config(state="normal")
        self.line_text.delete("1.0", "end")

        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(
            str(i).rjust(
                self.line_text_width
            ) for i in range(1, line_count + 1)
        )
        self.line_text.insert("1.0", numbers)

        if self.text.focus_get() == self.text:
            current_line = int(self.text.index("insert").split(".")[0])
            self.line_text.tag_add(
                "active_line",
                f"{current_line}.0",
                f"{current_line}.end",
            )

        self.line_text.config(state="disabled")
        self.line_text.yview_moveto(first)
