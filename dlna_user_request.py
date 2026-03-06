# dlna_user_request.py

import json
from pathlib import Path

REQUEST_PATH = Path("user_request.json")  # <-- location of the JSON file


# ----------------------------------------------------------------------- #
# Cette classe gère les musiques situées sur le serveur DLNA.
# ----------------------------------------------------------------------- #
class DLNAUserRequest:
    """
    Interactions with musical files.
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        # --------------------------------------------------------------------- #
        # Default User Request / Previous User Request
        # --------------------------------------------------------------------- #
        self.previous_mode = "By Genre"  # fre: "Par genre"
        self.previous_genre = "Jazz"
        self.hasChanged = False
        self.new_request = dict()

    # ----------------------------------------------------------------------- #
    # Lit la demande de l'utilisateur dans un fichier json.
    # ----------------------------------------------------------------------- #
    def load_user_request(self) -> dict:
        """
        Reads user_request.json and returns a dict with at least the keys
        ``mode`` and ``genre``.  Missing keys fall back to the defaults
        defined in the original script.
        """
        defaults = {"mode": self.previous_mode, "genre": self.previous_genre}

        if not REQUEST_PATH.is_file():
            print("No file – just use the defaults")
            return defaults

        try:
            with REQUEST_PATH.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            # Normalise keys (allow upper‑case or missing entries)
            self.new_request["mode"] = data.get("mode", defaults["mode"])
            self.new_request["genre"] = data.get("genre", defaults["genre"])
            # return {"mode": mode, "genre": genre}
            return self.new_request
        except Exception as e:  # pragma: no cover
            print(f"️Could not parse {REQUEST_PATH}: {e}")
            return defaults

    # -----------------------------------------------------------------
    # Recharge le fichier json. A appeler sous forme de callback.
    # -----------------------------------------------------------------
    def refresh_user_request(self):
        """ Return True if the user request has changed"""
        print("Callback called")
        self.previous_mode = self.new_request["mode"]
        self.previous_genre = self.new_request["genre"]
        self.new_request = self.load_user_request()
        # Only change the variables if the file actually differs.
        # This avoids unnecessary prints when the user hasn't edited the file.
        self.hasChanged = (self.new_request["mode"] != self.previous_mode
                           or self.new_request["genre"] != self.previous_genre)
        if self.hasChanged:
            print(f"\nDetected user request change: {self.new_request['mode']} > {self.new_request['genre']}")
            # self.previous_mode = self.new_request["mode"]
            # self.previous_genre = self.new_request["genre"]

    # -----------------------------------------------------------------
    # Indique si le fichier a changé lors la dernière lecture
    # -----------------------------------------------------------------
    def has_changed(self) -> bool:
        """ Return True if the user request has changed"""
        return self.hasChanged

    # -----------------------------------------------------------------
    # Retourne la dernière valeur lue.
    # -----------------------------------------------------------------
    def get(self, key) -> str:
        """ Return the value of the corresponding key 'mode' or 'genre' """
        if key == "mode":
            return self.previous_mode
        elif key == "genre":
            return self.previous_genre
        else:
            return self.new_request.get(key)
