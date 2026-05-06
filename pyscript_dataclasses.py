"""Data structures used by the PyScript parser

Created on 2026.02.21
Contributors:
    Widmo
"""

from dataclasses import dataclass
from typing import Any, Callable, Type
from enums import TokenType, NodeType


@dataclass(frozen=True)
class Token(object):
    type: TokenType
    value: Any

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

    def __init__(self):
        self._root = ProcessNode(None, NodeType.CLOSURE, None, None)


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
class Function(object):
    func: Callable
    arg_types: tuple

    def __init__(self, func: Callable, arg_types: tuple[Type]|Type|None=None):
        self.func = func
        if arg_types is None:
            self.arg_types = tuple()
        elif type(arg_types) == tuple:
            self.arg_types = arg_types
        else:
            self.arg_types = (arg_types,)

    def __call__(self, *args, **kwargs) -> Any:
        self.func(*args, **kwargs)

    @property
    def name(self) -> str:
        """Return the name of this function"""
        return self.func.__name__


# do we even need this?
@dataclass
class FunctionHolder(object):
    functions: dict[str, Function]

    def __init__(self):
        self.functions = {}

    def add(self, function: Function, name_override: str="") -> None:
        """Add a new function to this FunctionHolder.

        The function can be referenced by its name.
        """
        if name_override == "":
            self.functions[function.name] = function
        else:
            self.functions[name_override] = function

    def has(self, function_name: str) -> bool:
        """Check whether a given function is contained in this FunctionHolder."""
        return function_name in self.functions.keys()

    def get(self, function_name: str) -> Function:
        """Retrieve a function by its name."""
        return self.functions[function_name]

    def run(self, function_name: str, *args) -> Any:
        """Run a stored function.

        Return value is determined by the function itself.
        """
        func = self.get(function_name)
        return func(*args)


@dataclass
class Instruction(object):
    function: Callable
    parameters: list



