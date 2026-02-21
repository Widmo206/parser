"""Common classes and functions used by different modules

Created on 2026.02.07
Contributors:
    Romcode
"""

from enum import Enum
import logging
from pathlib import Path
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Callable, Literal

from platformdirs import user_data_dir

APP_NAME = "PyScript"
APP_AUTHOR = "WidRom"
PYSCRIPT_EXTENSION = ".pyscript"

PROJECT_DIR = Path.cwd()
USER_DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
SOLUTIONS_DIR = USER_DATA_DIR / "solutions"
SAVE_PATH = USER_DATA_DIR / "save.yaml"

FILE_DIALOG_OPTIONS = {
    "initialdir": SOLUTIONS_DIR,
    "filetypes": (("PyScript", f"*{PYSCRIPT_EXTENSION}"), ("Any", "*")),
    "defaultextension": PYSCRIPT_EXTENSION,
}

logger = logging.getLogger(__name__)


def bind_recursive(
    widget: tk.Widget,
    sequence: str | None = None,
    func: Callable | None = None,
    add: Literal["", "+"] | bool | None = None,
) -> None:
    """Same as Widget.bind, but affects all children recursively."""
    widget.bind(sequence, func, add)
    for child in widget.winfo_children():
        bind_recursive(child, sequence, func, add)


def print_enum(enum: Enum) -> None:
    """Nicely fromats and prints enum members for debugging purposes."""
    width = max(len(str(entry)) for entry in enum)
    for entry in enum:
        if isinstance(entry.value, str):
            print(f"{str(entry).ljust(width)} = '{entry.value}'")
        else:
            print(f"{str(entry).ljust(width)} = {entry.value}")


def ask_open_pyscript() -> Path | None:
    logger.debug("Asking user for PyScript file to open")
    path_str = askopenfilename(**FILE_DIALOG_OPTIONS)
    return Path(path_str) if path_str != "" else None


def ask_save_as_pyscript() -> Path | None:
    logger.debug("Asking user for PyScript file save path")
    path_str = asksaveasfilename(**FILE_DIALOG_OPTIONS)
    return Path(path_str) if path_str != "" else None


def get_solution_path(path: Path) -> Path | None:
    logger.debug(f"Creating solution path for '{path.name}'")
    return SOLUTIONS_DIR / f"{path.stem}_solution{PYSCRIPT_EXTENSION}"
