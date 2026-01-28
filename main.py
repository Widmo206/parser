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

    style = ttk.Style()

    main_frame = ttk.Frame(root)
    main_frame.pack(anchor=CENTER, fill=BOTH, expand=True)

    paned_window = tk.PanedWindow(
        main_frame,
        orient=HORIZONTAL,
        sashwidth=8,
        borderwidth=0,
        bg=style.colors.bg,
    )
    paned_window.pack(anchor=CENTER, fill=BOTH, expand=True)

    editor = Editor(paned_window)
    paned_window.add(editor.frame)

    tilemap = Tilemap(paned_window, 16, 16)
    paned_window.add(tilemap.frame)

    root.mainloop()


if __name__ == "__main__":
    main()
