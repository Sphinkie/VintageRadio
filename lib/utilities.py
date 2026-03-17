# coding: UTF-8
# ==================================================================
# lib/utilities.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import hashlib


# --------------------------------------------------------------------- #
# Calcule un hash de 8 caractères basé sur le nom du fichier.
# --------------------------------------------------------------------- #
@staticmethod
def calculate_file_hash(file_name: str) -> str:
    """
    Calcule un hash de 8 caractères basé uniquement sur le nom du fichier.
    
    Args:
        file_name: Nom du fichier MP3 (ex: "01_Song_Name.mp3")
        
    Returns:
        Hash hexadécimal de 8 caractères
    """
    # Utilise SHA256 puis prend les 8 premiers caractères
    hash_obj = hashlib.sha256(file_name.encode('utf-8'))
    return hash_obj.hexdigest()[:8].upper()




# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
if __name__ == "__main__":
    # -------------------------------------------------------------
    # TEST DU HASHAGE
    # -------------------------------------------------------------
    filename = "Aretha Franklin - I will Survive.mp3"
    hash1 = calculate_file_hash(filename)  # Ex: "D6DC212A"
    print(hash1)

    filename = "Blue Steel & His Orchestra - Sugar Babe, I'm Leavin'!.mp3"
    hash2 = calculate_file_hash(filename)  # Ex: "16B19780"
    print(hash2)
