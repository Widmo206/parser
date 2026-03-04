"""App class that serves as the root of the composition tree

Created on 2026.02.21
Contributors:
    Romcode
"""

from common import SOLUTIONS_DIR
import events
from game_controller import GameController
from interface import Interface


class App:
    interface: Interface
    game_controller: GameController | None

    def __init__(self) -> None:
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        self.interface = Interface()
        self.game_controller = None

        events.LevelSelectButtonPressed.connect(self._on_level_select_button_pressed)
        events.LevelSelected.connect(self._on_level_selected)

    def run(self) -> None:
        self.interface.mainloop()

    def _on_level_select_button_pressed(self, _event: events.LevelSelectButtonPressed) -> None:
        if self.game_controller is not None:
            self.game_controller.destroy()
            self.game_controller = None

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.game_controller = GameController.from_path(event.path)
