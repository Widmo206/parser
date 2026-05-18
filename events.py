"""A global event system to pass around data through the composition tree

We'll probably need it, so better build it right now.
We need it. But be careful choosing between tk events and these events.

Created on 2026.02.15
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Callable, ClassVar

from level import Level
from save import LevelScore
from tile_data import TileData

logger = logging.getLogger(__name__)


class Event:
    """Base type for all events.

    Works almost like Godot signals, with a static list of listeners.
    Instantiate an event to emit it.

    We would use typing.Self instead of __future__ annotations because
    Event is general while Self takes the form of the event subclass,
    but Self is python 3.11+ only.
    """
    _listeners: ClassVar[list[Callable[[Event], None]]]

    def __init_subclass__(cls) -> None:
        cls._listeners = []

    @classmethod
    def connect(cls, callback: Callable[[Event], None]) -> None:
        logger.debug(
            "Connecting method '%s' to event '%s'",
            callback.__name__,
            cls.__name__,
        )
        cls._listeners.append(callback)

    @classmethod
    def disconnect(cls, callback: Callable[[Event], None]) -> None:
        logger.debug(
            "Disconnecting method '%s' from event '%s'",
            callback.__name__,
            cls.__name__,
        )
        cls._listeners.remove(callback)

    def __post_init__(self) -> None:
        cls = type(self)
        logger.debug(
            "Emitting event %r to %d listener(s)",
            self,
            len(cls._listeners),
        )
        for callback in cls._listeners:
            callback(self)


@dataclass(frozen=True, slots=True)
class ActivePyscriptRequested(Event):
    queue_cycle_start: bool = False


@dataclass(frozen=True, slots=True)
class ClosePopupRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class Cycled(Event):
    pass


@dataclass(frozen=True, slots=True)
class CyclingToggled(Event):
    is_running: bool


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
class LevelClosed(Event):
    pass


@dataclass(frozen=True, slots=True)
class LevelComplete(Event):
    level_name: str
    level_score: LevelScore


@dataclass(frozen=True, slots=True)
class LevelOpened(Event):
    level: Level


@dataclass(frozen=True, slots=True)
class CloseLevelRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class LevelSelected(Event):
    path: Path


@dataclass(frozen=True, slots=True)
class LevelScoreUpdated(Event):
    level_score: LevelScore


@dataclass(frozen=True, slots=True)
class LevelStateChanged(Event):
    is_active: bool


@dataclass(frozen=True, slots=True)
class LevelSelectOpened(Event):
    pass


@dataclass(frozen=True, slots=True)
class ParseRequested(Event):
    path: Path
    queue_cycle_start: bool = False


@dataclass(frozen=True, slots=True)
class PyscriptOutputRequested(Event):
    processor_id: int = 0
    text: Any = ""


@dataclass(frozen=True, slots=True)
class RedoRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class ReloadDefaultRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class RestartRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class RunPauseRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class StepBackRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class StepForwardRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class TileDataChanged(Event):
    x: int
    y: int
    tile_data: TileData


@dataclass(frozen=True, slots=True)
class ToggleFullscreenRequested(Event):
    pass


@dataclass(frozen=True, slots=True)
class UndoRequested(Event):
    pass
