"""LevelModel class to handle level logic and interact with LevelBottomBar and LevelView.

Created on 2026.02.18
Contributors:
    Romcode
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
import logging
from pathlib import Path

from enums import Direction, TileAction, TileType
from errors import InvalidSpecialMoveError
import events
from level import Level
from matrix import Matrix
from parser import Parser
from processor import Processor
from save import LevelScore
from tile_data import TileData
from tile_model import TileModel

logger = logging.getLogger(__name__)


@dataclass
class LevelModel:
    ATTACK_DURATION = 250

    level: Level
    tile_model_matrix: Matrix[TileModel]
    history: list[Matrix[TileData]] = field(default_factory=list)
    view_step: int = 0
    pyscript_path: Path | None = None
    token_count: int = 0

    @classmethod
    def from_path(cls, path: Path) -> LevelModel:
        level = Level.from_path(path)
        tile_data_matrix = level.get_tile_data_matrix()
        tile_model_matrix = tile_data_matrix.map(TileModel)
        history = [tile_data_matrix]

        return cls(level, tile_model_matrix, history)

    @property
    def model_step(self) -> int:
        return len(self.history) - 1

    def load_processors(self, pyscript_path: Path) -> None:
        """Create and assign a processor with program compiled from path for
        each player tile in the level.

        Also clears step history, so this should only be used when level is in
        base state.
        """
        if self.view_step != 0:
            logger.error("Cannot load processors when level is not in base state")
            return

        self.history = [self.history[0]]
        self.tile_model_matrix = self.history[0].map(TileModel)

        parser = None
        processor_id = 0
        # We parse code for each processor, which is wasteful but required
        # because of how external functions work.
        for x, y, tile_model in self.tile_model_matrix.iter_xy():
            if tile_model.tile_data.tile_type not in (TileType.PLAYER, TileType.PLAYER_KEY):
                continue

            processor = Processor(processor_id)
            external_references = processor.generate_action_functions()

            parser = Parser(pyscript_path, external_references)
            processor.load(parser.compile_from_file())

            new_tile_model = TileModel(
                tile_model.tile_data,
                processor,
                tile_model.floor_tile_data,
            )
            self.tile_model_matrix.set(x, y, new_tile_model)
            processor_id += 1

        assert parser is not None
        self.pyscript_path = pyscript_path
        self.token_count = parser.token_count

    def restart(self) -> None:
        if self.view_step == 0:
            return

        self._set_view_step(0)

    def step_back(self) -> None:
        if self.view_step == 0:
            return

        self._set_view_step(self.view_step - 1)

    def step_forward(self) -> None:
        if self.view_step == self.model_step:
            # Early check looks redundant but is necessary
            # to avoid stepping when level is already complete.
            if self._check_win_state():
                self._emit_level_complete()
                return

            self._model_step_forward()

        self._set_view_step(self.view_step + 1)

        if self._check_win_state() and self.view_step == self.model_step:
            self._emit_level_complete()

    def _check_win_state(self) -> bool:
        return all(self.tile_model_matrix.map(
            lambda tile_model: tile_model.tile_data.tile_type != TileType.FLAG
        ))

    def _emit_level_complete(self) -> None:
        level_score = LevelScore(self.pyscript_path, self.model_step, self.token_count)
        events.LevelComplete(self.level.name, level_score)

    def _handle_tile_action(self, x: int, y: int, action: TileAction) -> None:
        tile_model = self.tile_model_matrix.get(x, y)
        tile_data = tile_model.tile_data

        match action:
            case TileAction.MOVE_FORWARD:
                self._move_tile(x, y, tile_data.tile_direction)

            case TileAction.MOVE_BACK:
                self._move_tile(x, y, -tile_data.tile_direction)

            case TileAction.TURN_LEFT:
                self.tile_model_matrix.set(x, y, TileModel(
                    TileData(tile_data.tile_type, tile_data.tile_direction.rotate()),
                    tile_model.processor,
                    tile_model.floor_tile_data,
                ))

            case TileAction.TURN_RIGHT:
                self.tile_model_matrix.set(x, y, TileModel(
                    TileData(tile_data.tile_type, tile_data.tile_direction.rotate(True)),
                    tile_model.processor,
                    tile_model.floor_tile_data,
                ))

            case TileAction.ATTACK:
                self._attack_tile(
                    x + tile_data.tile_direction.x,
                    y + tile_data.tile_direction.y,
                )

            case TileAction.DECAY:
                self.tile_model_matrix.set(x, y, (
                    TileModel(TileData(TileType.KEY))
                    if tile_model.tile_data.tile_type in (TileType.PLAYER_KEY, TileType.ENEMY_KEY)
                    else TileModel(tile_model.floor_tile_data)
                ))

            case _:
                logger.error("Unknown tile action %s", action)

    def _model_step_forward(self) -> None:
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
            self._handle_tile_action(x, y, action)

        self.history.append(
            self.tile_model_matrix.map(
                lambda tile_model: deepcopy(tile_model.tile_data)
            )
        )

    def _move_tile(self, x: int, y: int, direction: Direction) -> None:
        to_x = x + direction.x
        to_y = y + direction.y

        try:
            from_tile_model = self.tile_model_matrix.get(x, y)
            to_tile_model = self.tile_model_matrix.get(to_x, to_y)
        except (IndexError, AssertionError):
            return

        # Attack tiles are temporary and should not count when moving into one.
        if to_tile_model.tile_data.tile_type is TileType.ATTACK:
            to_tile_model = TileModel(to_tile_model.floor_tile_data)

        try:
            new_tile_model = from_tile_model.get_special_move_result(to_tile_model)
        except InvalidSpecialMoveError:
            if not to_tile_model.tile_data.tile_type.is_walkable:
                return

            logger.debug(
                "Moving tile %s from (%d, %d) in direction %s (%s)",
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
        else:
            logger.debug(
                "Executing special move from tile %s (%d, %d) in direction %s (%s)",
                from_tile_model.tile_data.tile_type,
                x,
                y,
                direction,
                to_tile_model.tile_data.tile_type,
            )

        self.tile_model_matrix.set(x, y, TileModel(from_tile_model.floor_tile_data))
        self.tile_model_matrix.set(to_x, to_y, new_tile_model)

    def _attack_tile(self, x: int, y: int) -> None:
        try:
            tile_model = self.tile_model_matrix.get(x, y)
        except IndexError:
            return

        # Preserve what's on the floor
        if tile_model.tile_data.tile_type.is_walkable:
            self.tile_model_matrix.set(x, y, TileModel(
                TileData(TileType.ATTACK),
                floor_tile_data=tile_model.tile_data,
            ))
            return

        match tile_model.tile_data.tile_type:
            case TileType.ENEMY:
                self.tile_model_matrix.set(x, y, TileModel(
                    TileData(TileType.ATTACK),
                    floor_tile_data=tile_model.floor_tile_data,
                ))
            case TileType.ENEMY_KEY:
                self.tile_model_matrix.set(x, y, TileModel(
                    TileData(TileType.ATTACK),
                    floor_tile_data=TileData(TileType.KEY),
                ))

    def _set_view_step(self, step: int) -> None:
        if self.view_step < 0:
            logger.error(
                "View step (%d) cannot be negative",
                self.view_step,
            )
            self.view_step = self.model_step
        elif self.view_step > self.model_step:
            logger.error(
                "View step (%d) cannot be higher than model step (%d)",
                self.view_step,
                self.model_step,
            )
            self.view_step = self.model_step

        self.view_step = step
        for x, y, tile_data in self.history[step].iter_xy():
            events.TileDataChanged(x, y, tile_data)
