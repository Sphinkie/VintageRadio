# coding: UTF-8
# ==================================================================
# dlna_preferences.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import configparser
from pathlib import Path
from typing import List, Tuple, Optional
from lib.dlna_logger import get_logger

# --------------------------------------------------------------------- #
# Configuration handling (preferred_dlna.ini)
# --------------------------------------------------------------------- #
CONFIG_FILE = Path("preferred_dlna.ini")
CONFIG_SECTION = "server"
log = get_logger(__name__)


# --------------------------------------------------------------------- #
# Lecture des préférences.
# Retourne la "Description URL" du Serveur DLNA.
# --------------------------------------------------------------------- #
def load_preferred_server() -> Optional[str]:
    """Return the saved server control URL, or None if the file is missing."""
    if not CONFIG_FILE.is_file():
        log.warning("file '%s' not found", CONFIG_FILE)
        return None
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    return cfg.get(CONFIG_SECTION, "desc_url", fallback=None)


# --------------------------------------------------------------------- #
# Ecriture des préférences
# --------------------------------------------------------------------- #
def save_preferred_server(desc_url: str) -> None:
    """Persist the chosen server's control URL for next runs."""
    cfg = configparser.ConfigParser()
    cfg[CONFIG_SECTION] = {"desc_url": desc_url}
    with CONFIG_FILE.open("w") as fp:
        cfg.write(fp)
        pass
    log.info("file '%s' written", CONFIG_FILE)


