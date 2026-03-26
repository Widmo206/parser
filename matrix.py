"""Matrix generic class that represents a grid of things

Created on 2026.02.27
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generic, Iterator, TypeVar

T = TypeVar('T')
U = TypeVar('U')


@dataclass(frozen=True)
class Matrix(Generic[T]):
    width: int
    height: int
    _elements: list[T]

    def __post_init__(self) -> None:
        if not isinstance(self._elements, list):
            object.__setattr__(self, "_elements", list(self._elements))

        if self.width <= 0 or self.height <= 0:
            raise ValueError("Matrix width and height must be positive")
        if len(self._elements) != self.width * self.height:
            raise ValueError("Matrix element count must match width and height")

    def __getitem__(self, index: int) -> T:
        return self._elements[index]

    def __setitem__(self, index: int, value: T) -> None:
        self._elements[index] = value

    def __iter__(self) -> Iterator[T]:
        return iter(self._elements)

    def __len__(self) -> int:
        return len(self._elements)

    def __str__(self) -> str:
        # I'm sorry
        return "(\n{}\n)".format("\n".join(
            "   ({}),".format(", ".join(
                str(self.get(x, y))
                for x in range(self.width)
            ))
            for y in range(self.height)
        ))

    def get(self, x: int, y: int) -> T:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("Matrix indices out of range")

        return self._elements[y * self.width + x]

    def set(self, x: int, y: int, value: T) -> None:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise IndexError("Matrix indices out of range")

        self._elements[y * self.width + x] = value

    def iter_xy(self) -> Iterator[tuple[int, int, T]]:
        # Equivalent of enumerate but 2D
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.get(x, y)

    def map(self, func: Callable[[T], U]) -> Matrix[U]:
        return Matrix(
            self.width,
            self.height,
            (func(element) for element in self),
        )

    def map_xy(self, func: Callable[[int, int, T], U]) -> Matrix[U]:
        return Matrix(
            self.width,
            self.height,
            (func(x, y, element) for x, y, element in self.iter_xy()),
        )


def _test() -> None:
    matrix: Matrix[int] = Matrix(3, 3, range(9))
    print(matrix)


if __name__ == "__main__":
    _test()
