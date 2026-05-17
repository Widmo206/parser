"""Processor - this is what executes the PyScript code

Created on 2026.05.15
Contributors:
    Widmo
    Romcode
"""


import logging
from typing import Generator, Any, TypeAlias

from enums import TileAction, TileType, PPUInstruction, Operator
from errors import EndOfProgram, PyScriptRuntimeError
import events
from processor_level_data import ProcessorLevelData
from pyscript_dataclasses import (
    AnyFunction,
    Closure,
    Constant,
    ExternalFunction,
    Function,
    Instruction,
    Program,
    SubprogramProvider,
    Variable,
)

logger = logging.getLogger(__name__)

ACTIONS = (
    TileAction.MOVE_FORWARD,
    TileAction.MOVE_BACK,
    TileAction.TURN_LEFT,
    TileAction.TURN_RIGHT,
    TileAction.ATTACK,
)
OPERATIONS = {
    Operator.NEGATIVE:  lambda b: -b,
    Operator.EQUALS:    lambda a, b: a == b,
    Operator.NOTEQUALS: lambda a, b: a != b,
    Operator.LESS_EQ:   lambda a, b: a <= b,
    Operator.MORE_EQ:   lambda a, b: a >= b,
    Operator.LESS_THAN: lambda a, b: a < b,
    Operator.MORE_THAN: lambda a, b: a > b,
    Operator.POW:       lambda a, b: a ** b,
    Operator.FLOOR_DIV: lambda a, b: a // b,
    Operator.ADD:       lambda a, b: a + b,
    Operator.SUB:       lambda a, b: a - b,
    Operator.MULT:      lambda a, b: a * b,
    Operator.DIV:       lambda a, b: a / b,
    Operator.MOD:       lambda a, b: a % b,
}

ActionGenerator = Generator[TileAction | None, ProcessorLevelData, None]
NoneType = type(None)


class Processor(object):
    processor_id: int
    value_stack: list
    program: Program | None
    action_generator: ActionGenerator | None
    level_data: ProcessorLevelData | None
    next_action: TileAction | None

    def __init__(self, processor_id: int = 0, program: Program = None) -> None:
        self.processor_id = processor_id
        self.program = program
        self.value_stack = []

    def advance(self, level_data: ProcessorLevelData) -> TileAction | None:
        assert self.action_generator is not None
        return self.action_generator.send(level_data)

    def generate_action_functions(self) -> list[ExternalFunction]:
        """Generate a list of functions corresponding to TileActions.

        N.B.: the functions are specific to a given Processor instance and
        should be inputted as external_references when setting up the Parser.
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
        
        Remember to use generate_action_functions and load them in the Parser,
        if you want to use them.
        """
        self.program = program
        self.action_generator = self.make_action_generator()
        # Initialize the generator as you can't send values to just-started
        # generators.
        next(self.action_generator)

    def push(self, value: Any):
        """Push a value onto the stack."""
        self.value_stack.append(value)
    
    def pull(self) -> Any:
        """Pull a value from the stack."""
        return self.value_stack.pop(-1)

    def make_action_generator(self) -> ActionGenerator:
        """Run the Processor until it runs into a function that makes it pass the turn, then yield a chosen TileAction.
        
        If the program terminates, the Processor will continue to yield None
        """
        # Keeping possibility for multiple player tiles,
        # that should all succeed with the same code to force versatility.
        # One processor per player tile, to keep variables separate.
        assert self.program is not None
        global_closure = Closure(self.program.closure_type, None)
        global_closure.add_many(self.program.initial_references)
        current_closure = global_closure
        function_call_args = []

        self.level_data = yield
        self._log_advance()

        while True:
            try:
                instruction = self.program.next()
                logger.debug(instruction)
            except EndOfProgram:
                break

            self.next_action = None

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
                    function: AnyFunction = current_closure.find(instruction.parameter[0].name)
                    no_args: int = instruction.parameter[1]
                    args = []
                    # TODO: check that the function actually accepts that number of args + check type
                    for i in range(no_args):
                        args.append(self.pull())
                    args.reverse() # args are back-to-front on the stack

                    if isinstance(function, ExternalFunction):
                        self.push(function.call(*args))
                        if function.pauses_execution:
                            self.level_data = yield self.next_action
                            self._log_advance()
                    else:
                        function_call_args = []
                        assert len(args) == len(function.args)
                        for arg, value in zip(function.args, args):
                            function_call_args.append(Variable(arg[0], arg[1], value))

                case PPUInstruction.EVAL:
                    operator: Operator = instruction.parameter
                    b = self.pull()
                    # TODO: check operand type
                    if operator.is_unary:
                        result = OPERATIONS[operator](b)
                    else:
                        a = self.pull()
                        result = OPERATIONS[operator](a, b)
                    self.push(result)

                case PPUInstruction.DEFC:
                    current_closure.add(Constant(instruction.parameter.name, instruction.parameter.type, self.pull()))

                case PPUInstruction.DEFV:
                    current_closure.add(Variable(instruction.parameter.name, instruction.parameter.type, self.pull()))

                case PPUInstruction.DEFF:
                    current_closure.add(instruction.parameter) # Function doesn't have anything that's supposed to be modified, so this should be fine

                case PPUInstruction.EXEC:
                    subprogram: SubprogramProvider = instruction.parameter
                    current_closure.value_stack_length = len(self.value_stack)
                    current_closure = Closure(subprogram.closure_type, current_closure)
                    current_closure.add_many(function_call_args)
                    function_call_args = []

                case PPUInstruction.EXIT:
                    has_return_value = instruction.parameter
                    if has_return_value:
                        return_value = self.pull()
                    else:
                        return_value = None
                    previous_closure = current_closure
                    current_closure = current_closure.get_parent()
                    if len(self.value_stack) < current_closure.value_stack_length:
                        raise PyScriptRuntimeError(f"Missing values on value_stack after exiting closure {previous_closure.label}")
                    trimmed_values = 0
                    while len(self.value_stack) > current_closure.value_stack_length:
                        trimmed_values += 1
                        self.pull()
                    if trimmed_values > 0:
                        logger.debug(f"Trimmed {trimmed_values} values from value_stack")
                    if return_value is not None:
                        self.push(return_value)

                case _:
                    raise NotImplementedError(f"Unimplemented instruction: {instruction.instruction.name}")

        while True:
            yield None

    def _log_advance(self) -> None:
        if self.level_data is None:
            return

        logger.debug(
            "Advancing processor %d for tile %s at (%d, %d)",
            self.processor_id,
            self.level_data.tile_data_matrix.get(
                self.level_data.x,
                self.level_data.y
            ).tile_type,
            self.level_data.x,
            self.level_data.y,
        )

    def _check_forward(self) -> str:
        if self.level_data is None:
            return "Missing level data"

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
