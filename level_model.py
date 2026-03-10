"""LevelModel class to handle level logic and interact with LevelBar and LevelView

Created on 2026.02.18
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path

from enums import Direction, TileAction, TileType
import events
from level import Level
from matrix import Matrix
from tile_model import TileModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LevelModel:
    level: Level
    tile_model_matrix: Matrix[TileModel]

    @classmethod
    def from_path(cls, path: Path) -> LevelModel:
        level = Level.from_path(path)
        tile_model_matrix = level.get_tile_data_matrix().map(TileModel)

        return cls(level, tile_model_matrix)

    def __post_init__(self) -> None:
        events.CycleRequested.connect(self._on_cycle_requested)
        events.RestartButtonPressed.connect(self._on_restart_button_pressed)

    def destroy(self) -> None:
        events.CycleRequested.disconnect(self._on_cycle_requested)
        events.RestartButtonPressed.disconnect(self._on_restart_button_pressed)

    def cycle(self) -> None:
        tile_data_matrix = self.tile_model_matrix.map(
            lambda tile_model: tile_model.tile_data
        )
        tile_actions = [
            (x, y, action)
            for x, y, tile_model in self.tile_model_matrix.iter_xy()
            if (action := tile_model.get_action(x, y, tile_data_matrix)) is not None
        ]
        tile_actions.sort(
            key=lambda xyaction: tile_data_matrix.get(
                xyaction[0],
                xyaction[1],
            ).tile_type.action_priority
        )

        for x, y, action in tile_actions:
            self.process_tile_action(x, y, action)

    def move_tile(self, x: int, y: int, direction: Direction) -> None:
        to_x = x + direction.x
        to_y = y + direction.y

        try:
            from_tile_model = self.tile_model_matrix.get(x, y)
            to_tile_model = self.tile_model_matrix.get(to_x, to_y)
            assert to_tile_model.tile_data.tile_type.is_walkable
        except (IndexError, AssertionError):
            return

        logger.debug(
            "Moving tile %s from (%i, %i) in direction %s (%s)",
            from_tile_model.tile_data.tile_type,
            x,
            y,
            direction,
            to_tile_model.tile_data.tile_type,
        )
        self.set_tile_model(to_x, to_y, from_tile_model)
        self.set_tile_model(x, y, TileModel())

    def process_tile_action(self, x: int, y: int, action: TileAction) -> None:
        tile_data = self.tile_model_matrix.get(x, y).tile_data

        match action:
            case TileAction.MOVE_FORWARD:
                self.move_tile(x, y, tile_data.tile_direction)

            case TileAction.MOVE_BACK:
                self.move_tile(x, y, -tile_data.tile_direction)

            case TileAction.TURN_LEFT:
                self.tile_config(x, y, tile_direction=tile_data.tile_direction.rotate())

            case TileAction.TURN_RIGHT:
                self.tile_config(x, y, tile_direction=tile_data.tile_direction.rotate(True))

            case TileAction.ATTACK:
                # TODO: Implement attacking.
                pass

            case _:
                pass

    def restart(self) -> None:
        for x, y, tile_data in self.level.get_tile_data_matrix().iter_xy():
            self.set_tile_model(x, y, TileModel(tile_data))

    def set_tile_model(
        self,
        x: int,
        y: int,
        tile_model: TileModel
    ) -> None:
        self.tile_model_matrix.set(x, y, tile_model)

        events.TileDataChanged(x, y, tile_model.tile_data)

    def tile_config(
        self,
        x: int,
        y: int,
        tile_type: TileType | str | None = None,
        tile_direction: Direction | None = None,
    ) -> None:
        tile_data = self.tile_model_matrix.get(x, y).tile_data

        if tile_type is not None:
            tile_data.tile_type = TileType.normalize(tile_type)
        if tile_direction is not None:
            tile_data.tile_direction = Direction.normalize(tile_direction)

        events.TileDataChanged(x, y, tile_data)

    def _on_cycle_requested(self, _event: events.CycleRequested) -> None:
        self.cycle()

    def _on_restart_button_pressed(self, _event: events.RestartButtonPressed) -> None:
        self.restart()
