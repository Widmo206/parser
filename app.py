"""App class that serves as the root of the composition tree.

Created on 2026.02.21
Contributors:
    Romcode
"""
import logging

from common import SAVE_PATH, SOLUTIONS_DIR
import events
from game_controller import GameController
from interface import Interface
from save import LevelScore, Save
from scheduler import Scheduler

logger = logging.getLogger(__name__)


class App:
    interface: Interface
    scheduler: Scheduler
    game_controller: GameController | None
    save: Save

    def __init__(self) -> None:
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

        self.save = Save.from_path(SAVE_PATH) if SAVE_PATH.exists() else Save()
        self.interface = Interface(self.save)
        self.scheduler = Scheduler(self.interface)
        self.game_controller = None

        events.ExitRequested.connect(self._on_exit_requested)
        events.CloseLevelRequested.connect(self._on_close_level_requested)
        events.LevelComplete.connect(self._on_level_complete)
        events.LevelSelected.connect(self._on_level_selected)

    def run(self) -> None:
        self.interface.mainloop()

    def _on_close_level_requested(self, _event: events.CloseLevelRequested) -> None:
        if self.game_controller is not None:
            self.game_controller.destroy()
            self.game_controller = None
            events.LevelClosed()

    def _on_level_complete(self, event: events.LevelComplete) -> None:
        if event.level_name in self.save.level_scores:
            # Only keep latest solution path to reload it when opening the
            # level again, but independently save best step and token count.
            old_level_score = self.save.level_scores[event.level_name]
            new_level_score = LevelScore(
                event.level_score.solution_path,
                min(event.level_score.step_count, old_level_score.step_count),
                min(event.level_score.token_count, old_level_score.token_count),
            )

        else:
            new_level_score = event.level_score

        self.save.level_scores[event.level_name] = new_level_score
        self.save.save(SAVE_PATH)

        events.LevelScoreUpdated(new_level_score)
        self.interface.open_level_complete_popup(event.level_name, event.level_score)

    def _on_exit_requested(self, _event: events.ExitRequested) -> None:
        logger.debug("Exiting application")
        self.interface.destroy()

    def _on_level_selected(self, event: events.LevelSelected) -> None:
        self.game_controller = GameController(self.scheduler, event.path)
        events.LevelOpened(self.game_controller.level_model.level)
