# coding: UTF-8
# ==================================================================
# lib/user_display.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================


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
