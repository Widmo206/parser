"""Token class used by Parser during tokenization

Created on 2026.02.21
Contributors:
    Widmo
"""

from dataclasses import dataclass
from typing import Any

from enums import TokenType


@dataclass(frozen=True)
class Token(object):
    type: TokenType
    value: Any

    def __repr__(self):
        if self.value is None:
            return f"Token({self.type.name})"
        else:
            return f"Token({self.type.name}, {repr(self.value)})"
