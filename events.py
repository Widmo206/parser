"""An event system to pass around data through the composition tree

We'll probably need it, so better build it right now.
We need it. But be careful choosing between tk events and these events.

Created on 2026.02.15
Contributors:
    Romcode
"""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Callable, ClassVar, Self

from level import Level

logger = logging.getLogger(__name__)


class Event:
    """Base type for all events.

    Works almost exactly like Godot signals.
    """

    # We annotate with Self instead of __future__ annotations
    # because Event is too general while Self takes the form of the event subclass.
    _listeners: ClassVar[list[Callable[[Self], None]]]

    def __init_subclass__(cls) -> None:
        cls._listeners = []

    @classmethod
    def connect(cls, callback: Callable[[Self], None]) -> None:
        logger.debug(f"Connecting method '{callback.__name__}' to event '{cls.__name__}'")
        cls._listeners.append(callback)

    @classmethod
    def disconnect(cls, callback: Callable[[Self], None]) -> None:
        logger.debug(f"Disconnection method '{callback.__name__}' from event '{cls.__name__}'")
        cls._listeners.remove(callback)

    def __post_init__(self) -> None:
        cls = type(self)
        logger.debug(f"Emitting event '{cls.__name__}' to {len(cls._listeners)} listener(s)")
        for callback in cls._listeners:
            callback(self)


@dataclass(frozen=True, slots=True)
class ActivePyscriptChanged(Event):
    pyscript_path: Path | None


@dataclass(frozen=True, slots=True)
class FileNewRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class FileOpenRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class FileSaveRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class FileSaveAsRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class ExitRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class LevelOpened(Event):
    level: Level


@dataclass(frozen=True, slots=True)
class LevelSelectButtonPressed(Event):
    pass


@dataclass(frozen=True, slots=True)
class LevelSelected(Event):
    path: Path


@dataclass(frozen=True, slots=True)
class LevelSelectOpened(Event):
    pass


@dataclass(frozen=True, slots=True)
class RunButtonPressed(Event):
    pass
