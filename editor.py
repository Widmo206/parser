"""Editor class to manage PyscriptEditorTabs

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap import constants as ttkc

from common import get_solution_path, select_pyscript
from editor_tab import EditorTab
from errors import EditorTabCreationError
import events

logger = logging.getLogger(__name__)

LEVEL_SELECT_PYSCRIPT_PATH = Path("pyscript/level_select.pyscript")


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

        events.FileNewRequested.connect(self._on_file_new_requested)
        events.FileOpenRequested.connect(self._on_file_open_requested)
        events.LevelOpened.connect(self._on_level_opened)
        events.LevelSelectOpened.connect(self._on_level_select_opened)
        events.RunButtonPressed.connect(self._on_run_button_pressed)

    def get_selected_tab(self) -> EditorTab | None:
        tab_id = self.select()
        if tab_id is None:
            return None

        widget = self.nametowidget(tab_id)

        if not isinstance(widget, EditorTab):
            logger.error("Selected widget is not an EditorTab")
            return None

        return widget

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

    def _on_file_new_requested(self, _event: events.FileNewRequested) -> None:
        self.new_tab()

    def _on_file_open_requested(self, _event: events.FileOpenRequested) -> None:
        path = select_pyscript()
        if path is not None:
            self.open_tab(path)

    def _on_file_save_requested(self, _event: events.FileSaveRequested) -> None:
        selected_tab = self.get_selected_tab()
        if selected_tab is None:
            return

        if selected_tab.path is None:
            pass
            # TODO: Implement save as
        else:
            selected_tab.path.write_text(selected_tab.text.get("1.0", ttkc.END))

    def _on_level_opened(self, event: events.LevelOpened) -> None:
        self.open_tab_solution(event.level.pyscript_path)

    def _on_level_select_opened(self, _event: events.LevelSelectOpened) -> None:
        self.open_tab(LEVEL_SELECT_PYSCRIPT_PATH)

    def _on_run_button_pressed(self, _event: events.RunButtonPressed) -> None:
        events.FileSaveRequested()

        selected_tab = self.get_selected_tab()
        if selected_tab is None:
            return

        if selected_tab.path is not None:
            events.RunRequested(self.get_selected_tab().path)
