"""MenuBar class to manage pyscript files.

Created on 2026.02.01
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from menu_command import EditMenuCommand, FileMenuCommand, ViewMenuCommand


class MenuBar(ttk.Frame):
    """Menu bar frame wiring File/Edit/View commands."""
    file_menu_button: ttk.Menubutton
    edit_menu_button: ttk.Menubutton
    view_menu_button: ttk.Menubutton

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        kwargs.setdefault("bootstyle", ttkc.DARK)
        super().__init__(master, **kwargs)

        self.file_menu_button = ttk.Menubutton(self, text="File", bootstyle=kwargs["bootstyle"])
        self.file_menu_button.grid(column=0, row=0)
        FileMenuCommand.set_menu(self.file_menu_button)

        self.edit_menu_button = ttk.Menubutton(self, text="Edit", bootstyle=kwargs["bootstyle"])
        self.edit_menu_button.grid(column=1, row=0)
        EditMenuCommand.set_menu(self.edit_menu_button)

        self.view_menu_button = ttk.Menubutton(self, text="View", bootstyle=kwargs["bootstyle"])
        self.view_menu_button.grid(column=2, row=0)
        ViewMenuCommand.set_menu(self.view_menu_button)
