# coding: UTF-8
# ==================================================================
# lib/dlna_logger.py
# ==================================================================
# VintageRadio - Helper for Logging.
# David de Lorenzo (2026)
# ==================================================================
import logging
import sys


def get_logger(name: str = __name__) -> logging.Logger:
    """Return a module-level logger configured exactly once."""
    logger = logging.getLogger(name)

    # Configure only the first time the logger is created
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # ensure DEBUG is enabled
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)  # or FileHandler('radio.log')
        # On ajoute un CarriageReturn pour la console Linux.
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s \r"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False  # avoid duplicate prints

    # Force line buffering for stdout to ensure immediate display
    # This is often the missing piece in async apps
    # sys.stdout.reconfigure(line_buffering=True)
    return logger
