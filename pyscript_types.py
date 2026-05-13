"""Definitions for pyscript reference types.

Created on 2026.05.12
Contributors:
    Widmo
"""


from dataclasses import dataclass
from typing import Type, Any, Callable, TypeAlias


def format_type(type: Type) -> str:
    """Turn a Type into a string.
    
    Fix for Any showing up as typing.Any in the logs
    """
    try:
        return type.__name__
    except AttributeError:
        return str(type)


@dataclass(frozen=True)
class Constant(object):
    name: str
    type: Type
    _value: Any

    def __post_init__(self):
        assert isinstance(self._value, self.type)

    def __repr__(self):
        if self._value is None:
            return f"const {self.name}: {format_type(self.type)}"
        else:
            return f"const {self.name}: {format_type(self.type)} = {self._value}"

    def get(self) -> Any:
        return self._value


@dataclass
class Variable(object):
    name: str
    type: Type
    _value: Any

    def __post_init__(self):
        assert self._value is None or isinstance(self._value, self.type)

    def __repr__(self):
        if self._value is None:
            return f"var {self.name}: {format_type(self.type)}"
        else:
            return f"var {self.name}: {format_type(self.type)} = {self._value}"

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
    
    def __repr__(self):
        return f"func {self.name}() -> {format_type(self.return_type)}"

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

    def __repr__(self):
        return f"func {self.name}() -> {format_type(self.return_type)}"

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
