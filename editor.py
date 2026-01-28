"""Editor class for writing pyscript in tkinter

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


@dataclass
class Editor:
    master: tk.Misc

    def __post_init__(self) -> None:
        self.frame = ttk.Frame(self.master)

        self.text = ttk.Text(self.frame, wrap="none")
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.text.config(yscrollcommand=self.scrollbar.set)
