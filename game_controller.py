"""GameController class that links LevelModel and CycleController

Created on 2026.03.04
Contributors:
    Romcode
"""

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

        events.RestartRequested.connect(self._on_restart_requested)
        events.RunRequested.connect(self._on_run_requested)
        events.StepBackRequested.connect(self._on_step_back_requested)
        events.StepForwardRequested.connect(self._on_step_forward_requested)

    def destroy(self) -> None:
        events.RestartRequested.disconnect(self._on_restart_requested)
        events.RunRequested.disconnect(self._on_run_requested)
        events.StepBackRequested.disconnect(self._on_step_back_requested)
        events.StepForwardRequested.disconnect(self._on_step_forward_requested)

    def _on_cycled(self, _event: events.Cycled) -> None:
        self.level_model.step_forward()

    def _on_restart_requested(self, _event: events.RestartRequested) -> None:
        self.cycle_controller.stop()
        self.level_model.restart()

    def _on_run_requested(self, event: events.RunRequested) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
        else:
            parser = Parser(FunctionHolder(), event.path)
            parser.tokenize()
            # TODO: generate processors and pass them to level model tiles
            self.cycle_controller.start()

    def _on_step_back_requested(self, _event: events.StepBackRequested) -> None:
        self.cycle_controller.stop()
        self.level_model.step_back()

    def _on_step_forward_requested(self, _event: events.StepForwardRequested) -> None:
        self.cycle_controller.stop()
        self.level_model.step_forward()