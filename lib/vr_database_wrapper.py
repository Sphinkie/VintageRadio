# coding: UTF-8
# ==================================================================
# lib/vr_database_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.vr_database import VRDatabase
from lib.vr_logger import get_logger
from typing import List, Optional

log = get_logger(__name__)


# --------------------------------------------------------------------- #
# Wrapper de la base de données des métadonnées MP3.
# --------------------------------------------------------------------- #
class DBWrapper:
    """
    Wrapper autour de la base de données des métadonnées MP3.
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, db_path: str):
        self.db = VRDatabase(db_path)

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
        """
        Retourne une liste d'URLs filtrée par plage de dates avec ordre circulaire.
        Args :
            year : Date de départ (ex : 1964)
        Returns :
            Liste d'URLs triées selon l'ordre circulaire
        """
        log.debug(f" Demande les clips de la décade {year}...")
        if year < 1700:
            return self.db.get_track_urls_by_date_range(year, 0, 1700)
        if year < 1800:
            return self.db.get_track_urls_by_date_range(year, 1700, 1800)
        if year < 1900:
            return self.db.get_track_urls_by_date_range(year, 1800, 1900)
        if year < 1940:
            return self.db.get_track_urls_by_date_range(year, 1900, 1939)
        if year < 1950:
            return self.db.get_track_urls_by_date_range(year, 1940, 1949)
        if year < 1960:
            return self.db.get_track_urls_by_date_range(year, 1950, 1959)
        if year < 1970:
            return self.db.get_track_urls_by_date_range(year, 1960, 1969)
        if year < 1980:
            return self.db.get_track_urls_by_date_range(year, 1970, 1979)
        return self.db.get_track_urls_by_date_range(year, 1980, 2050)

    # --------------------------------------------------------------------- #
    # Demande les url pour un genre donné.
    # --------------------------------------------------------------------- #
    def get_tracks_for_genre(self, value: str) -> List[str]:
        return self.db.get_track_urls_by_genre(value)

    # --------------------------------------------------------------------- #
    # Met à jour le rating d'une piste.
    # --------------------------------------------------------------------- #
    def update_track_rating(self, url: str, rating: int):
        self.db.update_track(url, "rating", rating)

    # --------------------------------------------------------------------- #
    # Met à jour le BPM (Beat Per Minute) d'une piste.
    # --------------------------------------------------------------------- #
    def update_track_bpm(self, url: str, bpm: int):
        self.db.update_track(url, "bmp", bpm)

    # --------------------------------------------------------------------- #
    # Retourne des infos sur le clip demandé, en les cherchant dans la
    # base de données.
    # --------------------------------------------------------------------- #
    def get_track_info(self, item_id: str) -> Optional[tuple]:
        """
        Extract metadata from the database.

        Args:
            item_id: The ID of the item to look up. Ex: '2913'.

        Returns:
            Tuple of (title, artist, year, genre)
            Empty strings if field is missing
            None if item not found
        """
        log.debug("get clip info from db for item id: %s", item_id)
        metadata = self.db.get_track_info(item_id)
        if metadata:
            return metadata['title'], metadata['artist'], metadata['year'], metadata['genre']
        else:
            # Not found
            return None

    # --------------------------------------------------------------------- #
    # Ferme la connexion à la base de données
    # --------------------------------------------------------------------- #
    def close(self):
        self.db.close()


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
if __name__ == "__main__":
    db_wrapper = DBWrapper("data/music_metadata.db")
    # -------------------------------------------------------------
    # TEST DE COUNT
    # -------------------------------------------------------------
    print(f"Total {db_wrapper.db.count()} tracks")

    # -------------------------------------------------------------
    # TEST DE LISTE DES FIFTIES
    # -------------------------------------------------------------
    # Récupérer une liste basée sur la date
    urls = db_wrapper.get_tracks_for_decade(1955)
    print(f"Retrieved {len(urls)} songs for 1955")
    # -------------------------------------------------------------
    # TEST DE LISTE DES CHANSONS
    # -------------------------------------------------------------
    urls = db_wrapper.get_tracks_for_genre('Blues')
    print(f"Retrieved {len(urls)} songs of Blues")
