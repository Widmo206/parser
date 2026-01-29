"""Testing ttkbootstrap for game visuals

Created on 2026.01.28
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from editor import Editor
from tilemap import Tilemap


def main() -> None:
    root = ttk.Window(themename="darkly")
    root.attributes("-fullscreen", True)

    style = ttk.Style()

    main_frame = ttk.Frame(root)
    main_frame.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

    paned_window = tk.PanedWindow(
        main_frame,
        orient=ttkc.HORIZONTAL,
        sashwidth=8,
        borderwidth=0,
        bg=style.colors.bg,
    )
    paned_window.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

    editor = Editor(paned_window)
    paned_window.add(editor.frame)

    tilemap = Tilemap(paned_window, 7, 7)
    paned_window.add(tilemap.frame)

    root.mainloop()


if __name__ == "__main__":
    main()
