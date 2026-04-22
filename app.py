"""App class that serves as the root of the composition tree

Created on 2026.02.21
Contributors:
    Romcode
"""
import logging

from common import SAVE_PATH, SOLUTIONS_DIR
import events
from game_controller import GameController
from interface import Interface
from save import Save
from scheduler import Scheduler

logger = logging.getLogger(__name__)


class App:
    interface: Interface
    scheduler: Scheduler
    game_controller: GameController | None
    save: Save

    def __init__(self) -> None:
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        self.interface = Interface()
        self.scheduler = Scheduler(self.interface)
        self.game_controller = None
        self.save = Save.from_path(SAVE_PATH) if SAVE_PATH.exists() else Save()

        events.ExitRequested.connect(self._on_exit_requested)
        events.CloseLevelRequested.connect(self._on_close_level_requested)
        events.LevelSelected.connect(self._on_level_selected)

    def run(self) -> None:
        self.interface.mainloop()

    def _on_close_level_requested(self, _event: events.CloseLevelRequested) -> None:
        if self.game_controller is not None:
            self.game_controller.destroy()
            self.game_controller = None
            events.LevelClosed()

    def _on_exit_requested(self, _event: events.ExitRequested) -> None:
        logger.debug("Exiting application")
        self.interface.destroy()

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.game_controller = GameController(self.scheduler, event.path)
        events.LevelOpened(self.game_controller.level_model.level)
