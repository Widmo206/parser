"""Editor class to manage PyscriptEditorTabs

Created on 2026.01.28
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk

from common import (
    ask_open_pyscript,
    ask_save_as_pyscript,
    get_solution_path,
    message_error,
    PROJECT_DIR,
)
from editor_tab import EditorTab
from errors import EditorTabCreationError
import events

logger = logging.getLogger(__name__)

LEVEL_SELECT_PYSCRIPT_PATH = Path("pyscript/level_select.pyscript")
UNTITLED_TAB_NAME = "<untitled>"


class Editor(ttk.Notebook):
    style: ttk.Style
    is_level_active: bool

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.style = style
        self.is_level_active = False

        events.ActivePyscriptRequested.connect(self._on_active_pyscript_requested)
        events.FileNewRequested.connect(self._on_file_new_requested)
        events.FileOpenRequested.connect(self._on_file_open_requested)
        events.FileSaveRequested.connect(self._on_file_save_requested)
        events.FileSaveAsRequested.connect(self._on_file_save_as_requested)
        events.LevelOpened.connect(self._on_level_opened)
        events.LevelSelectOpened.connect(self._on_level_select_opened)
        events.LevelStateChanged.connect(self._on_level_state_changed)

    def destroy(self) -> None:
        events.ActivePyscriptRequested.disconnect(self._on_active_pyscript_requested)
        events.FileNewRequested.disconnect(self._on_file_new_requested)
        events.FileOpenRequested.disconnect(self._on_file_open_requested)
        events.FileSaveRequested.disconnect(self._on_file_save_requested)
        events.FileSaveAsRequested.disconnect(self._on_file_save_as_requested)
        events.LevelOpened.disconnect(self._on_level_opened)
        events.LevelSelectOpened.disconnect(self._on_level_select_opened)
        events.LevelStateChanged.disconnect(self._on_level_state_changed)
        super().destroy()

    def get_active_tab(self) -> EditorTab | None:
        tab_id = self.select()
        if tab_id == "":
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
                logger.debug("Selecting open tab '%s'", path.name)
                self.select(tab_id)
                return

        self._add_tab(path, default_content_path)

    def open_tab_solution(self, path: Path) -> None:
        self.open_tab(get_solution_path(path), path)

    def save(self) -> None:
        active_tab = self.get_active_tab()
        if active_tab is None:
            message_error("No active tab to save")
            return
        if active_tab.path is None:
            self.save_as()
            return
        absolute_path = active_tab.path.absolute()
        if absolute_path.is_relative_to(PROJECT_DIR):
            message_error("Cannot overwrite built-in file '%s'", absolute_path)
            return

        logger.debug(f"Saving tab to file '{active_tab.path}'")
        active_tab.path.write_text(active_tab.text.get("1.0", "end-1c"))

    def save_as(self) -> None:
        active_tab = self.get_active_tab()
        if active_tab is None:
            message_error("No active tab to save")
            return
        path = ask_save_as_pyscript()
        if path is None:
            return
        absolute_path = active_tab.path.absolute()
        if absolute_path.is_relative_to(PROJECT_DIR):
            message_error("Cannot overwrite built-in file '%s'", absolute_path)
            return

        logger.debug("Saving tab to file '%s'", active_tab.path)
        path.write_text(active_tab.text.get("1.0", "end-1c"))
        active_tab.path = path
        self.tab(active_tab, text=path.name)

    def _add_tab(
        self,
        path: Path | None = None,
        default_content_path: Path | None = None,
    ) -> None:
        name = path.name if path is not None else UNTITLED_TAB_NAME
        logger.debug("Creating new tab '%s'", name)

        try:
            self.add(
                EditorTab(self, self.style, path, default_content_path),
                text=name,
            )
        except EditorTabCreationError:
            message_error("Failed to create tab '%s'", name)
            return

        tab_id = self.tabs()[-1]
        tab = self.nametowidget(tab_id)
        tab_state = tk.DISABLED if self.is_level_active else tk.NORMAL
        self.tab(tab_id, state=tab_state)
        tab.text.config(state=tab_state)
        self.select(tab_id)

    def _update_tab_visuals(self) -> None:
        tab_state = tk.DISABLED if self.is_level_active else tk.NORMAL
        active_tab_id = self.select()
        # Tkinter is just great you have to do all that just to darken some text.
        self.style.map(
            "TNotebook.Tab",
            foreground=[
                (
                    "disabled",
                    (
                        self.style.colors.selectbg
                        if self.is_level_active
                        else self.style.colors.fg
                    ),
                ),
                ("selected", self.style.colors.fg),
                ("!selected", self.style.colors.fg),
            ],
        )
        for tab_id in self.tabs():
            is_active_tab = tab_id == active_tab_id
            self.tab(tab_id, state=tk.NORMAL if is_active_tab else tab_state)
            self.nametowidget(tab_id).text.config(
                state=tab_state,
                fg=(
                    self.style.colors.selectbg
                    if is_active_tab and self.is_level_active
                    else self.style.colors.fg
                ),
            )

    def _on_file_open_requested(self, _event: events.FileOpenRequested) -> None:
        path = ask_open_pyscript()
        if path is not None:
            self.open_tab(path)

    def _on_file_new_requested(self, _event: events.FileNewRequested) -> None:
        self.new_tab()

    def _on_file_save_requested(self, _event: events.FileSaveRequested) -> None:
        self.save()

    def _on_file_save_as_requested(self, _event: events.FileSaveAsRequested) -> None:
        self.save_as()

    def _on_level_opened(self, event: events.LevelOpened) -> None:
        self.open_tab_solution(event.level.pyscript_path)

    def _on_level_select_opened(self, _event: events.LevelSelectOpened) -> None:
        self.open_tab(LEVEL_SELECT_PYSCRIPT_PATH)

    def _on_level_state_changed(self, event: events.LevelStateChanged) -> None:
        self.is_level_active = event.is_active
        self._update_tab_visuals()

    def _on_active_pyscript_requested(self, _event: events.ActivePyscriptRequested) -> None:
        self.save()

        active_tab = self.get_active_tab()
        if active_tab is None:
            message_error("No active tab to run")
            return
        if active_tab.path is None:
            message_error("Cannot run tab without assigned path")
            return

        events.ParseRequested(active_tab.path)
