"""MenuCommand class to ease tkinter menu creation and binding

Created on 2026.02.09
Contributors:
    Romcode
"""

from common import print_enum
from enum import Enum
from typing import Callable, NamedTuple
import tkinter as tk

import events


class MenuCommandMixin(NamedTuple):
    label: str
    command: Callable
    accelerator: str | None = None
    accelerator_sequence: str | None = None

    def add(self, widget: tk.Misc, menu: tk.Menu) -> None:
        menu.add_command(
            label=self.label,
            command=self.command,
            accelerator=self.accelerator,
        )
        widget.bind_all(
            self.accelerator_sequence,
            lambda _: self.command(),
        )


class FileMenuCommand(MenuCommandMixin, Enum):
    NEW     = ("New", events.FileNewRequested, "Ctrl+N", "<Control-n>")
    OPEN    = ("Open...", events.FileOpenRequested, "Ctrl+O", "<Control-o>")
    SAVE    = ("Save", events.FileSaveRequested, "Ctrl+S", "<Control-s>")
    SAVE_AS = ("Save as...", events.FileSaveAsRequested, "Ctrl+Shift+S", "<Control-Shift-n>")
    EXIT    = ("Exit", events.ExitRequested, "Ctrl+Q", "<Control-q>")


def _test() -> None:
        print()
        print_enum(FileMenuCommand)


if __name__ == "__main__":
    _test()
