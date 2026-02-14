"""An event system to pass around data through the composition tree

We'll probably need it, so better build it right now.

Created on 2026.02.15
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, ClassVar


class Event:
    """Base type for all events."""
    listeners: ClassVar[list[Callable]]

    def __init_subclass__(cls) -> None:
        cls.listeners = []

    @classmethod
    def connect(cls, callback: Callable) -> None:
        cls.listeners.append(callback)

    @classmethod
    def disconnect(cls, callback: Callable) -> None:
        cls.listeners.remove(callback)

    def emit(self) -> None:
        for callback in type(self).listeners:
            callback(self)


@dataclass(frozen=True, slots=True)
class RunButtonPressed(Event):
    pass


@dataclass(frozen=True, slots=True)
class ActivePyscriptChanged(Event):
    pyscript_path: Path | None
