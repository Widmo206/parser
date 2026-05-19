"""EditorTab class for writing pyscript in tkinter.

Created on 2026.02.11
Contributors:
    Romcode
"""

from __future__ import annotations

import logging
from math import ceil, floor
from pathlib import Path
import tkinter as tk
from typing import Callable

import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText

from common import PYSCRIPT_EXTENSION, message_error
from errors import EditorTabCreationError

logger = logging.getLogger(__name__)


class EditorTab(ttk.Frame):
    """Tab widget with a text editor, line numbers, and zoom support."""
    DELTA_PER_ZOOM = 120

    path: Path | None
    default_path: Path | None
    is_dirty: bool
    font: str
    font_size: int
    min_font_size: int
    max_font_size: int
    line_text_width: int
    padx_ratio: float
    zoom_factor: float

    line_text: tk.Text
    scrolled_text: ScrolledText
    text: tk.Text

    def __init__(
        self,
        master: tk.Misc,
        style: ttk.Style,
        path: Path | None = None,
        default_path: Path | None = None,
        on_dirty_changed: Callable[[EditorTab], None] | None = None,
        font: str = "Consolas",
        font_size: int = 11,
        min_font_size: int = 1,
        max_font_size: int = 128,
        line_text_width: int = 4,
        padx_ratio: float = 0.5,
        zoom_factor: float = 1.1,
        **kwargs,
    ) -> None:
        if path is not None and path.suffix != PYSCRIPT_EXTENSION:
            logger.warning(
                "Expected file extension '%s' in path '%s'",
                PYSCRIPT_EXTENSION,
                path,
            )
        if default_path is not None and default_path.suffix != PYSCRIPT_EXTENSION:
            logger.warning(
                "Expected file extension '%s' in default path '%s'",
                PYSCRIPT_EXTENSION,
                default_path,
            )

        super().__init__(master, **kwargs)

        self.path = path
        self.default_path = default_path

        self.is_dirty = False
        self._saved_content = ""
        self._on_dirty_changed = on_dirty_changed

        self._normal_color = style.colors.fg
        self._disabled_color = style.colors.selectbg

        self.font = font
        self.font_size = font_size
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.line_text_width = line_text_width
        self.padx_ratio = padx_ratio
        self.zoom_factor = zoom_factor

        self.line_text = tk.Text(self)
        self.line_text.config(
            width=self.line_text_width,
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            takefocus=0,
            state=tk.DISABLED,
            bg=style.colors.primary,
            fg=style.colors.secondary,
        )
        self.line_text.tag_config("active_line", foreground=style.colors.info)
        self.line_text.pack(side=tk.LEFT, fill=tk.Y)

        self.scrolled_text = ScrolledText(
            self,
            hbar=True,
            autohide=True,
            padding=0,
        )
        self.scrolled_text.vbar.config(command=self._on_scrollbar)
        self.scrolled_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text = self.scrolled_text.text
        self.text.configure(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
            highlightthickness=0,
            yscrollcommand=self._on_text_scroll,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            bg=style.colors.bg,
            fg=self._normal_color,
        )

        self._init_bind()
        self._init_load()

    def get_content(self) -> str:
        """Return the current editor contents without the trailing newline."""
        return self.text.get("1.0", "end-1c")

    def mark_saved(self) -> None:
        """Mark the current content as saved and clear the dirty flag."""
        self._saved_content = self.get_content()
        self._set_dirty(False)

    def reload_default(self) -> None:
        """Reload the editor content from the default path."""
        logger.debug("Reloading default tab content")
        if self.default_path is None:
            message_error("Current tab has no default path")
            return

        self._try_load(self.default_path)

    def set_state(self, state: str) -> None:
        """Set the text widget state and update its foreground color."""
        self.text.configure(
            state=state,
            fg = (
                self._disabled_color
                if state == tk.DISABLED
                else self._normal_color
            ),
        )

    def undo(self) -> None:
        """Undo the most recent edit if possible."""
        try:
            self.text.edit_undo()
        except tk.TclError:
            logger.debug("No undo action available")
        else:
            logger.debug("Undoing text change")
            self.text.edit_modified(False)
            self._update_line_numbers()
            self._refresh_dirty_state()

    def redo(self) -> None:
        """Redo the most recently undone edit if possible."""
        try:
            self.text.edit_redo()
        except tk.TclError:
            logger.debug("No redo action available")
        else:
            logger.debug("Redoing text change")
            self.text.edit_modified(False)
            self._update_line_numbers()
            self._refresh_dirty_state()

    def _init_bind(self) -> None:
        self.text.bind("<<Modified>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<ButtonRelease-1>", self._on_change)
        self.text.bind("<FocusIn>", self._on_focus_change)
        self.text.bind("<FocusOut>", self._on_focus_change)
        self.text.bind('<Control-MouseWheel>', self._on_zoom)
        self.line_text.bind('<Control-MouseWheel>', self._on_zoom)

        # Unbind text selection for line numbers.
        for seqence in (
                "<Button-1>",
                "<B1-Motion>",
                "<Double-Button-1>",
                "<Triple-Button-1>",
        ):
            self.line_text.bind(seqence, lambda _: "break")

    def _init_load(self) -> None:
        if self.path is None:
            self.mark_saved()
            return

        if self.path.is_file():
            self._try_load(self.path)
        else:
            logger.debug("No file found at '%s'", self.path)
            if self.default_path is not None and self.default_path.is_file():
                logger.debug("Using default path '%s'", self.default_path)
                self._try_load(self.default_path)
            else:
                if self.default_path is None:
                    logger.debug("No default path provided")
                else:
                    logger.debug("No default file found at '%s'", self.default_path)
                logger.debug("Keeping empty tab")

        self.mark_saved()

    def _refresh_dirty_state(self) -> None:
        self._set_dirty(self.get_content() != self._saved_content)

    def _set_dirty(self, is_dirty: bool) -> None:
        if self.is_dirty == is_dirty:
            return
        self.is_dirty = is_dirty
        if self._on_dirty_changed is not None:
            self._on_dirty_changed(self)

    def _try_load(self, path: Path) -> None:
        logger.debug("Loading text from '%s'", path)
        try:
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", path.read_text(encoding="utf-8"))
            self.text.edit_reset()
            self.text.edit_modified(False)
        except (OSError, UnicodeDecodeError) as error:
            logger.error("Failed to load text from '%s'", path)
            raise EditorTabCreationError from error

    def _update_line_numbers(self) -> None:
        first, _ = self.line_text.yview()
        self.line_text.config(state=tk.NORMAL)
        self.line_text.delete("1.0", tk.END)

        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(
            str(i).rjust(
                self.line_text_width
            ) for i in range(1, line_count + 1)
        )
        self.line_text.insert("1.0", numbers)

        if (
            self.text.cget("state") == tk.NORMAL
            and self.text.focus_get() == self.text
        ):
            current_line = int(self.text.index(tk.INSERT).split(".")[0])
            self.line_text.tag_add(
                "active_line",
                f"{current_line}.0",
                f"{current_line}.end",
            )

        self.line_text.config(state=tk.DISABLED)
        self.line_text.yview_moveto(first)

    def _zoom(self, zoom_delta: int) -> None:
        if zoom_delta == 0:
            return

        raw_font_size = self.font_size * self.zoom_factor ** zoom_delta
        if abs(raw_font_size - self.font_size) < 1:
            if zoom_delta < 0:
                raw_font_size = floor(raw_font_size)
            else:
                raw_font_size = ceil(raw_font_size)
        else:
            raw_font_size = round(raw_font_size)
        self.font_size = min(max(raw_font_size, self.min_font_size), self.max_font_size)

        self.line_text.config(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
        )
        self.text.config(
            font=(self.font, self.font_size),
            padx=self.font_size * self.padx_ratio,
        )

    def _on_text_scroll(self, *args) -> None:
        self.scrolled_text.vbar.set(*args)
        self.line_text.yview_moveto(args[0])

    def _on_scrollbar(self, *args) -> None:
        self.text.yview(*args)
        self.line_text.yview(*args)

    def _on_change(self, _event: tk.Event) -> None:
        self.text.edit_modified(False)
        self._update_line_numbers()
        self._refresh_dirty_state()

    def _on_focus_change(self, _event: tk.Event) -> None:
        self._update_line_numbers()

    def _on_zoom(self, event: tk.Event) -> str:
        self._zoom(round(event.delta / self.DELTA_PER_ZOOM))
        return "break"
