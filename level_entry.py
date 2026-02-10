"""LevelEntry class that displays level info and can be clicked to play it

Created on 2026.02.06
Contributors:
    Romcode
"""

from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from common import bind_recursive
from enums import VirtualEventSequence as Ves
from level import Level


class LevelEntry(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        level_number: int,
        level_path: Path,
        number_label_width: int = 3,
        separation: int = 4,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(1, minsize=separation)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.level_number = level_number
        self.level_path = level_path

        self.number_label = ttk.Label(
            self,
            text=str(self.level_number),
            width=number_label_width,
            anchor=ttkc.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle = (ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.number_label.grid(column=0, row=0, sticky=tk.NSEW)

        self.name_label = ttk.Label(
            self,
            text=Level.from_path(self.level_path).name,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.name_label.grid(column=2, row=0, sticky=tk.NSEW)

        self.number_label.bind("<Enter>", self._on_enter)
        self.number_label.bind("<Leave>", self._on_leave)
        self.name_label.bind("<Enter>", self._on_enter)
        self.name_label.bind("<Leave>", self._on_leave)
        bind_recursive(self,"<Button-1>", self._on_clicked)

    def _on_enter(self, _event: tk.Event) -> None:
        self.number_label.config(bootstyle=(ttkc.SECONDARY, ttkc.INVERSE))
        self.name_label.config(bootstyle=(ttkc.SECONDARY, ttkc.INVERSE))

    def _on_leave(self, _event: tk.Event) -> None:
        self.number_label.config(bootstyle=(ttkc.PRIMARY, ttkc.INVERSE))
        self.name_label.config(bootstyle=(ttkc.PRIMARY, ttkc.INVERSE))

    def _on_clicked(self, _event: tk.Event) -> None:
        self.event_generate(Ves.CLICKED)
