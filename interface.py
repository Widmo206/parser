"""Main interface class containing all tk elements

Created on 2026.02.04
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from editor import Editor
from level_player import LevelPlayer
from menu_bar import MenuBar


class Interface(ttk.Window):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("title", "PyScript")
        kwargs.setdefault("themename", "darkly")
        super().__init__(**kwargs)

        self.geometry("1280x720")
        self.state("zoom")
        self.bind("<F11>", lambda _: self.toggle_fullscreen())

        self.style.colors.set("primary", "#191919")

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

        self.editor = Editor(self.paned_window, style=self.style)
        self.paned_window.add(self.editor)

        self.level_player = LevelPlayer(self.paned_window)
        self.paned_window.add(self.level_player)

        self.paned_window.paneconfig(self.level_player, minsize=370)

    def toggle_fullscreen(self) -> None:
        self.attributes(
            "-fullscreen",
            not self.root.attributes("-fullscreen"),
        )
