"""LevelView class to manage TileLabels and obey LevelModel

Created on 2026.01.28
Contributors:
    Romcode
"""

from math import floor
import tkinter as tk

import ttkbootstrap as ttk

from enums import Direction, TileActionType, TileType
import events
from tile_label import TileLabel


class LevelView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        layout: str,
        **kwargs,
    ) -> None:
        if layout == "":
            raise ValueError("Tilemap layout cannot be empty")

        self.layout = layout

        rows = self.layout.splitlines()
        self.width = len(rows[0])
        self.height = len(rows)

        if any(len(row) != self.width for row in rows):
            raise ValueError(f"Mismatched row length in tilemap layout\n{self.layout}")

        kwargs.setdefault("padding", 64)
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.grid()

        self.bind("<Configure>", lambda _: self.update_tile_size())

        self.tiles = []
        for y in range(self.height):
            for x in range(self.width):
                tile = TileLabel(self.grid_frame, rows[y][x])
                tile.grid(column=x, row=y)
                self.tiles.append(tile)

        # TODO: Remove manual movement
        self.bind_all("<w>", lambda _: events.MoveRequested(Direction.UP))
        self.bind_all("<s>", lambda _: events.MoveRequested(Direction.DOWN))
        self.bind_all("<a>", lambda _: events.MoveRequested(Direction.LEFT))
        self.bind_all("<d>", lambda _: events.MoveRequested(Direction.RIGHT))

    def get_tile(self, x: int, y: int) -> TileLabel | None:
        try:
            assert 0 <= x < self.width
            assert 0 <= y < self.height
            return self.tiles[y * self.width + x]
        except (AssertionError, IndexError):
            return None

    def move_tile(self, x: int, y: int, direction: Direction) -> None:
        from_tile = self.get_tile(x, y)
        to_tile = self.get_tile(x + direction.x, y + direction.y)

        if from_tile is not None and to_tile is not None and to_tile.tile_type.walkable:
            to_tile.set_tile_type(from_tile.tile_type)
            from_tile.set_tile_type(TileType.EMPTY)

    def update_tile_size(self) -> None:
        padding = int(str(self.cget("padding")[0])) # TODO: clean up this weird conversion issue
        tile_size = floor(min(
            (self.winfo_width() - padding * 2) / self.width,
            (self.winfo_height() - padding * 2) / self.height,
        ))

        for tile in self.tiles:
            tile.resize(tile_size)
