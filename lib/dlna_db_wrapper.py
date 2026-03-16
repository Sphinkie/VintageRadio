# coding: UTF-8
# ==================================================================
# lib/dlna_db_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_db import DLNADatabase
from lib.dlna_logger import get_logger
from typing import List, Optional, Tuple

log = get_logger(__name__)


# --------------------------------------------------------------------- #
# Wrapper de la base de données des métadonnées MP3.
# --------------------------------------------------------------------- #
class DLNADbWrapper:
    """
    Wrapper de la base de données des métadonnées MP3.
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, db_path: Optional[str]):
        self.db = DLNADatabase(db_path)

    # --------------------------------------------------------------------- #
    # Stocke (ou met à jour) une liste de pistes dans la base.
    # --------------------------------------------------------------------- #
    def store_tracks(self, tracks: List[dict]):
        self.db.store_tracks(tracks)

    # --------------------------------------------------------------------- #
    # En fonction de l'année demandée, on remonte une liste de MP3 contenus
    # dans la "période" correspondante.
    # On a défini 9 "périodes" :
    #   0000-1700 (moyen-age)
    #   1700-1800 (en général, la musique classique)
    #   1800-1900 (opéras et débuts de la chanson)
    #   20's      (chansons d'avant-guerre)
    #   40's      (musiques des années 40)
    #   50's      (musiques des années 50 - fifties)
    #   60's      (musiques des années 60 - sixties)
    #   70's      (musiques des années 70 - seventies)
    #   Ce qui est venu après (entre 1980 et 2050)
    # --------------------------------------------------------------------- #
    def get_tracks_for_decade(self, year: int) -> List[str]:
        if year < 1700: return self.db.get_tracks_by_date_range(year, 0, 1700)
        if year < 1800: return self.db.get_tracks_by_date_range(year, 1700, 1800)
        if year < 1900: return self.db.get_tracks_by_date_range(year, 1800, 1900)
        if year < 1940: return self.db.get_tracks_by_date_range(year, 1900, 1939)
        if year < 1950: return self.db.get_tracks_by_date_range(year, 1940, 1949)
        if year < 1960: return self.db.get_tracks_by_date_range(year, 1950, 1959)
        if year < 1970: return self.db.get_tracks_by_date_range(year, 1960, 1969)
        if year < 1980: return self.db.get_tracks_by_date_range(year, 1970, 1979)
        return self.db.get_tracks_by_date_range(year, 1980, 2050)

    # --------------------------------------------------------------------- #
    # demande les url pour un genre donné
    # --------------------------------------------------------------------- #
    def get_tracks_by_genre(self, value: str) -> List[str]:
        return self.db.select_url('genre', value)

    # --------------------------------------------------------------------- #
    # Retourne les metadata de la piste demandée.
    # --------------------------------------------------------------------- #
    def get_track_info(self, url: str) -> Optional[dict]:
        return self.db.get_track_info(url)

    # --------------------------------------------------------------------- #
    # Met à jour le rating d'une piste.
    # --------------------------------------------------------------------- #
    def update_track_rating(self, url: str, rating: int):
        self.db.update_track(url, "rating", rating)

    # --------------------------------------------------------------------- #
    # Met à jour le BPM (Beat Per Minute) d'une piste
    # --------------------------------------------------------------------- #
    def update_track_bpm(self, url: str, bpm: int):
        self.db.update_track(url, "bmp", bpm)

    # --------------------------------------------------------------------- #
    # Ferme la connexion à la base de données
    # --------------------------------------------------------------------- #
    def close(self):
        self.db.close()
