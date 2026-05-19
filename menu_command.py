"""MenuCommand class to ease tkinter menu creation and binding.

Created on 2026.02.09
Contributors:
    Romcode
"""

from enum import Enum
import tkinter as tk
from typing import Callable, NamedTuple

from common import open_user_dir, print_enum
import events


class MenuCommandMixin(NamedTuple):
    """Menu command data with optional accelerator bindings."""
    label: str
    command: Callable
    accelerator: str | None = None
    accelerator_sequence: str | None = None

    def add(self, widget: tk.Misc, menu: tk.Menu) -> None:
        """Add the command to the menu and bind its accelerator if provided."""
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
    """Enum base that can build a Tk menu from its members."""
    @classmethod
    def set_menu(cls, widget: tk.Misc) -> None:
        """Create and attach a menu to the widget using enum members."""
        menu = tk.Menu(widget)
        for menu_command in cls:
            menu_command.add(widget, menu)
        widget["menu"] = menu


class FileMenuCommand(MenuCommandEnum):
    """File menu command definitions."""
    NEW              = ("New",        events.FileNewRequested,    "Ctrl+N",       "<Control-n>")
    OPEN             = ("Open...",    events.FileOpenRequested,   "Ctrl+O",       "<Control-o>")
    SAVE             = ("Save",       events.FileSaveRequested,   "Ctrl+S",       "<Control-s>")
    SAVE_AS          = ("Save as...", events.FileSaveAsRequested, "Ctrl+Shift+S", "<Control-S>")
    OPEN_USER_FOLDER = ("Open user directory", open_user_dir)
    RELOAD           = ("Reload default code", events.ReloadDefaultRequested)
    EXIT             = ("Exit",       events.ExitRequested,       "Ctrl+Q",       "<Control-q>")


class EditMenuCommand(MenuCommandEnum):
    """Edit menu command definitions."""
    UNDO = ("Undo", events.UndoRequested, "Ctrl+Z", "<Control-z>")
    REDO = ("Redo", events.RedoRequested, "Ctrl+Y", "<Control-y>")


class ViewMenuCommand(MenuCommandEnum):
    """View menu command definitions."""
    TOGGLE_FULLSCREEN = ("Toggle fullscreen", events.ToggleFullscreenRequested, "F11", "<F11>")


def _test() -> None:
    for enum in (FileMenuCommand, EditMenuCommand, ViewMenuCommand):
        if len(enum) == 0:
            continue
        print()
        print_enum(enum)


if __name__ == "__main__":
    _test()
