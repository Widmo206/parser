"""PyscriptManager class that links Editor and Output

Created on 2026.02.08
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk

from editor import Editor
from output import Output

logger = logging.getLogger(__name__)


class PyscriptManager(tk.PanedWindow):
    editor: Editor
    output: Output

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        **kwargs,
    ) -> None:
        kwargs.setdefault("orient", tk.VERTICAL)
        kwargs.setdefault("sashwidth", 8)
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("bg", style.colors.dark)
        super().__init__(master, **kwargs)

        self.editor = Editor(self, style)
        self.add(self.editor)

        self.output = Output(self, style)
        self.add(self.output)
