"""Processor - this is what executes the PyScript code

Created on 2026.05.15
Contributors:
    Widmo
    Romcode
"""


import logging
from typing import Generator, Any, TypeAlias
from enums import TileAction
from tile_data import TileData
from matrix import Matrix
from pyscript_types import ExternalFunction
from pyscript_dataclasses import Instruction, Program
from dataclasses import dataclass
from errors import EndOfProgram


logger = logging.getLogger(__name__)
ACTIONS = (
    TileAction.MOVE_FORWARD,
    TileAction.MOVE_BACK,
    TileAction.TURN_LEFT,
    TileAction.TURN_RIGHT,
    TileAction.ATTACK,
)
NoneType = type(None)


class Processor(object):
    program: Program | None
    call_stack: list
    value_stack: list
    next_action: TileAction | None

    def __init__(self, program: Program=None):
        self.program = program
        self.stack = []
    
    def load(self, program: Program):
        """Load a compiled program into the processor.
        
        Remember to use generate_action_functions and load them in the Parser, if you want to use them.
        """
        self.program = program

    def advance(
        self,
        self_x: int,
        self_y: int,
        tile_data_matrix: Matrix[TileData],
    ) -> Generator[TileAction | None, None, None]:
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        assert self.program is not None
        logger.debug(
            "Advancing processor for tile %s at (%s, %s)",
            tile_data_matrix.get(self_x, self_y).tile_type,
            self_x,
            self_y,
        )
        while True:
            self.next_action = None
            try:
                instruction = self.program.next()
            except EndOfProgram:
                break

            ... # do stuff
            logger.debug(instruction)
            # yield self.next_action

        while True:
            yield None

    def _set_next_action(self, action: TileAction | None) -> None:
        self.next_action = action

    def generate_action_functions(self) -> list[ExternalFunction]:
        result = [
            # None is the default choice, so having it set to None may be unnecessary
            ExternalFunction("wait", NoneType, lambda: self._set_next_action(None), True)
        ]
        for action in ACTIONS:
            result.append(ExternalFunction(action.name.lower(), NoneType, lambda: self._set_next_action(action), True))
        return result
