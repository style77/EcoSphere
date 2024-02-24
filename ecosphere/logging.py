import logging
from typing import Literal


def set_logging_level(level: Literal["debug", "info", "warning", "error", "critical"]):
    logging.basicConfig(
        level=level.upper(), format="%(asctime)s - %(levelname)s - %(message)s"
    )
