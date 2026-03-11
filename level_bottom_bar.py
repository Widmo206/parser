"""LevelBottomBar class to holds buttons for playing through levels

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


class LevelBottomBar(ttk.Frame):
    restart_image_tk: ImageTk.PhotoImage
    step_back_image_tk: ImageTk.PhotoImage
    run_image_tk: ImageTk.PhotoImage
    pause_image_tk: ImageTk.PhotoImage
    step_forward_image_tk: ImageTk.PhotoImage
    level_select_image_tk: ImageTk.PhotoImage

    restart_button: ttk.Button
    step_back_button: ttk.Button
    run_button: ttk.Button
    step_forward_button: ttk.Button
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
            command=events.RestartButtonPressed,
            image=self.restart_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.restart_button.grid(column=0, row=1)

        self.step_back_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/step_back.png")))
        self.step_back_button = ttk.Button(
            self,
            command=events.StepBackButtonPressed,
            image=self.step_back_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.step_back_button.grid(column=2, row=1)

        self.run_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/run.png")))
        self.pause_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/pause.png")))
        self.run_button = ttk.Button(
            self,
            command=events.RunButtonPressed,
            image=self.run_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.run_button.grid(column=3, row=1)

        self.step_forward_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/step_forward.png")))
        self.step_forward_button = ttk.Button(
            self,
            command=events.StepForwardButtonPressed,
            image=self.step_forward_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.step_forward_button.grid(column=4, row=1)
        
        self.level_select_image_tk = ImageTk.PhotoImage(Image.open(Path("sprites/level_select.png")))
        self.level_select_button = ttk.Button(
            self,
            command=events.LevelSelectButtonPressed,
            image=self.level_select_image_tk,
            bootstyle=kwargs["bootstyle"],
        )
        self.level_select_button.grid(column=6, row=1)

        events.CyclingStarted.connect(self._on_cycling_started)
        events.CyclingStopped.connect(self._on_cycling_stopped)

    def destroy(self) -> None:
        events.CyclingStarted.disconnect(self._on_cycling_started)
        events.CyclingStopped.disconnect(self._on_cycling_stopped)
        super().destroy()

    def _on_cycling_started(self, _event: events.CyclingStarted) -> None:
        self.run_button.config(image=self.pause_image_tk)

    def _on_cycling_stopped(self, _event: events.CyclingStopped) -> None:
        self.run_button.config(image=self.run_image_tk)

