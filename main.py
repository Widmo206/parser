"""Pyscript - a coding learning game

Created on 2026.01.28
Contributors:
    Romcode
    Widmo
"""

import logging

from app import App


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


if __name__ == "__main__":
    setup_logging()
    app = App()
    app.run()
