# coding: UTF-8
# ==================================================================
# lib/dlna_logger.py
# ==================================================================
# VintageRadio - Helper for Logging.
# David de Lorenzo (2026)
# ==================================================================
import logging
import sys


# ----------------------------------------------------------------------
# Fournit un logger
# ----------------------------------------------------------------------
def get_logger(name: str = __name__) -> logging.Logger:
    """Return a module-level logger configured exactly once."""
    logger = logging.getLogger(name)
    # Configure only the first time the logger is created
    if not logger.handlers:
        # On récupère la config faite ailleurs
        logger.propagate = True
    # Force line buffering for stdout to ensure immediate display
    # This is often the missing piece in async apps
    # sys.stdout.reconfigure(line_buffering=True)
    return logger


# ----------------------------------------------------------------------
# Configuration du Logger
# ----------------------------------------------------------------------
def set_logging(verbose_level: int) -> None:
    """
    Configure logging based on verbosity level.

    Args:
        verbose_level: 0 = WARNINGS+, 1 = INFO, 2 = DEBUG
    """
    # Map verbosity to log level
    level_map = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    # Default level : logging.WARNING
    level = level_map.get(verbose_level, logging.WARNING)
    level = logging.DEBUG
    # Configure root logger
    logging.basicConfig(
        level=level,
        # On ajoute un CarriageReturn pour la console Linux.
        format='%(asctime)s %(levelname)s %(name)s: %(message)s \r',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True  # Overwrite any existing configuration
    )
