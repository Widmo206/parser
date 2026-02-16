"""Pyscript - a coding learning game

Created on 2026.01.28
Contributors:
    Romcode
    Widmo
"""

import logging

from common import SOLUTIONS_DIR
import events
from interface import Interface
from parser import FunctionHolder, Parser


def main() -> None:
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

    events.RunRequested.connect(_on_run_requested)

    interface = Interface()
    interface.mainloop()


def setup_logging() -> None:
    open("latest.log", "w", encoding="utf-8").close() # Clears the previous logs
    logging.basicConfig(
        filename='latest.log',
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)03d | %(levelname)-7s | %(name)-13s | %(message)s",
        datefmt='%Y.%m.%d %H:%M:%S',
    )
    # Needed because PIL was flooding the logs
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)


def _on_run_requested(event: events.RunRequested) -> None:
    parser = Parser(FunctionHolder(), event.path)
    print(parser.tokenize())


if __name__ == "__main__":
    setup_logging()
    main()

# Removed the "else raise RuntimeError" block,
# ChatGPT said "This is not idiomatic Python and will bite you later."
