"""LevelCompletePopup class that opens a window with completion info

Created on 2026.04.02
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events

logger = logging.getLogger(__name__)


class LevelCompletePopup(ttk.Toplevel):
    SIZE = (440, 320)

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.title("Level complete")
        self.transient(master)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", events.ClosePopupRequested)
        self.bind("<Escape>", lambda _: events.ClosePopupRequested())

        width, height = self.SIZE
        x = master.winfo_rootx() + (master.winfo_width() - width) // 2
        y = master.winfo_rooty() + (master.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=ttkc.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        header = ttk.Label(
            main_frame,
            text="Level complete!",
            anchor=ttkc.CENTER,
            font=("Segoe UI", 18),
            bootstyle=(ttkc.SUCCESS, ttkc.INVERSE),
            padding=(0, 10),
        )
        header.grid(column=0, row=0, sticky=ttkc.EW)

        stats_frame = ttk.Frame(main_frame, padding=(0, 12))
        stats_frame.grid(column=0, row=1, sticky=ttkc.NSEW)
        stats_frame.columnconfigure(1, weight=1)

        # TODO: Pass completion stats correctly.
        stats = (
            ("Level", "level_name"),
            ("Steps", "step_count"),
            ("Tokens", "token_count"),
            ("Script", "script_name"),
        )

        for row, (name, value) in enumerate(stats):
            ttk.Label(
                stats_frame,
                text=f"{name}:",
                anchor=ttkc.W,
                font=("Segoe UI", 11, "bold"),
            ).grid(column=0, row=row, sticky=ttkc.W, pady=4, padx=(0, 12))
            ttk.Label(
                stats_frame,
                text=value,
                anchor=ttkc.W,
                font=("Segoe UI", 11),
            ).grid(column=1, row=row, sticky=ttkc.W, pady=4)

        buttons = ttk.Frame(main_frame)
        buttons.grid(column=0, row=2, sticky=ttkc.E)
        ttk.Button(
            buttons,
            text="Close",
            command=events.ClosePopupRequested,
            bootstyle=ttkc.SECONDARY,
        ).grid(column=0, row=0, padx=(0, 8))
        ttk.Button(
            buttons,
            text="Level select",
            command=events.CloseLevelRequested,
            bootstyle=ttkc.PRIMARY,
        ).grid(column=1, row=0, padx=(0, 8))
        ttk.Button(
            buttons,
            text="Restart",
            command=events.RestartRequested,
            bootstyle=ttkc.SUCCESS,
        ).grid(column=2, row=0)

        self.grab_set()
        self.focus_set()
