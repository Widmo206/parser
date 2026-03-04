"""GameController class that links LevelModel and CycleController

Created on 2026.03.04
Contributors:
    Romcode
"""

from dataclasses import dataclass
from pathlib import Path

from cycle_controller import CycleController
import events
from level_model import LevelModel
from parser import FunctionHolder, Parser
from scheduler import Scheduler


class GameController:
    cycle_controller: CycleController
    level_model: LevelModel

    def __init__(self, scheduler: Scheduler, path: Path) -> None:
        self.cycle_controller = CycleController(scheduler)
        self.level_model = LevelModel.from_path(path)
        events.RunRequested.connect(self._on_run_requested)

    def destroy(self) -> None:
        events.RunRequested.disconnect(self._on_run_requested)
        self.cycle_controller.destroy()
        self.level_model.destroy()

    def _on_run_requested(self, event: events.RunRequested) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
        else:
            parser = Parser(FunctionHolder(), event.path)
            parser.tokenize()
            # TODO: generate processors and pass them to level model tiles
            self.cycle_controller.start()
