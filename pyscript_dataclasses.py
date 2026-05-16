"""Data structures used by the PyScript parser

Created on 2026.02.21
Contributors:
    Widmo
"""


from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Collection
from enums import TokenType, NodeType, ClosureLabel, PPUInstruction
from pyscript_types import AnyReference, AnyFrozenRef
from errors import EndOfProgram


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
    instruction: PPUInstruction # creative name!
    parameter: Any
    source_line: int

    def __str__(self, _indent: int=0):
        if isinstance(self.parameter, Program): # just for passing the variable down
            return f"{self.instruction.name}: {self.parameter.__str__(_indent)}"
        else:
            return f"{self.instruction.name}: {self.parameter}"


@dataclass
class Program(object):
    instructions: list[Instruction]
    closure: Closure
    index: int=0

    def __str__(self, indent: int=1):
        e = indent
        return f"Program\n{e*"|"}Closure: {self.closure}\n{e*"|"}Instructions:\n{e*"|"}" + f"\n{e*"|"}".join([i.__str__(e+1) for i in self.instructions]) # absolute jank, but it works

    def next(self) -> tuple[Instruction, Closure]:
        """Grab the next instruction in the program, with the coresponding closure.
        
        If the instruction is a RUN, get the next instruction from it instead.
        Raises an EndOfProgram exception when it runs out of instructions.
        """
        while True:
            if self.index < len(self.instructions):
                instruction = self.instructions[self.index]
                closure = self.closure
            else:
                raise EndOfProgram
            match instruction.instruction:
                case PPUInstruction.EXEC:
                    try:
                        instruction, closure = instruction.parameter.next()
                    except EndOfProgram:
                        self.index += 1
                        continue # I wish Python had jumps
                case _:
                    self.index += 1
            break
        return instruction, closure
