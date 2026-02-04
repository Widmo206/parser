"""Main interface class containing all tk elements

Created on 2026.02.04
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from editor import Editor
from level import Level
from level_bar import LevelBar
from tile import Tile
from tilemap import Tilemap
from menu_bar import MenuBar


class Interface:
    def __init__(self) -> None:
        self.root = ttk.Window(title="PyScript", themename="darkly")

        self.style = ttk.Style()

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

        self.menu_bar = MenuBar(self.main_frame)
        self.menu_bar.frame.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.margin_frame = ttk.Frame(self.main_frame, bootstyle=ttkc.DARK)
        self.margin_frame.columnconfigure(0, minsize=8)
        self.margin_frame.columnconfigure(1, weight=1)
        self.margin_frame.columnconfigure(2, minsize=8)
        self.margin_frame.rowconfigure(0, weight=1)
        self.margin_frame.grid(column=0, row=1, sticky=ttkc.NSEW)

        self.paned_window = tk.PanedWindow(
            self.margin_frame,
            orient=ttkc.HORIZONTAL,
            sashwidth=8,
            borderwidth=0,
            bg=self.style.colors.dark,
        )
        self.paned_window.grid(column=1, row=0, sticky=ttkc.NSEW)

        self.editor = Editor(self.paned_window)
        self.paned_window.add(self.editor.frame)

        self.level_frame = ttk.Frame(self.paned_window)
        self.level_frame.columnconfigure(0, weight=1)
        self.level_frame.rowconfigure(0, weight=1)
        self.paned_window.add(self.level_frame)

        self.tilemap = Tilemap(self.level_frame, Level.from_path(Level.PATHS[0]).tilemap_layout)
        self.tilemap.frame.grid(column=0, row=0, sticky=ttkc.NSEW)

        self.level_bar = LevelBar(self.level_frame)
        self.level_bar.frame.grid(column=0, row=1, sticky=ttkc.NSEW)

        self.paned_window.paneconfig(self.level_frame, minsize=370)
