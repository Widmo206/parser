"""LevelTopBar class to display level name and best score.

Created on 2026.03.11
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

class LevelTopBar(ttk.Frame):
    name_label: ttk.Label
    token_count_label: ttk.Label

    def __init__(
        self,
        master: tk.Misc,
        name: str,
        token_count: int | None = None,
        separation: int = 4,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 8)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, minsize=separation)
        self.columnconfigure(4, weight=1)

        self.name_label = ttk.Label(
            self,
            text=name,
            anchor=tk.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.name_label.grid(column=1, row=0, sticky=tk.NSEW)

        best_score_text = "N/A" if token_count is None else str(token_count)
        self.token_count_label = ttk.Label(
            self,
            text=f"Best token count: {best_score_text}",
            anchor=tk.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.token_count_label.grid(column=3, row=0, sticky=tk.NSEW)

