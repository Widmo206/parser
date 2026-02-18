"""LevelModel class to handle level logic and interact with LevelController and LevelView

Created on 2026.02.18
Contributors:
    Romcode
"""

import events
from level import Level


class LevelModel:
    def __init__(self, level: Level) -> None:
        self.level = level
        self.tiles = 

        events.MoveRequested.connect(self._on_move_requested)

    def cycle(self, direction: Direction) -> None:
        # TODO: Remove manual movement
        actions = []
        for y in range(self.height):
            for x in range(self.width):
                actions.append(self.get_tile(x, y).get_action())

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

    def _on_move_requested(self, event: events.MoveRequested) -> None:
        self.cycle(event.direction)
