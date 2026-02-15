"""Main interface class containing all tk elements

Created on 2026.02.04
Contributors:
    Romcode
"""

import logging
from pathlib import Path
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from common import select_pyscript
from level_manager import LevelManager
from menu_bar import MenuBar
from pyscript_manager import PyscriptManager

logger = logging.getLogger(__name__)


class Interface(ttk.Window):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("title", "PyScript")
        kwargs.setdefault("themename", "darkly")
        super().__init__(**kwargs)

        self.geometry("1280x720")
        self.state("zoom")
        self.bind("<F11>", lambda _: self.toggle_fullscreen())

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

        self.paned_window.paneconfig(self.level_manager, minsize=370)

        self.update_idletasks()
        self.paned_window.sash_place(0, int(self.paned_window.winfo_width() * 0.5), 0)
        self.pyscript_manager.sash_place(0, 0, int(self.pyscript_manager.winfo_height() * 0.75))

    def toggle_fullscreen(self) -> None:
        new_mode = not self.attributes("-fullscreen")
        logger.debug(f"Setting fullscreen mode to {new_mode}")
        self.attributes("-fullscreen", new_mode)

    def _on_menu_bar_file_new(self, _event: tk.Event) -> None:
        if self.level_manager.level_player is None:
            self.pyscript_manager.editor.new_tab()
        else:
            self.pyscript_manager.editor.open_tab_solution(self.level_manager.level_player.level.pyscript_path)

    def _on_menu_bar_file_open(self, _event: tk.Event) -> None:
        path = select_pyscript()
        if path is not None:
            self.pyscript_manager.editor.open_tab(path)

    def _on_exit_requested(self, _event: tk.Event) -> None:
        logger.debug("Exiting application")
        self.destroy()

    def _on_level_manager_level_opened(self, _event: tk.Event) -> None:
        pyscript_path = self.level_manager.level_player.level.pyscript_path
        if pyscript_path is None:
            logger.warning(f"Loaded level has no initial PyScript")
        else:
            self.pyscript_manager.editor.open_tab_solution(pyscript_path)

    def _on_level_manager_level_select_opened(self, _event: tk.Event) -> None:
        self.pyscript_manager.editor.open_tab(Path("pyscript/level_select.pyscript"))
