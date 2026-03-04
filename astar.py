"""Custom implementation of the A* algorithm for enemy pathfinding

Created on 2026.03.04
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from math import copysign, inf

from enums import Direction
from matrix import Matrix


@dataclass(frozen=True)
class Node:
    direction: Direction
    cost: int = 0
    parent: Node | None = None

    def get_future_cost(self, dx: int, dy: int) -> int:
        """Estimate the minimum amount of actions needed to reach target"""
        sign_dx, sign_dy = copysign(1, dx), copysign(1, dy)

        move_cost = abs(dx) + abs(dy)
        turn_cost = min(abs(self.direction.x - sign_dx) + abs(self.direction.y - sign_dy), 2)

        return move_cost + turn_cost

    def get_total_cost(self, dx: int, dy: int) -> int:
        return self.cost + self.get_future_cost(dx, dy)

    def get_sequence(self) -> tuple[Direction, ...]:
        if self.parent is None:
            return ()

        return *self.parent.get_sequence(), self.direction


def astar(
    self_x: int,
    self_y: int,
    self_direction: Direction,
    target_x: int,
    target_y: int,
    walkable_matrix: Matrix[bool],
) -> tuple[Direction, ...] | None:
    """Return the shortest path from self to target using A* algorithm"""
    if self_x == target_x and self_y == target_y:
        return ()

    open_node_matrix: Matrix[Node | None] = walkable_matrix.map(lambda _: None)
    closed_node_matrix: Matrix[Node | None] = walkable_matrix.map(lambda _: None)

    open_node_matrix.set(self_x, self_y, Node(self_direction))

    while any(open_node_matrix):
        # Choose most promising node.
        current_x, current_y, current_node = min(
            open_node_matrix.iter_xy(),
            key=lambda x, y, node: inf if node is None else node.get_total_cost(
                target_x - x,
                target_y - y,
            ),
        )

        if current_x == target_x and current_y == target_y:
            return current_node.get_sequence()

        # Mark current node as explored.
        open_node_matrix.set(current_x, current_y, None)
        closed_node_matrix.set(current_x, current_y, current_node)

        # Spread to neighboring nodes.
        for direction in Direction:
            neighbor_x, neighbor_y = current_x + direction.x, current_y + direction.y
            if (
                walkable_matrix.get(neighbor_x, neighbor_y)
                and closed_node_matrix.get(neighbor_x, neighbor_y) is not None
            ):
                continue

            stored_neighbor_node = open_node_matrix.get(neighbor_x, neighbor_y)
            neighbor_cost = current_node.get_total_cost(direction.x, direction.y)

            # Don't override a better path to the same node.
            if (
                stored_neighbor_node is not None
                and stored_neighbor_node.cost < neighbor_cost
            ):
                continue

            # Add node to explore queue.
            open_node_matrix.set(
                neighbor_x,
                neighbor_y,
                Node(
                    direction,
                    neighbor_cost,
                    current_node,
                ),
            )

    # Nothing left to explore and no path found.
    return None
