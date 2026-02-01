"""Testing ttkbootstrap for game visuals

Created on 2026.01.28
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

from editor import Editor
from level import Level
from tilemap import Tilemap
from menu_bar import MenuBar


def main() -> None:
    root = ttk.Window(themename="darkly")
    root.attributes("-fullscreen", True)

    style = ttk.Style()

    main_frame = ttk.Frame(root)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    main_frame.pack(anchor=ttkc.CENTER, fill=ttkc.BOTH, expand=True)

    menu_bar = MenuBar(main_frame)
    menu_bar.frame.grid(column=0, row=0, sticky=ttkc.NSEW)

    paned_window = tk.PanedWindow(
        main_frame,
        orient=ttkc.HORIZONTAL,
        sashwidth=8,
        borderwidth=0,
        bg=style.colors.bg,
    )
    paned_window.grid(column=0, row=1, sticky=ttkc.NSEW)

    editor = Editor(paned_window)
    paned_window.add(editor.frame)

    tilemap = Tilemap(paned_window, Level.from_path(Level.PATHS[0]).tilemap_layout)
    paned_window.add(tilemap.frame)

    root.mainloop()


if __name__ == "__main__":
    main()
