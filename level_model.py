"""LevelModel class to handle level logic and interact with LevelBottomBar and LevelView

Created on 2026.02.18
Contributors:
    Romcode
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
import logging
from pathlib import Path

from enums import Direction, MoveMixin, SpecialMove, TileAction, TileType
import events
from level import Level
from matrix import Matrix
from scheduler import Scheduler
from tile_data import TileData
from tile_model import TileModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LevelModel:
    ATTACK_DURATION = 250

    level: Level
    scheduler: Scheduler
    tile_model_matrix: Matrix[TileModel]
    history: list[Matrix[TileModel]] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path, scheduler: Scheduler) -> LevelModel:
        level = Level.from_path(path)
        tile_model_matrix = level.get_tile_data_matrix().map(TileModel)

        return cls(level, scheduler, tile_model_matrix)

    @staticmethod
    def get_special_move_result(
        move: SpecialMove,
        from_tile_model: TileModel,
        _to_tile_model: TileModel,
    ) -> TileModel:
        match move:
            case SpecialMove.PLAYER_WIN:
                return TileModel(TileData(TileType.WIN))

            case SpecialMove.ENEMY_KILL_PLAYER:
                return TileModel(
                    from_tile_model.tile_data,
                    from_tile_model.processor,
                )

            case SpecialMove.PLAYER_OPEN_DOOR | SpecialMove.ENEMY_OPEN_DOOR:
                return TileModel(
                    TileData(
                        (
                            TileType.PLAYER
                            if move is SpecialMove.PLAYER_OPEN_DOOR
                            else TileType.ENEMY
                        ),
                        from_tile_model.tile_data.tile_direction,
                    ),
                    from_tile_model.processor,
                )

            case SpecialMove.PLAYER_PICKUP_KEY | SpecialMove.ENEMY_PICKUP_KEY:
                return TileModel(
                    TileData(
                        (
                            TileType.PLAYER_KEY
                            if move is SpecialMove.PLAYER_PICKUP_KEY
                            else TileType.ENEMY_KEY
                        ),
                        from_tile_model.tile_data.tile_direction,
                    ),
                    from_tile_model.processor,
                )

    def attack_tile(self, x: int, y: int) -> None:
        try:
            tile_model = self.tile_model_matrix.get(x, y)
        except IndexError:
            return

        if tile_model.tile_data.tile_type is TileType.ENEMY:
            self.set_tile_model(x, y, TileModel(tile_model.floor_tile_data))

        events.TileDataChanged(x, y, TileData(TileType.ATTACK))
        self.scheduler.after(
            self.ATTACK_DURATION,
            lambda: events.TileDataChanged(
                x,
                y,
                self.tile_model_matrix.get(x, y).tile_data
            )
        )

    def check_win_state(self) -> bool:
        return all(self.tile_model_matrix.map(
            lambda tile_model: tile_model.tile_data.tile_type != TileType.FLAG
        ))

    def move_tile(self, x: int, y: int, direction: Direction) -> None:
        to_x = x + direction.x
        to_y = y + direction.y

        try:
            from_tile_model = self.tile_model_matrix.get(x, y)
            to_tile_model = self.tile_model_matrix.get(to_x, to_y)
        except (IndexError, AssertionError):
            return

        try:
            move = SpecialMove(MoveMixin(
                from_tile_model.tile_data.tile_type,
                to_tile_model.tile_data.tile_type
            ))

            logger.debug(
                "Executing special move %s from tile %s (%i, %i) in direction %s (%s)",
                move,
                from_tile_model.tile_data.tile_type,
                x,
                y,
                direction,
                to_tile_model.tile_data.tile_type,
            )

            new_tile_model = self.get_special_move_result(
                move,
                from_tile_model,
                to_tile_model
            )
        except ValueError:
            if not to_tile_model.tile_data.tile_type.is_walkable:
                return

            logger.debug(
                "Moving tile %s from (%i, %i) in direction %s (%s)",
                from_tile_model.tile_data.tile_type,
                x,
                y,
                direction,
                to_tile_model.tile_data.tile_type,
            )

            new_tile_model = TileModel(
                from_tile_model.tile_data,
                from_tile_model.processor,
                to_tile_model.tile_data,
            )

        self.set_tile_model(x, y, TileModel(from_tile_model.floor_tile_data))
        self.set_tile_model(to_x, to_y, new_tile_model)

    def restart(self) -> None:
        if len(self.history) == 0:
            return

        for x, y, tile_model in self.history[0].iter_xy():
            self.set_tile_model(x, y, deepcopy(tile_model))

        self.history.clear()

    def set_tile_model(
        self,
        x: int,
        y: int,
        tile_model: TileModel
    ) -> None:
        self.tile_model_matrix.set(x, y, tile_model)

        events.TileDataChanged(x, y, tile_model.tile_data)

    def step_back(self) -> None:
        if len(self.history) == 0:
            return

        for x, y, tile_model in self.history.pop().iter_xy():
            self.set_tile_model(x, y, deepcopy(tile_model))

    def step_forward(self) -> None:
        # TODO: Add events for base state and win state, to toggle editor and step buttons.
        # Early check looks redundant but is necessary
        # to avoid stepping when level is already complete.
        if self.check_win_state():
            events.LevelComplete(self.level, len(self.history))
            return

        self.history.append(deepcopy(self.tile_model_matrix))

        tile_data_matrix = self.tile_model_matrix.map(
            lambda tile_model: tile_model.tile_data
        )
        tile_actions = [
            (x, y, tile_model, action)
            for x, y, tile_model in self.tile_model_matrix.iter_xy()
            if (action := tile_model.get_action(x, y, tile_data_matrix)) is not None
        ]
        tile_actions.sort(
            key=lambda action_data: action_data[2].tile_data.tile_type.action_priority
        )

        for x, y, tile_model, action in tile_actions:
            if tile_model is not self.tile_model_matrix.get(x, y):
                continue
            self.handle_tile_action(x, y, action)

        if self.check_win_state():
            events.LevelComplete(self.level, len(self.history))

    def handle_tile_action(self, x: int, y: int, action: TileAction) -> None:
        tile_model = self.tile_model_matrix.get(x, y)
        tile_data = tile_model.tile_data

        match action:
            case TileAction.MOVE_FORWARD:
                self.move_tile(x, y, tile_data.tile_direction)

            case TileAction.MOVE_BACK:
                self.move_tile(x, y, -tile_data.tile_direction)

            case TileAction.TURN_LEFT:
                self.set_tile_model(x, y, TileModel(
                    TileData(tile_data.tile_type, tile_data.tile_direction.rotate()),
                    tile_model.processor,
                    tile_model.floor_tile_data,
                ))

            case TileAction.TURN_RIGHT:
                self.set_tile_model(x, y, TileModel(
                    TileData(tile_data.tile_type, tile_data.tile_direction.rotate(True)),
                    tile_model.processor,
                    tile_model.floor_tile_data,
                ))

            case TileAction.ATTACK:
                self.attack_tile(
                    x + tile_data.tile_direction.x,
                    y + tile_data.tile_direction.y,
                    )

            case _:
                logger.error("Unknown tile action %s", action)
