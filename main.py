"""Pyscript - a coding learning game

Created on 2026.01.28
Contributors:
    Romcode
    Widmo
"""

import logging

from common import SOLUTIONS_DIR
import events
from interface import Interface
from level_model import LevelModel
from parser import FunctionHolder, Parser


class Main:
    interface: Interface
    level_model: LevelModel | None
    parser: Parser | None

    def __init__(self) -> None:
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        events.LevelSelectButtonPressed.connect(self._on_level_select_button_pressed)
        events.LevelSelected.connect(self._on_level_selected)
        events.RunRequested.connect(self._on_run_requested)

        self.interface = Interface()
        self.interface.mainloop()

    def _on_level_select_button_pressed(self, _event: events.LevelSelectButtonPressed) -> None:
        self.level_model.destroy()
        self.level_model = None

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.level_model = LevelModel(event.path)

    def _on_run_requested(self, event: events.RunRequested) -> None:
        self.parser = Parser(FunctionHolder(), event.path)
        print(self.parser.tokenize())


def setup_logging() -> None:
    open("latest.log", "w", encoding="utf-8").close() # Clears the previous logs
    logging.basicConfig(
        filename='latest.log',
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)-13s | %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
    )
    # Needed because PIL was flooding the logs
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging()
    Main()
