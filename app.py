"""App class that serves as the root of the composition tree

Created on 2026.02.21
Contributors:
    Romcode
"""

from common import SOLUTIONS_DIR
import events
from interface import Interface
from level_model import LevelModel
from parser import FunctionHolder, Parser


class App:
    interface: Interface
    level_model: LevelModel | None
    parser: Parser | None

    def __init__(self) -> None:
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        self.interface = Interface()
        self.level_model = None
        self.parser = None

        events.LevelSelectButtonPressed.connect(self._on_level_select_button_pressed)
        events.LevelSelected.connect(self._on_level_selected)
        events.RunRequested.connect(self._on_run_requested)

    def run(self) -> None:
        self.interface.mainloop()

    def _on_level_select_button_pressed(self, _event: events.LevelSelectButtonPressed) -> None:
        self.level_model.destroy()
        self.level_model = None

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.level_model = LevelModel(event.path)

    def _on_run_requested(self, event: events.RunRequested) -> None:
        self.parser = Parser(FunctionHolder(), event.path)
        self.parser.tokenize()
