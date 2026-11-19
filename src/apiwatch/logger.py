
import logging
from pathlib import Path


def setup_logger(
    name: str = "apiwatch",
    level: str = "INFO",
    log_file: str | None = None,
) -> logging.Logger:
    """Create and configure an APIWatch logger."""

    logger = logging.getLogger(name)

    logger.setLevel(level.upper())
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add console handler if it doesn't already exist
    has_console_handler = any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )

    if not has_console_handler:

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:

        log_path = Path(log_file)

        log_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        absolute_path = str(log_path.resolve())

        has_file_handler = any(
            isinstance(handler, logging.FileHandler)
            and handler.baseFilename == absolute_path
            for handler in logger.handlers
        )

        if not has_file_handler:

            file_handler = logging.FileHandler(
                log_path,
                encoding="utf-8",
            )

            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

    return logger
