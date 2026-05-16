"""Processor - this is what executes the PyScript code

Created on 2026.05.15
Contributors:
    Widmo
    Romcode
"""


import logging
from typing import Generator, Any, TypeAlias

from dataclasses import dataclass

from enums import TileAction, TileType
from errors import EndOfProgram
import events
from matrix import Matrix
from pyscript_types import ExternalFunction
from pyscript_dataclasses import Instruction, Program
from tile_data import TileData

logger = logging.getLogger(__name__)
ACTIONS = (
    TileAction.MOVE_FORWARD,
    TileAction.MOVE_BACK,
    TileAction.TURN_LEFT,
    TileAction.TURN_RIGHT,
    TileAction.ATTACK,
)
NoneType = type(None)


@dataclass(frozen=True)
class ProcessorLevelData:
    x: int
    y: int
    tile_data_matrix: Matrix[TileData]


class Processor(object):
    processor_id: int
    program: Program | None
    call_stack: list
    value_stack: list
    level_data: ProcessorLevelData
    next_action: TileAction

    def __init__(self, processor_id: int = 0, program: Program = None) -> None:
        self.processor_id = processor_id
        self.program = program
        self.stack = []

    def generate_action_functions(self) -> list[ExternalFunction]:
        """Generate a list of functions corresponding to TileActions.

        N.B.: the functions are specific to a given Processor instance and should be inputted as external_references when setting up the Parser.
        """
        result = [
            ExternalFunction(
                "check_forward",
                str,
                self._check_forward,
                False,
            ),
            ExternalFunction(
                "print",
                NoneType,
                self._print,
                False,
            ),
            ExternalFunction(
                "wait",
                NoneType,
                lambda: self._set_next_action(None),
                True,
            ),
        ]
        for action in ACTIONS:
            result.append(
                ExternalFunction(
                    action.name.lower(),
                    NoneType,
                    lambda: self._set_next_action(action),
                    True,
                )
            )

        return result

    def load(self, program: Program) -> None:
        """Load a compiled program into the processor.
        
        Remember to use generate_action_functions and load them in the Parser, if you want to use them.
        """
        self.program = program

    def make_action_generator(self) -> Generator[
        TileAction | None,
        tuple[int, int, Matrix[TileData]],
        None,
    ]:
        """Run the Processor until it runs into a function that makes it pass the turn, then yield a chosen TileAction.
        
        If the program terminates, the Processor will continue to yield None
        """
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        assert self.program is not None

        level_data: ProcessorLevelData | None = yield
        while level_data is not None:
            try:
                instruction = self.program.next()
            except EndOfProgram:
                break

            logger.debug(
                "Advancing processor %i for tile %s (%s, %s)",
                self.processor_id,
                level_data.tile_data_matrix.get(level_data.x, level_data.y).tile_type,
                level_data.x,
                level_data.y,
            )

            self.level_data = level_data
            self.next_action = None

            ... # do stuff
            logger.debug(instruction)

            level_data: ProcessorLevelData | None = yield self.next_action

        while level_data is not None:
            yield None

    def _check_forward(self) -> str:
        self_tile_data = self.level_data.tile_data_matrix.get(
            self.level_data.x,
            self.level_data.y,
        )
        scan_x = self.level_data.x + self_tile_data.tile_direction.x
        scan_y = self.level_data.y + self_tile_data.tile_direction.y
        scan_tile_data = self.level_data.tile_data_matrix.get(scan_x, scan_y)
        return scan_tile_data.tile_type.name.lower()

    def _print(self, text: Any = "") -> None:
        events.PyscriptOutputRequested(self.processor_id, text)

    def _set_next_action(self, action: TileAction | None) -> None:
        self.next_action = action
