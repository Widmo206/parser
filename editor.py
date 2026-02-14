"""Editor class to manage PyscriptEditorTabs

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk

from common import get_solution_path
from editor_tab import EditorTab
from errors import EditorTabCreationError

logger = logging.getLogger(__name__)


class Editor(ttk.Notebook):
    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.style = style

    def new_tab(self) -> None:
        logger.debug("Creating new untitled tab")
        self.add(
            EditorTab(self, self.style),
            text="<untitled>",
        )

    def open_tab(self, path: Path) -> None:
        logger.debug(f"Creating new tab '{path.name}'")

        try:
            self.add(
                EditorTab(self, self.style, path),
                text=path.name,
            )
        except EditorTabCreationError:
            logger.error(f"Failed to create tab '{path.name}'")

    def open_tab_solution(self, path: Path) -> None:
        solution_path = get_solution_path(path)
        logger.debug(f"Creating new tab '{solution_path.name}'")

        try:
            self.add(
                EditorTab(self, self.style, solution_path, path),
                text=solution_path.name,
            )
        except EditorTabCreationError:
            logger.error(f"Failed to create tab '{path.name}'")
