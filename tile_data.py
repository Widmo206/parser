"""TileData class for managing tile data.

Created on 2026.02.25
Contributors:
    Romcode
"""

from dataclasses import dataclass

from enums import Direction, TileType


@dataclass(frozen=True)
class TileData:
    """Immutable container for tile type and direction."""
    tile_type: TileType = TileType.EMPTY
    tile_direction: Direction = Direction.RIGHT

    def __post_init__(self) -> None:
        object.__setattr__(self, "tile_type", TileType.normalize(self.tile_type))
        object.__setattr__(self, "tile_direction", Direction.normalize(self.tile_direction))

    def __str__(self) -> str:
        """Return a compact string representation of the tile."""
        return f"'{self.tile_type.character}{self.tile_direction.character}'"
