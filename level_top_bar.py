"""LevelTopBar class to display level name and best score.

Created on 2026.03.11
Contributors:
    Romcode
"""

import tkinter as tk

import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkc

import events
from save import LevelScore

class LevelTopBar(ttk.Frame):
    name_label: ttk.Label
    step_count_label: ttk.Label
    token_count_label: ttk.Label

    def __init__(
        self,
        master: tk.Misc,
        name: str,
        level_score: LevelScore | None = None,
        separation: int = 4,
        **kwargs,
    ) -> None:
        kwargs.setdefault("padding", 8)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, minsize=separation)
        self.columnconfigure(4, minsize=separation)
        self.columnconfigure(6, weight=1)

        self.name_label = ttk.Label(
            self,
            text=name,
            anchor=tk.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.name_label.grid(column=1, row=0, sticky=tk.NSEW)
        self.step_count_label = ttk.Label(
            self,
            anchor=tk.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.step_count_label.grid(column=3, row=0, sticky=tk.NSEW)
        self.token_count_label = ttk.Label(
            self,

            anchor=tk.CENTER,
            font=("Segoe UI", 16),
            padding=16,
            bootstyle=(ttkc.PRIMARY, ttkc.INVERSE),
        )
        self.token_count_label.grid(column=5, row=0, sticky=tk.NSEW)

        self._update_labels(level_score)
        events.LevelScoreUpdated.connect(self._on_level_score_updated)

    def destroy(self) -> None:
        events.LevelScoreUpdated.disconnect(self._on_level_score_updated)
        super().destroy()

    def _update_labels(self, level_score: LevelScore | None) -> None:
        step_text = "N/A" if level_score is None else str(level_score.step_count)
        self.step_count_label.config(
            text=f"Best step count: {step_text}"
        )
        token_text = "N/A" if level_score is None else str(level_score.token_count)
        self.token_count_label.config(
            text=f"Best token count: {token_text}",
        )

    def _on_level_score_updated(self, event: events.LevelScoreUpdated) -> None:
        self._update_labels(event.level_score)
