"""MenuCommand class to ease tkinter menu creation and binding.

Created on 2026.02.09
Contributors:
    Romcode
"""

import tkinter as tk
from typing import Callable, NamedTuple

from common import open_user_dir, print_enum
from enum import Enum
import events


class MenuCommandMixin(NamedTuple):
    label: str
    command: Callable
    accelerator: str | None = None
    accelerator_sequence: str | None = None

    def add(self, widget: tk.Misc, menu: tk.Menu) -> None:
        if self.accelerator is None:
            menu.add_command(label=self.label, command=self.command)
        else:
            menu.add_command(
                label=self.label,
                command=self.command,
                accelerator=self.accelerator,
            )

        if self.accelerator_sequence is not None:
            widget.bind_all(
                self.accelerator_sequence,
                lambda _: self.command(),
            )


class MenuCommandEnum(MenuCommandMixin, Enum):
    @classmethod
    def set_menu(cls, widget: tk.Misc) -> None:
        menu = tk.Menu(widget)
        for menu_command in cls:
            menu_command.add(widget, menu)
        widget["menu"] = menu


class FileMenuCommand(MenuCommandEnum):
    NEW              = ("New",        events.FileNewRequested,    "Ctrl+N",       "<Control-n>")
    OPEN             = ("Open...",    events.FileOpenRequested,   "Ctrl+O",       "<Control-o>")
    SAVE             = ("Save",       events.FileSaveRequested,   "Ctrl+S",       "<Control-s>")
    SAVE_AS          = ("Save as...", events.FileSaveAsRequested, "Ctrl+Shift+S", "<Control-S>")
    OPEN_USER_FOLDER = ("Open user directory", open_user_dir)
    RELOAD           = ("Reload default code", events.ReloadDefaultRequested)
    EXIT             = ("Exit",       events.ExitRequested,       "Ctrl+Q",       "<Control-q>")


class ViewMenuCommand(MenuCommandEnum):
    TOGGLE_FULLSCREEN = ("Toggle fullscreen", events.ToggleFullscreenRequested, "F11", "<F11>")


def _test() -> None:
    for enum in (FileMenuCommand, ViewMenuCommand):
        if len(enum) == 0:
            continue
        print()
        print_enum(enum)


if __name__ == "__main__":
    _test()
