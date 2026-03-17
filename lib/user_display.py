# coding: UTF-8
# ==================================================================
# lib/user_display.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from typing import List, Optional


# ----------------------------------------------------------------------- #
# Cette classe gère l'affichage des messages devant être affichés à 
# l'utilisateur. Il y a une mode console, et un mode (final) où l'affichage
# se fait sur un écran LCD ou ePaper.
# ----------------------------------------------------------------------- #
class Display:
    """ Interactions with physical display. """
    display_target = 0

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, target: str):
        """ 
        Constructor. 
        Param target: allowed values 'tty' | 'raspberry'
        """
        if target == 'raspberry':
            Display.display_target = 1
        else:
            Display.display_target = 0

    # --------------------------------------------------------------------- #
    # Efface l'afficheur et affiche un certain nombre de textes
    # --------------------------------------------------------------------- #
    @staticmethod
    def show(*texts):
        if Display.display_target >= 0:
            Display.flush()
            for text in texts:
                print(text + "\r")

    @staticmethod
    # --------------------------------------------------------------------- #
    # Affiche une ligne à la suite de la précédente
    # --------------------------------------------------------------------- #
    def add_line(text: str):
        if Display.display_target >= 0:
            print(text + "\r")

    # --------------------------------------------------------------------- #
    # Affichage d'un texte en couleur rouge
    # --------------------------------------------------------------------- #
    @staticmethod
    def warning(text: str):
        if Display.display_target >= 0:
            print("🚦 ⚡ " + text)

    # --------------------------------------------------------------------- #
    # Efface l'afficheur
    # --------------------------------------------------------------------- #
    @staticmethod
    def flush():
        if Display.display_target >= 0:
            print("--------------\r")

    # --------------------------------------------------------------------- #
    # Affichage d'un texte et attente de réponse.
    # FONCTION BLOQUANTE
    # --------------------------------------------------------------------- #
    @staticmethod
    def input(text: str) -> str:
        choice = input(text)
        return choice

    # --------------------------------------------------------------------- #
    # Affiche le menu de choix du server DLNA parmi ceux qui ont été
    # trouvé, et demande à l'utilisateur d'en choisir un.
    # Retourne l'URL choisie (ou None).
    # --------------------------------------------------------------------- #
    @staticmethod
    def pick_server_interactively(server_list: List) -> Optional[str]:
        """
        Show a numbered list of discovered servers (showing just the host part)
        and ask the user to choose one.  Returns the selected *control URL*.
        """
        if not server_list:
            return None

        Display.flush()
        Display.add_line("Discovered DLNA MediaServers:")
        for idx, (desc_url, usn) in enumerate(server_list, start=1):
            host = desc_url.split("/", 3)[2]  # crude host extraction
            Display.add_line(f"[{idx}] {host}")

        while True:
            choice = Display.input(f"Select a server (1‑{len(server_list)} or press Enter to abort): ")
            if not choice:
                return None
            if choice.isdigit():
                i = int(choice)
                if 1 <= i <= len(server_list):
                    return server_list[i - 1][0]  # return the Description URL
            Display.warning("Invalid selection – try again.")
