"""Output class that manages multiple output tabs and routes pyscript output requests.

Created on 2026.05.18
Contributors:
    Romcode
"""

import logging
import tkinter as tk

import ttkbootstrap as ttk

import events
from output_tab import OutputTab

logger = logging.getLogger(__name__)


class Output(ttk.Notebook):
    style: ttk.Style
    output_tabs: dict[int, OutputTab]

    def __init__(self, master: tk.Misc, style: ttk.Style, **kwargs) -> None:
        kwargs.setdefault("padding", 0)
        super().__init__(master, **kwargs)

        self.style = style
        self.output_tabs = {}

        self._get_output_tab(0)

        events.ParseRequested.connect(self._on_parse_requested)
        events.PyscriptOutputRequested.connect(self._on_processor_output_requested)

    def destroy(self) -> None:
        events.ParseRequested.disconnect(self._on_parse_requested)
        events.PyscriptOutputRequested.disconnect(self._on_processor_output_requested)
        super().destroy()

    def _add_output_tab(self, processor_id: int) -> OutputTab:
        logger.debug("Creating output tab for processor %d", processor_id)
        tab = OutputTab(self, self.style)
        self.add(tab, text=f"Processor {processor_id}")
        self.output_tabs[processor_id] = tab
        return tab

    def _get_output_tab(self, processor_id: int) -> OutputTab:
        tab = self.output_tabs.get(processor_id)
        if tab is not None:
            return tab
        return self._add_output_tab(processor_id)

    def _on_parse_requested(self, event: events.ParseRequested) -> None:
        for tab in self.output_tabs.values():
            tab.clear()

        output_tab = self._get_output_tab(0)
        output_tab.print(event.path)
        self.select(output_tab)

    def _on_processor_output_requested(self, event: events.PyscriptOutputRequested) -> None:
        output_tab = self._get_output_tab(event.processor_id)
        output_tab.print(event.text)
        self.select(output_tab)
