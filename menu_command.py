"""MenuCommand class to ease tkinter menu creation and binding

Created on 2026.02.09
Contributors:
    Romcode
"""

from typing import NamedTuple
import tkinter as tk


class MenuCommand(NamedTuple):
    label: str
    sequence: str
    accelerator: str | None = None
    accelerator_sequence: str | None = None

    def add(self, widget: tk.Misc, menu: tk.Menu) -> None:
        def command(_event=None):
            widget.event_generate(self.sequence)

        menu.add_command(
            label=self.label,
            command=command,
            accelerator=self.accelerator,
        )
        widget.bind_all(self.accelerator_sequence, command)
