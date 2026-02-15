"""MenuCommand class to ease tkinter menu creation and binding

Created on 2026.02.09
Contributors:
    Romcode
"""

from typing import Callable, NamedTuple
import tkinter as tk


class MenuCommand(NamedTuple):
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
