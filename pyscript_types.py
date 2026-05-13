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

    def __post_init__(self):
        assert isinstance(self._value, self.type)

    def get(self) -> Any:
        return self._value


@dataclass
class Variable(object):
    name: str
    type: Type
    _value: Any | None

    def __post_init__(self):
        assert self._value is None or isinstance(self._value, self.type)

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


@dataclass()
class Function(object):
    """WIP don't use"""
    name: str
    return_type: Type
    function: Callable

    def call(self, *args) -> Any:
        result = self.function(*args)
        assert isinstance(result, self.return_type)
        return result


AnyValue:     TypeAlias = Constant | Variable
AnyFunction:  TypeAlias = Function | ExternalFunction
AnyReference: TypeAlias = AnyValue | AnyFunction


if __name__ == "__main__":
    foo = Constant("foo", int, 42)
    bar = Variable("bar", float, 9e9)
    pip = ExternalFunction("pip", str, lambda n: n*".")

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
