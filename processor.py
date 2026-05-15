"""Processor - this is what executes the PyScript code

Created on 2026.05.15
Contributors:
    Romcode
    Widmo
"""


import logging
from typing import Generator, Any
from enums import TileAction
from tile_data import TileData
from matrix import Matrix
from pyscript_types import ExternalFunction
from dataclasses import dataclass


logger = logging.getLogger(__name__)
Actions = (
    TileAction.MOVE_FORWARD,
    TileAction.MOVE_BACK,
    TileAction.TURN_LEFT,
    TileAction.TURN_RIGHT,
    TileAction.ATTACK,
)
NoneType = type(None)


@dataclass(frozen=True)
class Instruction(object):
    instruction: str # creative name!
    parameter: Any


@dataclass
class Program(object):
    instructions: list[Instruction]
    index: int=0

    def next(self):
        instruction = self.instructions[self.index]
        self.index += 1
        return instruction


class Processor(object):
    program: Program
    stack: list
    next_action: TileAction | None

    def __init__(self, program: Program):
        self.program = program
        self.stack = []

    def advance(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData],
    ) -> Generator[TileAction | None]:
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        logger.debug(
            "Advancing processor for tile %s at (%s, %s)",
            tile_data_matrix.get(self_x, self_y).tile_type,
            self_x,
            self_y,
        )
        while True:
            yield None

        # TODO: Advance program based on level state, block at next player action and return it.
    
    def set_next_action(self, action: TileAction | None) -> None:
        self.next_action = action
    
    def generate_action_choices(self) -> list[ExternalFunction]:
        result = [
            ExternalFunction("wait", NoneType, lambda: self.set_next_action(None), True)
        ]
        for action in Actions:
            result.append(ExternalFunction(action.name.lower(), NoneType, lambda: self.set_next_action(action), True))
        return result
        
