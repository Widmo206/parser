"""LevelBar class to select and play through levels

Created on 2026.02.04
Contributors:
    Romcode
"""

from pathlib import Path
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc


class LevelBar:
    def __init__(self, master: tk.Misc) -> None:
        self.frame = ttk.Frame(master, bootstyle=ttkc.DARK)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(5, weight=1)
        self.frame.rowconfigure(0, minsize=4)
        self.frame.rowconfigure(2, minsize=4)

        self.restart_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/restart.png")))
        self.restart_button = ttk.Button(self.frame, image=self.restart_image_tk, bootstyle=ttkc.DARK)
        self.restart_button.grid(column=0, row=1)

        self.back_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/back.png")))
        self.back_button = ttk.Button(self.frame, image=self.back_image_tk, bootstyle=ttkc.DARK)
        self.back_button.grid(column=2, row=1)

        self.play_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/play.png")))
        self.pause_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/pause.png")))
        self.play_button = ttk.Button(self.frame, image=self.play_image_tk, bootstyle=ttkc.DARK)
        self.play_button.grid(column=3, row=1)

        self.forward_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/forward.png")))
        self.forward_button = ttk.Button(self.frame, image=self.forward_image_tk, bootstyle=ttkc.DARK)
        self.forward_button.grid(column=4, row=1)
        
        self.level_select_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/level_select.png")))
        self.level_select_button = ttk.Button(self.frame, image=self.level_select_image_tk, bootstyle=ttkc.DARK)
        self.level_select_button.grid(column=6, row=1)
