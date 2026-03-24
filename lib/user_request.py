# coding: UTF-8
# ==================================================================
# lib/user_request.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import json
import asyncio
from pathlib import Path
from lib.vr_logger import get_logger

log = get_logger(__name__)
REQUEST_PATH = Path("user_request.json")  # <-- location of the JSON file


# ----------------------------------------------------------------------- #
# Cette classe lit le fichier Json contenant la demande de l'auditeur.
# ----------------------------------------------------------------------- #
class UserRequest:
    """ Interactions with json user request file. """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor.
        Initialisation des valeurs par défaut.
        """
        self.default_mode = 'genre'
        self.default_request = 'Jazz'
        self.previous_mode = self.default_mode
        self.previous_request = self.default_request
        self.hasChanged = True
        self.new_request = {'mode': self.default_mode, 'request': self.default_request}

    # ----------------------------------------------------------------------- #
    # Lit la demande de l'utilisateur dans le fichier json.
    # ----------------------------------------------------------------------- #
    def load_user_request(self):
        """
        Reads user_request.json and store a dict with at least the keys ``mode`` and ``value``.
        Missing keys fall back to the defaults values.
        """
        if not REQUEST_PATH.is_file():
            log.warning("No file – Use the defaults")

        try:
            with REQUEST_PATH.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            # Normalise keys (allow upper‑case or missing entries)
            mode_value = data.get('mode', self.default_mode) # can be 'genre' or 'year'
            self.new_request['mode'] = mode_value
            self.new_request['request'] = data.get(mode_value, self.default_request)
        except Exception as e:
            log.fatal(f"️Could not parse {REQUEST_PATH}: {e}")

    # -----------------------------------------------------------------
    # Recharge le fichier json.
    # -----------------------------------------------------------------
    def refresh_user_request(self):
        # log.debug("refresh_user_request invoked")
        # On mémorise les valeurs précédentes.
        self.previous_mode = self.new_request['mode']
        self.previous_request = self.new_request['request']
        self.load_user_request()
        # Only change the variables if the file actually differs.
        # This avoids unnecessary prints when the user hasn't edited the file.
        self.hasChanged = (self.new_request['mode'] != self.previous_mode
                           or self.new_request['request'] != self.previous_request)
        if self.hasChanged:
            log.info(f"Detected user request change: {self.new_request['mode']} > {self.new_request['request']}")

    # -----------------------------------------------------------------
    # Indique si le fichier a été changé depuis la dernière lecture.
    # -----------------------------------------------------------------
    def has_changed(self) -> bool:
        """ Return True if the user request has changed. """
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
        """ Acknowlegment : Set has_changed to False. """
        self.hasChanged = False

    # -----------------------------------------------------------------
    # Relit périodiquement le fichier de la UserRequest.
    # Fonction asynchrone : On attend PUIS on lit le fichier.
    # -----------------------------------------------------------------
    async def repeating_reread(self, period: float):
        """
        Periodic task: re-read the UserRequest Json file.
        Args:
            period: attente avant la relecture du fichier. Typiquement 5s.
        """
        try:
            while True:
                await asyncio.sleep(period)
                self.refresh_user_request()
        except asyncio.CancelledError:
            log.warning("repeating_reread of UserRequest cancelled.")
