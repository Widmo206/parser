"""Data structures used by the PyScript parser

Created on 2026.02.21
Contributors:
    Widmo
"""


from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Collection
from enums import TokenType, NodeType
from pyscript_types import Constant, Variable, ExternalFunction, AnyReference


@dataclass(frozen=True)
class Token(object):
    type: TokenType
    value: Any
    line: int

    def __repr__(self):
        if self.value is None:
            return f"Token({self.type.name})"
        else:
            return f"Token({self.type.name}, {repr(self.value)})"
        

@dataclass
class ProcessNode(object):
    _parent: ProcessNode | None
    _type: NodeType
    _value: Any=None
    _children: tuple[ProcessNode, ...] | None=None

    def get_type(self) -> NodeType:
        """Return the type of this node."""
        return self._type
    
    def get_value(self) -> Any:
        """Return the data in the value of this node."""
        return self._value

    def get_parent(self) -> ProcessNode | None:
        """Return the parent node of this node."""
        return self._parent

    def has_children(self):
        """Check if this node has children."""
        return self._children is None

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
        return f"{self._type.name}: {self._value}"


@dataclass
class ProcessTree(object):
    _root: ProcessNode

    def __init__(self, external_references: Collection[Constant | ExternalFunction]):
        _global = Closure("Global", None)
        _global.add_many(external_references)
        self._root = ProcessNode(None, NodeType.CLOSURE, _global, None)

    @staticmethod
    def _visualize_branch(node: ProcessNode, indent_level: int=0) -> str:
        result = indent_level*"|" + node.format() + "\n"
        for child in node.get_children():
            result += ProcessTree._visualize_branch(child, indent_level+1)
        return result

    def visualize(self) -> str:
        """Generate a depth-first visualization of this ProcessTree.
        
        Example visualization:\n
        CLOSURE: None\n
        |\<NodeType>: \<value>\n
        ||<node child 1>\n
        ||<node child 2>\n
        |...
        """
        return self._visualize_branch(self._root)
    
    def __repr__(self):
        return self.visualize()

    def get_root(self):
        return self._root


@dataclass
class Closure(object):
    """Stores constants, variables, and functions."""
    label: str
    is_root: bool
    parent: Closure | None
    _references: dict[str, AnyReference]

    def __init__(self, label: str, parent: Closure | None=None):
        self.label = label
        if parent is None:
            self.is_root = True
        else:
            assert isinstance(parent, Closure)
            self.is_root = False
        self.parent = parent
        self._references = {}
    
    def __str__(self):
        return self.label

    def add(self, reference: AnyReference) -> None:
        assert reference.name not in self._references
        self._references[reference.name] = reference
    
    def add_many(self, references: Collection[AnyReference]) -> None:
        for ref in references:
            self.add(ref)
    
    def has(self, reference: str) -> bool:
        return reference in self._references
    
    def find(self, reference: str) -> AnyReference | None:
        if self.has(reference):
            return self._references[reference]
        elif self.is_root:
            return None
        else:
            return self.parent.find(reference)


@dataclass
class Instruction(object):
    function: Callable
    parameters: list
