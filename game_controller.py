"""GameController class that links LevelModel and CycleController

Created on 2026.03.04
Contributors:
    Romcode
"""

from pathlib import Path

from cycle_controller import CycleController
import events
from level_model import LevelModel
from scheduler import Scheduler

class GameController:
    cycle_controller: CycleController
    level_model: LevelModel

    def __init__(self, scheduler: Scheduler, path: Path) -> None:
        self.cycle_controller = CycleController(scheduler)
        self.level_model = LevelModel.from_path(path, scheduler)

        events.Cycled.connect(self._on_cycled)
        events.LevelComplete.connect(self._on_level_complete)
        events.ParseRequested.connect(self._on_parse_requested)
        events.RestartRequested.connect(self._on_restart_requested)
        events.RunPauseRequested.connect(self._on_run_pause_requested)
        events.StepBackRequested.connect(self._on_step_back_requested)
        events.StepForwardRequested.connect(self._on_step_forward_requested)

    def destroy(self) -> None:
        events.LevelStateChanged(False)
        events.Cycled.disconnect(self._on_cycled)
        events.LevelComplete.disconnect(self._on_level_complete)
        events.ParseRequested.disconnect(self._on_parse_requested)
        events.RestartRequested.disconnect(self._on_restart_requested)
        events.RunPauseRequested.disconnect(self._on_run_pause_requested)
        events.StepBackRequested.disconnect(self._on_step_back_requested)
        events.StepForwardRequested.disconnect(self._on_step_forward_requested)

    def _on_cycled(self, _event: events.Cycled) -> None:
        self.level_model.step_forward()

    def _on_level_complete(self, _event: events.LevelComplete) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()

    def _on_parse_requested(self, event: events.ParseRequested) -> None:
        self.level_model.create_processors(event.path)
        if event.queue_cycle_start:
            self.cycle_controller.start()
        else:
            self.level_model.step_forward()

    def _on_restart_requested(self, _event: events.RestartRequested) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
        self.level_model.restart()
        events.LevelStateChanged(False)

    def _on_run_pause_requested(self, _event: events.RunPauseRequested) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
            return

        if len(self.level_model.history) == 0:
            events.LevelStateChanged(True)
            events.ActivePyscriptRequested()
            return

        self.cycle_controller.start()

    def _on_step_back_requested(self, _event: events.StepBackRequested) -> None:
        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
        self.level_model.step_back()

        if len(self.level_model.history) == 0:
            events.LevelStateChanged(False)

    def _on_step_forward_requested(self, _event: events.StepForwardRequested) -> None:
        if len(self.level_model.history) == 0:
            events.LevelStateChanged(True)
            events.ActivePyscriptRequested()
            return

        if self.cycle_controller.is_running:
            self.cycle_controller.stop()
        self.level_model.step_forward()
