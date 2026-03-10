"""Level class to store level files

Created on 2026.01.28
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path

import dacite
import yaml
from yaml.parser import ParserError

from common import message_error, normalize_path
from matrix import Matrix
from tile_data import TileData

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Level:
    PATHS = (
        Path("levels/test.yaml"),
        Path("levels/astar_test.yaml"),
        Path("levels/tutorial.yaml"),
    )
    YAML_FIELDS = (
        "name",
        "pyscript_path",
        "layout",
        "direction_layout",
    )

    name: str = "Missing level name"
    pyscript_path: Path | None = None
    layout: str = ""
    direction_layout: str = ""
    width: int = 0
    height: int = 0

    @classmethod
    def from_path(cls, path: Path) -> Level:
        logger.debug("Loading level from '%s'", path)

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            return dacite.from_dict(cls, data, dacite.Config(strict=True))
        except FileNotFoundError:
            message_error("Missing level file at '%s'", path)
        except ParserError:
            message_error("Failed to parse YAML data from '%s'", path)
        except dacite.DaciteError as e:
            message_error("Failed to parse level from YAML data from '%s': %s", path, e)

        return cls()

    def __post_init__(self) -> None:
        def raise_dimension_mismatch() -> None:
            # Commonly used error message
            message_error(
                "Mismatched dimensions in layout\n%s\n and direction layout\n%s",
                self.layout,
                self.direction_layout,
            )
            object.__setattr__(self, "layout", "")
            object.__setattr__(self, "direction_layout", "")
            return

        if self.layout == "":
            object.__setattr__(self, "width", 0)
            object.__setattr__(self, "height", 0)

            if self.direction_layout != "":
                raise_dimension_mismatch()

            return

        rows = self.layout.splitlines()
        object.__setattr__(self, "width", len(rows[0]))
        object.__setattr__(self, "height", len(rows))

        if any(len(row) != self.width for row in rows):
            raise message_error("Mismatched row length in layout\n%s", self.layout)

        if self.direction_layout == "":
            raise_dimension_mismatch()

        direction_rows = self.direction_layout.splitlines()

        if (
            len(direction_rows) != self.height
            or any(len(row) != self.width for row in direction_rows)
        ):
            raise_dimension_mismatch()

    def get_tile_data_matrix(self) -> Matrix[TileData]:
        return Matrix(
            self.width,
            self.height,
            (
                TileData(type_char, direction_char)
                for type_char, direction_char
                in zip(
                    self.layout.replace("\n", ""),
                    self.direction_layout.replace("\n", ""),
                )
            )
        )
