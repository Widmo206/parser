"""Data structures used by the PyScript parser

Created on 2026.02.21
Contributors:
    Widmo
"""


from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Collection, Type, TypeAlias
from enums import TokenType, NodeType, ClosureLabel, PPUInstruction
from errors import EndOfProgram


FunctionArg: TypeAlias = tuple[str, Type]


def is_of_type(value: Any, type: Type) -> bool:
    if type == Any:
        return True
    elif value is None:
        return True
    else:
        return isinstance(value, type)


def format_type(type: Type) -> str:
    """Turn a Type into a string.
    
    Fix for Any showing up as typing.Any in the logs
    """
    try:
        return type.__name__
    except AttributeError:
        return str(type)


@dataclass(frozen=True)
class DataType(object):
    name: str
    type: Type

    def __post_init__(self):
        assert isinstance(self.type, Type)

    def __repr__(self):
        return f"type {format_type(self.type)}"

    def __str__(self):
        return format_type(self.type)


@dataclass(frozen=True)
class Constant(object):
    name: str
    type: Type
    _value: Any

    def __post_init__(self):
        assert is_of_type(self._value, self.type)

    def __repr__(self):
        if self._value is None:
            return f"const {self.name}: {format_type(self.type)}"
        else:
            return f"const {self.name}: {format_type(self.type)} = {self._value}"

    def get(self) -> Any:
        """Return the stored value."""
        return self._value


@dataclass
class Variable(object):
    name: str
    type: Type
    _value: Any

    def __post_init__(self):
        assert is_of_type(self._value, self.type)

    def __repr__(self):
        if self._value is None:
            return f"var {self.name}: {format_type(self.type)}"
        else:
            return f"var {self.name}: {format_type(self.type)} = {self._value}"

    def get(self) -> Any:
        """Return the stored value."""
        return self._value
    
    def set(self, value: Any) -> None:
        """Set the stored value to the specified one.
        
        The type of the new value must match self.type.
        """
        assert is_of_type(self._value, self.type)
        self._value = value


@dataclass(frozen=True)
class ExternalFunction(object):
    name: str
    return_type: Type
    function: Callable
    pauses_execution: bool
    # args: tuple[FunctionArg, ...] # TODO: implement checks
    
    def __repr__(self):
        if self.return_type == type(None):
            return f"func {self.name}()"
        else:
            return f"func {self.name}() -> {format_type(self.return_type)}"

    def call(self, *args) -> Any:
        """Calls the function with specified arguments."""
        result = self.function(*args)
        assert isinstance(result, self.return_type)
        return result


@dataclass()
class Function(object):
    """WIP don't use"""
    name: str
    return_type: Type
    program: Program
    args: tuple[FunctionArg, ...]

    def __repr__(self):
        return f"func {self.name}() -> {format_type(self.return_type)}"
    
    def __str__(self):
        return repr(self)

    # def call(self, *args) -> Any:
    #     result = self.function(*args)
    #     assert isinstance(result, self.return_type)
    #     return result


AnyValue:     TypeAlias = Constant | Variable
AnyFunction:  TypeAlias = Function | ExternalFunction
AnyFrozenRef: TypeAlias = Constant | ExternalFunction | DataType
AnyReference: TypeAlias = AnyValue | AnyFunction | DataType


@dataclass(frozen=True)
class Token(object):
    type: TokenType
    value: Any
    line: int

    def __repr__(self):
        return f"Token(TokenType.{self.type.name}, {repr(self.value)}, {self.line})"

    def __str__(self):
        if self.value is None:
            return f"{self.type.name}"
        else:
            return f"{self.type.name} ({repr(self.value)})"
        

@dataclass
class ProcessNode(object):
    _parent: ProcessNode | None
    _type: NodeType
    _source_line: int
    _value: Any=None
    _children: tuple[ProcessNode, ...] | None=None

    def __repr__(self):
        return f"ProcessNode(..., NodeType.{self._type.name}, {self._source_line}, {self._value}, ...)"

    def get_type(self) -> NodeType:
        """Return the type of this node."""
        return self._type

    def get_line(self) -> int:
        """Return the line in the source code file that corresponds to this node."""
        return self._source_line
    
    def get_value(self) -> Any:
        """Return the data in the value of this node."""
        return self._value

    def get_parent(self) -> ProcessNode | None:
        """Return the parent node of this node."""
        return self._parent

    def has_children(self):
        """Check if this node has children."""
        return self._children is not None

    def get_children(self) -> tuple[ProcessNode, ...]:
        """List the children of this node."""
        if self._children is None:
            return tuple()
        else:
            return self._children

    def add_child(self, node: ProcessNode):
        """Add a child to this node."""
        if self._children is None:
            self._children = (node,)
        else:
            self._children += (node,)

    def format(self) -> str:
        """Create a pretty string for ProcessTree visualization."""
        if self._value is None:
            return f"{self._type.name}"
        else:
            return f"{self._type.name} ({repr(self._value)})"


@dataclass
class ProcessTree(object):
    _root: ProcessNode

    def __init__(self, external_references: Collection[AnyFrozenRef]):
        _global = Closure(ClosureLabel.GLOBAL, None)
        _global.add_many(external_references)
        self._root = ProcessNode(None, NodeType.CLOSURE, 0, _global, None)

    @staticmethod
    def _visualize_branch(node: ProcessNode, indent_level: int=0) -> str:
        result = indent_level*"|" + node.format() + "\n"
        for child in node.get_children():
            result += ProcessTree._visualize_branch(child, indent_level+1)
        return result

    def visualize(self) -> str:
        """Generate a depth-first visualization of this ProcessTree.
        
        Example visualization:\n
        CLOSURE (Global)\n
        |CALL (func foo -> str)\n
        ||EXPRESSION\n
        |||READ (var bar: int)\n
        ||EXPRESSION\n
        |||LITERAL (42)\n
        |...
        """
        return self._visualize_branch(self._root)
    
    def __repr__(self):
        return self.visualize()

    def get_root(self):
        """Return the root note of the tree."""
        return self._root


