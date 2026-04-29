"""TileModel class that holds tile data and can hold a pyscript processor

Created on 2026.03.01
Contributors:
    Romcode
"""

from dataclasses import dataclass, field

import logging
from math import inf
from tkinter.simpledialog import askstring

import events
from astar import astar
from enums import Direction, TileAction, TileType
from matrix import Matrix
from parser import Processor
from tile_data import TileData

logger = logging.getLogger(__name__)


@dataclass
class TileModel:
    INPUT_ACTION_MAP = {
        "w": TileAction.MOVE_FORWARD,
        "s": TileAction.MOVE_BACK,
        "a": TileAction.TURN_LEFT,
        "d": TileAction.TURN_RIGHT,
        "x": TileAction.ATTACK,
    }

    tile_data: TileData = field(default_factory=TileData)
    processor: Processor | None = None
    floor_tile_data: TileData = field(default_factory=TileData) # Hm yes the floor here is made out of floor


    def __post_init__(self) -> None:
        if self.processor is None and self.tile_data.tile_type is TileType.PLAYER:
            self.processor = Processor([])

    def get_action(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData]
    ) -> TileAction | None:
        if self.processor is not None:
            # return self.processor.advance(self_x, self_y, tile_data_matrix)
            # TODO: Remove manual actions once processor is implemented.
            try:
                return self.INPUT_ACTION_MAP[askstring(
                    "Player action",
                    "Player action (wasdx): ",
                )]
            except KeyError:
                events.RunButtonPressed()
                return None

        # If no pyscript processor, match behavior to tile type.
        match self.tile_data.tile_type:
            case TileType.PLAYER:
                logger.error("Player tile model at (%d, %d) has no processor")
                return None

            case TileType.ENEMY:
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
                walkable_matrix = tile_data_matrix.map(
                    lambda tile_data: tile_data.tile_type.is_walkable
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

                if shortest_sequence is None or len(shortest_sequence) == 0:
                    return None

                first_direction = shortest_sequence[0]

                if first_direction is self.tile_data.tile_direction:
                    return TileAction.MOVE_FORWARD

                if first_direction is self.tile_data.tile_direction.rotate(True):
                    return TileAction.TURN_RIGHT

                return TileAction.TURN_LEFT

            case _:
                return None

    def config(
        self,
        tile_type: TileType | str | None = None,
        tile_direction: Direction | str | None = None,
    ) -> None:
        self.tile_data = TileData(
            self.tile_data.tile_type if tile_type is None else tile_type,
            self.tile_data.tile_direction if tile_direction is None else tile_direction,
        )
