"""TileModel class that holds tile data and can hold a pyscript processor.

Created on 2026.03.01
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass, field
import logging
from math import inf

from astar import astar
from enums import TileAction, TileType
from errors import InvalidSpecialMoveError
from matrix import Matrix
from processor import Processor
from processor import ProcessorLevelData
from tile_data import TileData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TileModel:
    """Immutable tile model with optional processor and floor state."""
    INPUT_ACTION_MAP = {
        "w": TileAction.MOVE_FORWARD,
        "s": TileAction.MOVE_BACK,
        "a": TileAction.TURN_LEFT,
        "d": TileAction.TURN_RIGHT,
        "x": TileAction.ATTACK,
        "":  None,
    }

    tile_data: TileData = field(default_factory=TileData)
    processor: Processor | None = None
    # Hm yes the floor here is made out of floor.
    floor_tile_data: TileData = field(default_factory=TileData)

    def get_action(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData]
    ) -> TileAction | None:
        """Compute this tile's next action based on its position and level state."""
        if self.processor is not None:
            return self.processor.advance(
                ProcessorLevelData(self_x, self_y, tile_data_matrix)
            )

            # Manual input action code
            # try:
            #     return self.INPUT_ACTION_MAP[askstring(
            #         "Player action",
            #         "Player action (wasdx): ",
            #     )]
            # except KeyError:
            #     events.RunPauseRequested()
            #     return None

        # If no pyscript processor, match behavior to tile type.
        match self.tile_data.tile_type:
            case TileType.ATTACK:
                return TileAction.DECAY

            case TileType.PLAYER | TileType.PLAYER_KEY:
                logger.warning(
                    "Player tile model at (%d, %d) has no processor",
                    self_x,
                    self_y,
                )
                return None

            case TileType.ENEMY | TileType.ENEMY_KEY:
                return self._get_astar_action(self_x, self_y, tile_data_matrix)

            case _:
                return None

    def get_special_move_result(self, to_tile_model: TileModel) -> TileModel:
        """Return the resulting TileModel for when this tile moves into the given TileModel."""
        to_tile_type = to_tile_model.tile_data.tile_type
        match self.tile_data.tile_type:
            case TileType.PLAYER:
                if to_tile_type is TileType.FLAG:
                    return TileModel(TileData(TileType.WIN))
                if to_tile_type is TileType.KEY:
                    return TileModel(
                        TileData(TileType.PLAYER_KEY, self.tile_data.tile_direction),
                        self.processor,
                    )

            case TileType.PLAYER_KEY:
                if to_tile_type is TileType.FLAG:
                    return TileModel(TileData(TileType.WIN))
                if to_tile_type is TileType.DOOR:
                    return TileModel(
                        TileData(TileType.PLAYER, self.tile_data.tile_direction),
                        self.processor,
                    )

            case TileType.ENEMY:
                if to_tile_type is TileType.PLAYER:
                    return self
                if to_tile_type is TileType.PLAYER_KEY:
                    return TileModel(
                        TileData(TileType.ENEMY_KEY, self.tile_data.tile_direction),
                        self.processor,
                    )
                if to_tile_type is TileType.KEY:
                    return TileModel(
                        TileData(TileType.ENEMY_KEY, self.tile_data.tile_direction),
                        self.processor,
                    )

            case TileType.ENEMY_KEY:
                if to_tile_type is TileType.PLAYER:
                    return self
                if to_tile_type is TileType.PLAYER_KEY:
                    return TileModel(
                        TileData(TileType.ENEMY_KEY, self.tile_data.tile_direction),
                        self.processor,
                        TileData(TileType.KEY),
                    )
                if to_tile_type is TileType.DOOR:
                    return TileModel(
                        TileData(TileType.ENEMY, self.tile_data.tile_direction),
                        self.processor,
                    )

        raise InvalidSpecialMoveError

    def _get_astar_action(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData]
    ) -> TileAction | None:
        # Get coordinates of all players.
        player_positions = tuple(
            (x, y)
            for x, y, tile_data
            in tile_data_matrix.iter_xy()
            if tile_data.tile_type is TileType.PLAYER
        )

        if len(player_positions) == 0:
            return None

        # Compute shortest path with A* pathfinding.
        # Allow non-walkable tiles that may move or change such as other enemies or doors.
        walkable_matrix = tile_data_matrix.map(
            lambda tile_data: tile_data.tile_type is not TileType.BLOCKED
        )
        sequences = (
            astar(
                self_x,
                self_y,
                self.tile_data.tile_direction,
                target_x,
                target_y,
                walkable_matrix,
            )
            for target_x, target_y
            in player_positions
        )
        shortest_sequence = min(
            sequences,
            key=lambda sequence: inf if sequence is None else len(sequence),
        )

        # Return appropriate tile action based on best path found.
        if shortest_sequence is None or len(shortest_sequence) == 0:
            return None

        first_direction = shortest_sequence[0]

        if first_direction is self.tile_data.tile_direction:
            return TileAction.MOVE_FORWARD

        if first_direction is self.tile_data.tile_direction.rotate(True):
            return TileAction.TURN_RIGHT

        return TileAction.TURN_LEFT
