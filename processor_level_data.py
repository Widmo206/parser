"""ProcessorLevelData class that holds current level info for a processor.

Created on 2026.05.16
Contributors:
    Romcode
"""

from dataclasses import dataclass

from matrix import Matrix
from tile_data import TileData


@dataclass(frozen=True)
class ProcessorLevelData:
    x: int
    y: int
    tile_data_matrix: Matrix[TileData]
