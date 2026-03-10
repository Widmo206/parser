"""Save class to manage user save files

Created on 2026.03.07
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
import logging
from pathlib import Path

import dacite
import yaml
from yaml.parser import ParserError

from common import message_error

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LevelScore:
    solution_path: Path
    token_count: int


@dataclass(frozen=True)
class Save:
    level_scores: dict[Path, LevelScore] = field(default_factory=dict)

    @classmethod
    def from_path(cls, path: Path) -> Save:
        logger.debug("Loading save from '%s'", path)

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            return dacite.from_dict(cls, data, dacite.Config(strict=True))
        except FileNotFoundError:
            message_error("Missing save file at '%s'", path)
        except ParserError:
            message_error("Failed to parse YAML data from '%s'", path)
        except dacite.DaciteError as e:
            message_error("Failed to parse save from YAML data from '%s': %s", path, e)

        return cls()

    def save(self, path: Path) -> None:
        logger.debug("Saving save to '%s'", path)

        data = asdict(self)
        try:
            with open(path, "w", encoding="utf-8") as file:
                yaml.safe_dump(data, file)
        except OSError:
            message_error("Failed to save to '%s'", path)
