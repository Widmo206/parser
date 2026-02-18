"""Tile class for tile behavior and remote TileLabel control

Created on 2026.01.28
Contributors:
    Romcode
"""

from dataclasses import dataclass

from enums import TileActionType, TileType
from events import Event
from tile_action import TileAction


class Tile:
    def __init__(self, tile_type: TileType | str = TileType.EMPTY) -> None:
        self.tile_type = self._normalize_tile_type(tile_type)

        @dataclass(frozen=True, slots=True)
        self.TileTypeChanged = class TileTypeChanged(Event):
            tile_type: TileType

    def get_action(self) -> TileAction | None:
        if self.tile_type == TileType.PLAYER:
            # TODO: Implement action choice
            return TileAction(TileActionType.MOVE, Direction.UP)
        else:
            return None

    def set_tile_type(self, tile_type: TileType | str) -> None:
        self.tile_type = self._normalize_tile_type(tile_type)
        self.TileTypeChanged(self.tile_type)

    def _normalize_tile_type(self, tile_type: TileType | str) -> TileType:
        if isinstance(tile_type, str):
            try:
                return TileType(tile_type)
            except UnknownTileTypeError:
                logger.error(f"No tile type matching character '{tile_type}'")
                return TileType.EMPTY
        return tile_type