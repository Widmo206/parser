"""LevelController class to holds buttons for playing through levels

Created on 2026.02.04
Contributors:
    Romcode
"""

from pathlib import Path
from PIL import ImageTk, Image
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events


class LevelController(ttk.Frame):
    restart_image_tk: ImageTk.PhotoImage
    back_image_tk: ImageTk.PhotoImage
    run_image_tk: ImageTk.PhotoImage
    pause_image_tk: ImageTk.PhotoImage
    forward_image_tk: ImageTk.PhotoImage
    level_select_image_tk: ImageTk.PhotoImage

    restart_button: ttk.Button
    back_button: ttk.Button
    run_button: ttk.Button
    forward_button: ttk.Button
    level_select_button: ttk.Button

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        kwargs.setdefault("bootstyle", ttkc.DARK)
        super().__init__(master, **kwargs)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(5, weight=1)
        self.rowconfigure(0, minsize=8)

        self.restart_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/restart.png")))
        self.restart_button = ttk.Button(
            self,
            image=self.restart_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.restart_button.grid(column=0, row=1)

        self.back_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/back.png")))
        self.back_button = ttk.Button(
            self,
            image=self.back_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.back_button.grid(column=2, row=1)

        self.run_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/run.png")))
        self.pause_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/pause.png")))
        self.run_button = ttk.Button(
            self,
            command=events.RunButtonPressed,
            image=self.run_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.run_button.grid(column=3, row=1)

        self.forward_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/forward.png")))
        self.forward_button = ttk.Button(
            self,
            image=self.forward_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.forward_button.grid(column=4, row=1)
        
        self.level_select_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/level_select.png")))
        self.level_select_button = ttk.Button(
            self,
            command=events.LevelSelectButtonPressed,
            image=self.level_select_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.level_select_button.grid(column=6, row=1)
