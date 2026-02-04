"""MenuBar class to manage pyscript files

Created on 2026.02.01
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc


class MenuBar:
    def __init__(self, master: tk.Misc) -> None:
        self.frame = ttk.Frame(master, bootstyle=ttkc.DARK)

        self.file_menu_button = ttk.Menubutton(self.frame, text="File", bootstyle=ttkc.DARK)
        self.file_menu_button.grid(column=0, row=0)

        self.file_menu = tk.Menu(self.file_menu_button)
        self.file_menu.add_command(label="New...", command=None)
        self.file_menu.add_command(label="Open...", command=None)
        self.file_menu.add_command(label="Save", command=None)
        self.file_menu.add_command(label="Save as...", command=None)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=None)
        self.file_menu_button["menu"] = self.file_menu

        self.edit_menu_button = ttk.Menubutton(self.frame, text="Edit", bootstyle=ttkc.DARK)
        self.edit_menu_button.grid(column=1, row=0)
