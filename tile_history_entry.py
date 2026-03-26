"""TileHistoryEntry class for keeping track of the tile action history

Created on 2026.03.26
Contributors:
    Romcode
"""

from dataclasses import dataclass

from enums import TileAction


@dataclass(frozen=True)
class TileHistoryEntry:
    x: int
    y: int
    action: TileAction
