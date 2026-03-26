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
    # --------------------------------------------------------------------- #
    def __init__(self, target: str):
        """ 
        Constructor. 
        :param target: allowed values 'tty' | 'raspberry'
        """
        if target == 'raspberry':
            Display.display_target = 1
        else:
            Display.display_target = 0

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    @staticmethod
    def show(*texts):
        """
        Efface l'afficheur et affiche un certain nombre de textes
        :param texts: Une suite de texte (nombre non précisé).
        """
        if Display.display_target >= 0:
            Display.flush()
            for text in texts:
                print(text + "\r")

    @staticmethod
    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def add_line(text: str):
        """
        Affiche une ligne à la suite de la précédente.
        :param text: Une ligne de texte.
        """
        if Display.display_target >= 0:
            print(text + "\r")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    @staticmethod
    def warning(text: str):
        """
        Affichage d'un texte en couleur rouge.
        :param text: Une ligne de texte.
        """
        if Display.display_target >= 0:
            print(" ⚡ " + text)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    @staticmethod
    def flush():
        """
        Efface l'afficheur.
        """
        if Display.display_target >= 0:
            print("--------------\r")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    @staticmethod
    def input(text: str) -> str:
        """
        Affichage d'un texte et attente de réponse.
        FONCTION BLOQUANTE
        :param text: Un texte d'invite.
        :return: Le caractère ou le texte entré par l'utilisateur.
        """
        choice = input(text)
        return choice

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    @staticmethod
    def pick_server_interactively(server_list: List) -> Optional[str]:
        """
        Affiche le menu de choix du server DLNA parmi ceux qui ont été trouvé,
        et demande à l'utilisateur d'en choisir un.
        :param server_list: La liste de choix (liste de serveurs DLNA).
        :return: Retourne la Control URL du serveur choisi (ou None).
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
