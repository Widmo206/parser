"""Common classes and functions used by different modules.

Created on 2026.02.07
Contributors:
    Romcode
"""

from enum import Enum
import logging
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo, showerror, showwarning
from typing import Callable, Literal

from platformdirs import user_data_dir

APP_NAME = "PyScript"
APP_AUTHOR = "WidRom"
PYSCRIPT_EXTENSION = ".pyscript"

PROJECT_DIR = Path.cwd()
USER_DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
SAVE_PATH = USER_DATA_DIR / "save.yaml"
SOLUTIONS_DIR = USER_DATA_DIR / "solutions"

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
    logger.debug("Creating solution path for %s", path.name)
    return SOLUTIONS_DIR / f"{path.stem}_solution{PYSCRIPT_EXTENSION}"


def message_info(message: str, *args) -> None:
    logger.info(message, *args)
    showinfo("Info", message % args)


def message_error(message: str, *args) -> None:
    logger.error(message, *args)
    showerror("Error", message % args)


def message_warning(message: str, *args) -> None:
    logger.warning(message, *args)
    showwarning("Warning", message % args)


def normalize_path(value: Path | str) -> Path:
    """Safely convert a Path or string to a Path."""
    if isinstance(value, Path):
        return value
    return Path(value)


def open_user_dir() -> None:
    try:
        if sys.platform == "win32":
            os.startfile(str(USER_DATA_DIR))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(USER_DATA_DIR)], check=True)
        else:
            subprocess.run(["xdg-open", str(USER_DATA_DIR)], check=True)
    except OSError as e:
        message_error("Failed to open user directory '%s': %s", USER_DATA_DIR, e)
    except subprocess.CalledProcessError as e:
        message_error("Failed to open user directory '%s': %s", USER_DATA_DIR, e)
