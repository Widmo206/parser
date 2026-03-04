"""Implementation of the A* algorithm for enemy pathfinding

Created on 2026.03.04
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from math import copysign

from enums import Direction
from matrix import Matrix


@dataclass(frozen=True)
class Node:
    x: int
    y: int
    direction: Direction
    cost: int = 0
    parent: Node | None = None

    def get_future_cost(self, target_x: int, target_y: int) -> int:
        """Calculate minimum amount of actions needed to reach target"""
        dx, dy = target_x - self.x, target_y - self.y
        sign_dx, sign_dy = copysign(1, dx), copysign(1, dy)

        move_cost = abs(dx) + abs(dy)
        turn_cost = min(abs(self.direction.x - sign_dx) + abs(self.direction.y - sign_dy), 2)

        return move_cost + turn_cost

    def get_total_cost(self, target_x: int, target_y: int) -> int:
        return self.cost + self.get_future_cost(target_x, target_y)


def astar(
    self_x: int,
    self_y: int,
    self_direction: Direction,
    target_x: int,
    target_y: int,
    walkable_matrix: Matrix[bool],
) -> tuple[Direction, ...]:
    """Return the shortest path from self to target using A* algorithm."""
    if self_x == target_x and self_y == target_y:
        return ()

    open_nodes = [Node(self_x, self_y, self_direction)]
    closed_nodes = []

    while len(open_nodes) > 0:
        current_node = min(
            open_nodes,
            key=lambda node: node.get_total_cost(target_x, target_y),
        )

        if current_node.x == target_x and current_node.y == target_y:
            return ("yay")

        open_nodes.remove(current_node)
        closed_nodes.append(current_node)

        for direction in Direction:
