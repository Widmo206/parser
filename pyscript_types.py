"""Definitions for pyscript reference types.

Created on 2026.05.12
Contributors:
    Widmo
"""


from dataclasses import dataclass
from typing import Type, Any, Callable, TypeAlias


@dataclass(frozen=True)
class Constant(object):
    name: str
    type: Type
    _value: Any

    def __init__(self, name: str, type: Type, value: Any):
        assert isinstance(value, type)
        self.name   = name
        self.type   = type
        self._value = value

    def get(self) -> Any:
        return self._value


@dataclass
class Variable(object):
    name: str
    type: Type
    _value: Any

    def __init__(self, name: str, type: Type, initial_value: Any | None=None):
        assert initial_value is None or isinstance(initial_value, type)
        self.name   = name
        self.type   = type
        self._value = initial_value

    def get(self) -> Any:
        return self._value
    
    def set(self, value: Any) -> None:
        assert isinstance(self._value, self.type)
        self._value = value


@dataclass(frozen=True)
class ExternalFunction(object):
    name: str
    return_type: Type
    function: Callable

    def call(self, *args) -> Any:
        result = self.function(*args)
        assert isinstance(result, self.return_type)
        return result


AnyReference: TypeAlias = Constant | Variable | ExternalFunction
