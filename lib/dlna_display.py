# coding: UTF-8
# ==================================================================
# lib/dlna_display.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================


# ----------------------------------------------------------------------- #
# Cette classe gère l'affichage des messages devant être affichés à 
# l'utilisateur. Il y a une mode console, et un mode (final) où l'affichage
# se fait sur un écran LCD ou ePaper.
# ----------------------------------------------------------------------- #
class DLNADisplay:
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
            DLNADisplay.display_target = 1
        else:
            DLNADisplay.display_target = 0
        
    # --------------------------------------------------------------------- #
    # Affichage d'un texte
    # --------------------------------------------------------------------- #
    @staticmethod
    def show(text: str, color: str = "black"):
        if DLNADisplay.display_target >= 0:
            print(text)

    # --------------------------------------------------------------------- #
    # Affichage d'un texte et attente de réponse.
    # FONCTION BLOQUANTE
    # --------------------------------------------------------------------- #
    @staticmethod
    def input(text: str) -> str:
        choice = input(text)
        return choice
