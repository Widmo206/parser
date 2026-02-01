"""Editor class for writing pyscript in tkinter

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc


@dataclass
class Editor:
    master: tk.Misc

    def __post_init__(self) -> None:
        self.frame = ttk.Frame(self.master)

        self.text = ttk.Text(self.frame, wrap=ttkc.NONE)
        self.text.pack(side=ttkc.LEFT, fill=ttkc.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame, orient=ttkc.VERTICAL, command=self.text.yview)
        self.scrollbar.pack(side=ttkc.RIGHT, fill=ttkc.Y)

        self.text.config(yscrollcommand=self.scrollbar.set)
