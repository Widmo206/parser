"""LevelSelect class that displays a list of available levels

Created on 2026.02.06
Contributors:
    Romcode
"""

# TODO: Fix TclError caused when brutally murdering a LevelSelect

from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc
from ttkbootstrap.widgets.scrolled import ScrolledFrame

from enums import VirtualEventSequence as Ves
from level import Level
from level_entry import LevelEntry


class LevelSelect(ScrolledFrame):
    def __init__(
        self,
        master: tk.Misc,
        separation: int = 4,
        **kwargs,
    ) -> None:
        kwargs.setdefault("autohide", True)
        kwargs.setdefault("padding", 8)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        # This is very ugly but tk events don't allow passing non str data,
        # so the parent has to grab these when receiving a level selected event
        self.selected_level_number: int | None = None
        self.selected_level_path: Path | None = None

        for i, level_path in enumerate(Level.PATHS):
            level_entry = LevelEntry(self, i + 1, level_path)
            level_entry.bind(Ves.CLICKED, self._on_level_entry_clicked)
            level_entry.grid(row=i * 2, column=0, sticky=tk.EW)

            if i < len(Level.PATHS * 50) - 1:
                self.rowconfigure(i * 2 + 1, minsize=separation)

    def _on_level_entry_clicked(self, event: tk.Event) -> None:
        level_entry: LevelEntry = event.widget

        self.selected_level_number = level_entry.level_number
        self.selected_level_path = level_entry.level_path

        self.event_generate(Ves.LEVEL_SELECTED)
