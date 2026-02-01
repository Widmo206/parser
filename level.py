"""Level class to store level files

Created on 2026.01.28
Contributors:
    Romcode
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import yaml # pip install PyYAML

from errors import LevelParserError


@dataclass
class Level:
    PATHS = (
        Path("levels/tutorial.yaml"),
    )

    name: str
    tilemap_layout: str
    pyscript: str

    @classmethod
    def from_path(cls, path: Path) -> Level:
        with open(path) as file:
            try:
                return cls(**yaml.safe_load(file))
            except yaml.parser.ParserError as e:
                raise LevelParserError(f"Failed to parse level from '{path}'") from e
