"""GameController class that links LevelModel and CycleController

Created on 2026.03.04
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from cycle_controller import CycleController
import events
from level_model import LevelModel
from parser import FunctionHolder, Parser


@dataclass(frozen=True)
class GameController:
    level_model: LevelModel
    cycle_controller: CycleController

    @classmethod
    def from_path(cls, path: Path) -> GameController:
        return cls(
            LevelModel.from_path(path),
            CycleController(),
        )

    def __post_init__(self) -> None:
        events.RunRequested.connect(self._on_run_requested)

    def destroy(self) -> None:
        events.RunRequested.disconnect(self._on_run_requested)
        self.level_model.destroy()
        self.cycle_controller.destroy()

    def _on_run_requested(self, event: events.RunRequested) -> None:
        parser = Parser(FunctionHolder(), event.path)
        parser.tokenize()
        # TODO: generate processors and pass them to level model tiles
        self.cycle_controller.run()