@dataclass
class Closure(object):
    """Stores constants, variables, and functions."""
    label: ClosureLabel
    is_root: bool
    _parent: Closure | None
    _references: dict[str, AnyReference]

    def __init__(self, label: ClosureLabel, parent: Closure | None=None):
        self.label = label
        if parent is None:
            self.is_root = True
        else:
            assert isinstance(parent, Closure)
            self.is_root = False
        self._parent = parent
        self._references = {}
    
    def __repr__(self):
        return self.label.name

    def add(self, reference: AnyReference) -> None:
        """Add a reference to this Closure."""
        assert reference.name not in self._references
        self._references[reference.name] = reference
    
    def add_many(self, references: Collection[AnyReference]) -> None:
        """Add several references at once."""
        for ref in references:
            self.add(ref)
    
    def has(self, reference: str) -> bool:
        """Check whether this Closure contains a given reference."""
        return reference in self._references
    
    def find(self, reference: str) -> AnyReference | None:
        """Recursively search for a specific reference.
        
        If this Closure doesn't contain it, search the parent.
        If no Closure has it, return None.
        """
        if self.has(reference):
            return self._references[reference]
        elif self.is_root:
            return None
        else:
            return self._parent.find(reference) # Shutup pylance, if self._parent is None, this line will never run
        
    def get_parent(self) -> Closure | None:
        """Return the next closure above this one."""
        return self._parent
    
    def list(self) -> tuple[AnyReference, ...]:
        """Create a tuple of all references stored in this closure."""
        return tuple(self._references.values())
    
    def list_all(self) -> tuple[tuple[AnyReference, ...], ...]:
        """Recursively list all references in this and enclosing Closures.
        
        This closure has index 0 in the outermost tuple, it's parent is 1, etc.
        """
        if self.is_root:
            return self.list(),
        else:
            return self.list(), *self.get_parent().list_all() # same as above


@dataclass(frozen=True)
class Instruction(object):
    instruction: PPUInstruction # Naming things is hard
    parameter: Any
    source_line: int

    def __str__(self, _indent: int=0):
        if isinstance(self.parameter, Program | SubprogramProvider): # just for passing the variable down
            return f"{self.instruction.name}: {self.parameter.__str__(_indent)}"
        else:
            return f"{self.instruction.name}: {self.parameter}"


@dataclass
class Program(object):
    instructions: list[Instruction]
    closure_type: ClosureLabel
    initial_references: list[AnyFrozenRef] | None = None
    current_subprogram: Program | None = None
    index: int=0

    def __str__(self, indent: int=1):
        e = indent
        instructions = ""
        for i in self.instructions:
            if i.instruction == PPUInstruction.EXEC:
                instructions += "\n" + e * "|" + i.__str__(e+1)
            else:
                instructions += "\n" + e * "|" + str(i)

        return f"Subprogram\n{e*'|'}Closure Type: {self.closure_type}\n{e*'|'}Initial References: {self.initial_references}\n{e*'|'}Instructions:" + instructions

    def next(self) -> Instruction:
        """Grab the next instruction in the program, with the coresponding closure.
        
        If the instruction is a RUN, get the next instruction from it instead.
        Raises an EndOfProgram exception when it runs out of instructions.
        """
        while True:
            if self.index < len(self.instructions):
                instruction = self.instructions[self.index]
            else:
                raise EndOfProgram
            match instruction.instruction:
                case PPUInstruction.EXEC:
                    subprogram_provider = instruction.parameter
                    if self.current_subprogram is None:
                        self.current_subprogram = subprogram_provider.new()
                        break
                    else:
                        try:
                            instruction = self.current_subprogram.next()
                        except EndOfProgram:
                            self.index += 1
                            continue # I wish Python had jumps
                case _:
                    self.index += 1
            break
        return instruction


@dataclass
class SubprogramProvider(object):
    program: list[Instruction]
    closure_type: ClosureLabel
    initial_references: list[AnyFrozenRef] | None = None
    
    def __post_init__(self):
        if self.initial_references is None:
            self.initial_references = []
    
    def __str__(self, indent: int=1):
        e = indent
        instructions = ""
        for i in self.program:
            if i.instruction == PPUInstruction.EXEC:
                instructions += "\n" + e * "|" + i.__str__(e+1)
            else:
                instructions += "\n" + e * "|" + str(i)

        return f"Subprogram\n{e*'|'}Closure Type: {self.closure_type}\n{e*'|'}Initial References: {self.initial_references}\n{e*'|'}Instructions:" + instructions

    def new(self):
        return Program(self.program, self.closure_type, self.initial_references)


if __name__ == "__main__":
    foo = Constant("foo", int, 42)
    bar = Variable("bar", float, 9e9)
    pip = ExternalFunction("pip", str, lambda n: n*".", False)

    assert foo.get() == 42
    assert bar.get() == 9e9
    assert pip.call(5) == "....."
    bar.set(3.14)
    assert bar.get() < 5
    try:
        bar.set("poof")
        assert False
    except:
        pass

    print("Tests passed")
