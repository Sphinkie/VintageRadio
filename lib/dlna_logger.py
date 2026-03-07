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
        logger.setLevel(logging.DEBUG)               # ensure DEBUG is enabled
        handler = logging.StreamHandler(sys.stdout)  # or FileHandler('radio.log')
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False                     # avoid duplicate prints
    return logger