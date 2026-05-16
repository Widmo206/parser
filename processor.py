"""Processor - this is what executes the PyScript code

Created on 2026.05.15
Contributors:
    Widmo
    Romcode
"""


import logging
from typing import Generator, Any, TypeAlias
from enums import TileAction, PPUInstruction, Operator
from tile_data import TileData
from matrix import Matrix
from pyscript_types import ExternalFunction, Constant, Variable, Function
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
    value_stack: list
    next_action: TileAction | None

    def __init__(self, program: Program=None):
        self.program = program
        self.value_stack = []
    
    def load(self, program: Program):
        """Load a compiled program into the processor.
        
        Remember to use generate_action_functions and load them in the Parser, if you want to use them.
        """
        self.program = program
    
    def push(self, value: Any):
        """Push a value onto the stack."""
        self.value_stack.append(value)
    
    def pull(self) -> Any:
        """Pull a value from the stack."""
        return self.value_stack.pop(-1)

    def advance(
        self,
        self_x: int,
        self_y: int,
        #tile_data_matrix: Matrix[TileData],
    ) -> Generator[TileAction | None, None, None]:
        """Run the Processor until it runs into a function that makes it pass the turn, then yield a chosen TileAction.
        
        If the program terminates, the Processor will continue to yield None
        """
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        assert self.program is not None
        logger.debug(
            "Advancing processor for tile %s at (%s, %s)",
            None, #tile_data_matrix.get(self_x, self_y).tile_type,
            self_x,
            self_y,
        )
        while True:
            self.next_action = None
            try:
                instruction, current_closure = self.program.next()
                logger.debug(instruction)
            except EndOfProgram:
                break

            match instruction.instruction: # I sure love match/case, don't I?
                case PPUInstruction.PUSH:
                    self.push(instruction.parameter)
                case PPUInstruction.PULL:
                    raise NotImplementedError # I don't think it's needed, actually
                case PPUInstruction.READ:
                    self.push(current_closure.find(instruction.parameter.name).get())
                case PPUInstruction.WRIT:
                    # TODO: check type of value before assignment
                    current_closure.find(instruction.parameter.name).set(self.pull())
                case PPUInstruction.CALL:
                    function: ExternalFunction = current_closure.find(instruction.parameter[0].name)
                    no_args: int = instruction.parameter[1]
                    args = []
                    # TODO: check that the function actually accepts that number of args + check type
                    for i in range(no_args):
                        args.append(self.pull())
                    self.push(function.call(*args))
                    if function.pauses_execution:
                        yield self.next_action
                case PPUInstruction.EVAL:
                    operator: Operator = instruction.parameter
                    b = self.pull()
                    # TODO: check operand type
                    if operator.is_unary:
                        match operator:
                            case Operator.NEGATIVE:
                                result = -b
                            case _:
                                raise NotImplementedError
                    else: 
                        a = self.pull()
                        match operator: # There's got to be a better way to do this
                            case Operator.EQUALS:
                                result = a == b
                            case Operator.NOTEQUALS:
                                result = a != b
                            case Operator.LESS_EQ:
                                result = a <= b
                            case Operator.MORE_EQ:
                                result = a >= b
                            case Operator.LESS_THAN:
                                result = a < b
                            case Operator.MORE_THAN:
                                result = a > b
                            case Operator.POW:
                                result = a ** b
                            case Operator.FLOOR_DIV:
                                result = a // b
                            case Operator.ADD:
                                result = a + b
                            case Operator.SUB:
                                result = a - b
                            case Operator.MULT:
                                result = a * b
                            case Operator.DIV:
                                result = a / b
                            case Operator.MOD:
                                result = a % b
                            case _:
                                raise NotImplementedError
                    self.push(result)
                case PPUInstruction.DEFC:
                    current_closure.add(Constant(instruction.parameter.name, instruction.parameter.type, self.pull()))
                case PPUInstruction.DEFV:
                    current_closure.add(Variable(instruction.parameter.name, instruction.parameter.type, self.pull()))
                case PPUInstruction.DEFF:
                    raise NotImplementedError
                case _:
                    raise NotImplementedError

        while True:
            yield None

    def _set_next_action(self, action: TileAction | None) -> None:
        self.next_action = action

    def generate_action_functions(self) -> list[ExternalFunction]:
        """Generate a list of functions corresponding to TileActions.
        
        N.B.: the functions are specific to a given Processor instance and should be inputted as external_references when setting up the Parser.
        """
        result = [
            # None is the default choice, so having it set to None may be unnecessary
            ExternalFunction("wait", NoneType, lambda: self._set_next_action(None), True)
        ]
        for action in ACTIONS:
            result.append(ExternalFunction(action.name.lower(), NoneType, lambda: self._set_next_action(action), True))
        return result
