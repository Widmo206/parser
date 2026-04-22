"""Interface class containing all tk elements

Created on 2026.02.04
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events
from level_complete_popup import LevelCompletePopup
from level_manager import LevelManager
from menu_bar import MenuBar
from pyscript_manager import PyscriptManager

logger = logging.getLogger(__name__)


class Interface(ttk.Window):
    MIN_RIGHT_PANEL_SIZE = 500

    main_frame: ttk.Frame
    menu_bar: MenuBar
    margin_frame: ttk.Frame
    paned_window: tk.PanedWindow
    pyscript_manager: PyscriptManager
    level_manager: LevelManager
    level_complete_popup: LevelCompletePopup | None

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("title", "PyScript")
        kwargs.setdefault("themename", "darkly")
        super().__init__(**kwargs)

        self.geometry("1280x720")
        self.state("zoom")

        self.style.colors.set("primary", "#191919")
        self.style.layout("TNotebook", [])

        self.main_frame = ttk.Frame(self)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

        self.menu_bar = MenuBar(self.main_frame)
        self.menu_bar.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.margin_frame = ttk.Frame(self.main_frame, bootstyle=ttkc.DARK)
        self.margin_frame.columnconfigure(0, minsize=8)
        self.margin_frame.columnconfigure(1, weight=1)
        self.margin_frame.columnconfigure(2, minsize=8)
        self.margin_frame.rowconfigure(0, weight=1)
        self.margin_frame.rowconfigure(2, minsize=8)
        self.margin_frame.grid(column=0, row=1, sticky=ttkc.NSEW)

        self.paned_window = tk.PanedWindow(
            self.margin_frame,
            orient=ttkc.HORIZONTAL,
            sashwidth=8,
            borderwidth=0,
            bg=self.style.colors.dark,
        )
        self.paned_window.grid(column=1, row=0, sticky=ttkc.NSEW)

        self.pyscript_manager = PyscriptManager(self.paned_window, self.style)
        self.paned_window.add(self.pyscript_manager)

        self.level_manager = LevelManager(self.paned_window)
        self.paned_window.add(self.level_manager)
        self.level_complete_popup = None

        self.paned_window.paneconfig(self.level_manager, minsize=self.MIN_RIGHT_PANEL_SIZE)

        self.update_idletasks()
        self.paned_window.sash_place(0, int(self.paned_window.winfo_width() * 0.5), 0)
        self.pyscript_manager.sash_place(0, 0, int(self.pyscript_manager.winfo_height() * 0.75))

        events.ClosePopupRequested.connect(self._on_close_popup_requested)
        events.CloseLevelRequested.connect(self._on_close_level_requested)
        events.LevelComplete.connect(self._on_level_complete)
        events.RestartRequested.connect(self._on_restart_requested)
        events.ToggleFullscreenRequested.connect(self._on_toggle_fullscreen_requested)

    def close_popup(self) -> None:
        if self.level_complete_popup is None:
            return

        self.level_complete_popup.destroy()
        self.level_complete_popup = None

    def destroy(self) -> None:
        events.ClosePopupRequested.disconnect(self._on_close_popup_requested)
        events.CloseLevelRequested.disconnect(self._on_close_level_requested)
        events.LevelComplete.disconnect(self._on_level_complete)
        events.RestartRequested.disconnect(self._on_restart_requested)
        events.ToggleFullscreenRequested.disconnect(self._on_toggle_fullscreen_requested)
        super().destroy()

    def _on_close_level_requested(self, _event: events.CloseLevelRequested) -> None:
        self.close_popup()


    def _on_close_popup_requested(self, _event: events.ClosePopupRequested) -> None:
        self.close_popup()

    def _on_level_complete(self, event: events.LevelComplete) -> None:
        self.close_popup()

        self.level_complete_popup = LevelCompletePopup(self)

    def _on_restart_requested(self, _event: events.RestartRequested) -> None:
        self.close_popup()

    def _on_toggle_fullscreen_requested(self, _event: events.ToggleFullscreenRequested) -> None:
        new_mode = not self.attributes("-fullscreen")
        logger.debug(f"Setting fullscreen mode to {new_mode}")
        self.attributes("-fullscreen", new_mode)
