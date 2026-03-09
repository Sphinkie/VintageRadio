# coding: UTF-8
# ==================================================================
# dlna_user_request.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import json
import asyncio
from pathlib import Path
from lib.dlna_logger import get_logger

log = get_logger(__name__)
REQUEST_PATH = Path("user_request.json")  # <-- location of the JSON file


# ----------------------------------------------------------------------- #
# Cette classe lit le fichier Json contenant la demande de l'auditeur
# ----------------------------------------------------------------------- #
class DLNAUserRequest:
    """ Interactions with json user request file. """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.default_mode = "By Genre"  # fre: "Par genre"
        self.default_genre = "Jazz"
        self.previous_mode = self.default_mode
        self.previous_genre = self.default_genre
        self.hasChanged = True
        self.new_request = {"mode": self.default_mode, "genre": self.default_mode}

    # ----------------------------------------------------------------------- #
    # Lit la demande de l'utilisateur dans un fichier json.
    # ----------------------------------------------------------------------- #
    def load_user_request(self):
        """
        Reads user_request.json and store a dict with at least the keys ``mode`` and ``genre``.
        Missing keys fall back to the defaults values.
        """
        if not REQUEST_PATH.is_file():
            log.warning("No file – just use the defaults")

        try:
            with REQUEST_PATH.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            # Normalise keys (allow upper‑case or missing entries)
            self.new_request["mode"] = data.get("mode", self.default_mode)
            self.new_request["genre"] = data.get("genre", self.default_genre)
        except Exception as e:  # pragma: no cover
            log.fatal(f"️Could not parse {REQUEST_PATH}: {e}")

    # -----------------------------------------------------------------
    # Recharge le fichier json.
    # -----------------------------------------------------------------
    def refresh_user_request(self):
        log.debug("refresh_user_request invoked")
        self.previous_mode = self.new_request["mode"]
        self.previous_genre = self.new_request["genre"]
        self.load_user_request()
        # Only change the variables if the file actually differs.
        # This avoids unnecessary prints when the user hasn't edited the file.
        self.hasChanged = (self.new_request["mode"] != self.previous_mode
                           or self.new_request["genre"] != self.previous_genre)
        if self.hasChanged:
            log.info(f"Detected user request change: {self.new_request['mode']} > {self.new_request['genre']}")

    # -----------------------------------------------------------------
    # Indique si le fichier a changé lors la dernière lecture.
    # -----------------------------------------------------------------
    def has_changed(self) -> bool:
        """ Return True if the user request has changed"""
        return self.hasChanged

    # -----------------------------------------------------------------
    # Retourne la dernière valeur lue.
    # -----------------------------------------------------------------
    def get(self, key) -> str:
        """ Return the value of the corresponding key 'mode' or 'genre' """
        return self.new_request.get(key)

    # -----------------------------------------------------------------
    # Acquitte le flag has_changed.
    # -----------------------------------------------------------------
    def ack_has_changed(self):
        """ Acknowlegment: Set has_changed to False. """
        self.hasChanged = False

    # -----------------------------------------------------------------
    # Relit périodiquement le fichier de user request.
    # Intervalle typique = 5s
    # -----------------------------------------------------------------
    async def repeating_reread(self, interval):
        """ Periodic task: re-read user request json file. """
        try:
            while True:
                self.refresh_user_request()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            log.warning("repeating refresh_user_request cancelled.")
