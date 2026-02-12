"""PyscriptEditor class to manage PyscriptEditorTabs

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from common import PROJECT_DIR
from pyscript_editor_tab import PyscriptEditorTab

logger = logging.getLogger(__name__)


class PyscriptEditor(ttk.Notebook):
    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.style = style

    def open_pyscript(self, pyscript_path: Path) -> None:
        logger.debug(f"Creating new PyScript tab '{pyscript_path.name}'")
        if pyscript_path.absolute().is_relative_to(PROJECT_DIR):
            self.add(
                PyscriptEditorTab(self, self.style, pyscript_path),
                text=pyscript_path.name,
            )
        else:
            self.add(
                PyscriptEditorTab(self, self.style, pyscript_path),
                text=pyscript_path.name,
            )
