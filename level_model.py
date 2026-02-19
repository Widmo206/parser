"""LevelModel class to handle level logic and interact with LevelController and LevelView

Created on 2026.02.18
Contributors:
    Romcode
"""

import logging
from pathlib import Path

from enums import Direction, TileActionType, TileType
import events
from level import Level
from tile_action import TileAction

logger = logging.getLogger(__name__)


class LevelModel:
    def __init__(self, path: Path) -> None:
        self.level = Level.from_path(path)

        if self.level.layout == "":
            self.width = 0
            self.height = 0
            self.tile_types = []
        else:
            rows = self.level.layout.splitlines()
            self.width = len(rows[0])
            self.height = len(rows)

            if any(len(row) != self.width for row in rows):
                raise ValueError(f"Mismatched row length in tilemap layout\n{self.level.layout}")

            self.tile_types = [TileType.normalize(character) for character in self.level.layout.replace("\n", "")]

        events.MoveRequested.connect(self._on_move_requested)

        events.LevelOpened(self.level)

    def cycle(self, direction: Direction) -> None:
        # TODO: Remove manual movement
        actions = []
        for y in range(self.height):
            for x in range(self.width):
                actions.append(self.get_tile_action(x, y))

        for y in range(self.height):
            for x in range(self.width):
                action = actions[y * self.width + x]
                if action is None:
                    continue
                match action.type:
                    case TileActionType.MOVE:
                        # action.direction
                        if direction is None:
                            continue
                        self.move_tile(x, y, direction)
                    case TileActionType.ATTACK:
                        pass
                    case _:
                        pass

    def destroy(self) -> None:
        events.MoveRequested.disconnect(self._on_move_requested)
        events.LevelClosed()

    def move_tile(self, x: int, y: int, direction: Direction) -> None:
        to_x = x + direction.x
        to_y = y + direction.y
        from_tile_type = self.get_tile_type(x, y)
        to_tile_type = self.get_tile_type(to_x, to_y)

        if (
            from_tile_type is None
            or to_tile_type is None
            or not to_tile_type.is_walkable
        ):
            return

        logger.debug(
            "Moving tile '%s' from (%i, %i) in direction '%s' ('%s')",
            from_tile_type.name,
            x,
            y,
            direction.name,
            to_tile_type.name,
        )
        self.set_tile_type(to_x, to_y, from_tile_type)
        self.set_tile_type(x, y, TileType.EMPTY)

    def get_tile_action(self, x: int, y: int) -> TileAction | None:
        if self.get_tile_type(x, y) == TileType.PLAYER:
            # TODO: Implement action choice
            return TileAction(TileActionType.MOVE, Direction.UP)
        else:
            return None

    def get_tile_type(self, x: int, y: int) -> TileType | None:
        try:
            assert 0 <= x < self.width
            assert 0 <= y < self.height
            return self.tile_types[y * self.width + x]
        except (AssertionError, IndexError):
            return None

    def set_tile_type(self, x: int, y: int, tile_type: TileType | str) -> None:
        tile_type = TileType.normalize(tile_type)
        self.tile_types[y * self.width + x] = tile_type
        events.TileTypeChanged(x, y, tile_type)

    def _on_move_requested(self, event: events.MoveRequested) -> None:
        self.cycle(event.direction)
