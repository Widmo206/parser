"""Testing ttkbootstrap for game visuals

Created on 2026.01.28
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from editor import Editor
from tilemap import Tilemap


def main() -> None:
    root = ttk.Window(themename="darkly")
    root.attributes("-fullscreen", True)
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    main_frame = ttk.Frame(root)
    main_frame.grid()

    editor = Editor(main_frame)
    editor.frame.grid(column=0, row=0, sticky=NSEW, padx=16)

    tilemap = Tilemap(main_frame, 16, 16)
    tilemap.frame.grid(column=1, row=0)

    root.mainloop()


if __name__ == "__main__":
    main()
