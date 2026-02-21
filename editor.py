"""Editor class to manage PyscriptEditorTabs

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk

from common import ask_open_pyscript, ask_save_as_pyscript, get_solution_path, PROJECT_DIR
from editor_tab import EditorTab
from errors import EditorTabCreationError
import events

logger = logging.getLogger(__name__)

LEVEL_SELECT_PYSCRIPT_PATH = Path("pyscript/level_select.pyscript")
UNTITLED_TAB_NAME = "<untitled>"


class Editor(ttk.Notebook):
    style: ttk.Style

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.style = style

        events.FileNewRequested.connect(lambda _: self.new_tab())
        events.FileOpenRequested.connect(self._on_file_open_requested)
        events.FileSaveRequested.connect(lambda _: self.save())
        events.LevelOpened.connect(self._on_level_opened)
        events.LevelSelectOpened.connect(lambda _: self.open_tab(LEVEL_SELECT_PYSCRIPT_PATH))
        events.RunButtonPressed.connect(self._on_run_button_pressed)

    def get_selected_tab(self) -> EditorTab | None:
        tab_id = self.select()
        if tab_id is None:
            return None

        return self.nametowidget(tab_id)

    def new_tab(self) -> None:
        self._add_tab()

    def open_tab(
        self,
        path: Path,
        default_content_path: Path | None = None,
    ) -> None:
        for tab_id in self.tabs():
            if self.nametowidget(tab_id).path == path:
                logger.debug(f"Creating new tab '{path.name}'")
                self.select(tab_id)
                return

        self._add_tab(path, default_content_path)

    def open_tab_solution(self, path: Path) -> None:
        self.open_tab(get_solution_path(path), path)

    def save(self) -> None:
        selected_tab = self.get_selected_tab()
        if selected_tab is None:
            return

        if selected_tab.path is None:
            self.save_as()
        elif selected_tab.path.absolute().is_relative_to(PROJECT_DIR):
            logger.warning(f"Cannot overwrite built-in file '{selected_tab.path}'")
        else:
            logger.debug(f"Saving file '{selected_tab.path}'")
            selected_tab.path.write_text(selected_tab.text.get("1.0", "end-1c"))

    def save_as(self) -> None:
        selected_tab = self.get_selected_tab()
        if selected_tab is None:
            return

        print(ask_save_as_pyscript())
        #TODO: Actually save the file and rename tab

    def _add_tab(
        self,
        path: Path | None = None,
        default_content_path: Path | None = None,
    ) -> None:
        name = path.name if path is not None else UNTITLED_TAB_NAME
        logger.debug(f"Creating new tab '{name}'")

        try:
            self.add(
                EditorTab(self, self.style, path, default_content_path),
                text=name,
            )
        except EditorTabCreationError:
            logger.error(f"Failed to create tab '{name}'")
            return

        self.select(self.tabs()[-1])

    def _on_file_open_requested(self, _event: events.FileOpenRequested) -> None:
        path = ask_open_pyscript()
        if path is not None:
            self.open_tab(path)

    def _on_level_opened(self, event: events.LevelOpened) -> None:
        self.open_tab_solution(event.level.pyscript_path)

    def _on_run_button_pressed(self, _event: events.RunButtonPressed) -> None:
        self.save()

        selected_tab = self.get_selected_tab()
        if selected_tab is None:
            return

        if selected_tab.path is not None:
            events.RunRequested(self.get_selected_tab().path)
