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
    # --------------------------------------------------------------------- #
    def __init__(self, db_path: str):
        """
        Constructeur.
        :param db_path: Le chemin et le nom de la base de données.
        """
        self.db = VRDatabase(db_path)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def store_tracks(self, tracks: List[dict]):
        """
        Stocke (ou met à jour) une liste de pistes dans la base.
        :param tracks: Une liste de tracks avec leurs metadata.
        """
        self.db.store_tracks(tracks)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_tracks_for_decade(self, year: int) -> List[str]:
        """
        Retourne une liste d'URLs filtrée par plage de dates avec ordre circulaire.
        En fonction de l'année demandée, on remonte une liste de MP3 contenus
        dans la "période" correspondante.
        On a défini 9 "périodes" (décades) :
         - 0000-1700 (moyen-age)
         - 1700-1800 (en général, la musique classique)
         - 1800-1900 (opéras et débuts de la chanson)
         - 20's      (chansons d'avant-guerre)
         - 40's      (musiques des années 40)
         - 50's      (musiques des années 50 - fifties)
         - 60's      (musiques des années 60 - sixties)
         - 70's      (musiques des années 70 - seventies)
         - Ce qui est venu après (entre 1980 et 2050)
        :param year: Date de départ (ex : 1964)
        :return: Une liste d'URLs triées selon l'ordre circulaire.
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
    # --------------------------------------------------------------------- #
    def get_tracks_for_genre(self, value: str) -> List[str]:
        """
        Demande des urls pour le genre donné.
        :param value: Le nom d'un genre de musiques.
        :return: Une liste d'URLs dans un ordre aléatoire à chaque fois différent.
        """
        return self.db.get_track_urls_by_genre(value)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_tracks_for_beat(self, value: float) -> List[str]:
        """
        Demande des tracks pour un rythme (bpm) donné.
        La fonction renvoie la liste des URLs à partir du BPM donné, et dans le sens demandé
        croissant ou décroissant.
        Si le rythme demandé est lent, on va vers du plus calme.
        Si le rythme demandé est rapide, on va vers du plus énergique.
        :param value: La valeur du BPM demandée de base.
        :returns: Une liste d'URLs triées selon le critère demandé.
        """
        direction = "desc" if value < 120 else "asc"
        return self.db.get_track_urls_by_bpm(value, direction)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_unrythmed_tracks(self, force: bool = False) -> List[str]:
        """
        Demande des urls des clips qui n'ont pas de BPM.
        :param force: Si True, renvoie la liste de toutes les URLs, pour un re-scan total.
        :returns: Une liste d'URLs.
        """
        if force:
            # Si force, on renvoie toutes les urls.
            return self.db.get_track_urls()
        else:
            # Sinon, on ne renvoie que les urls qui n'ont pas de BPM en base.
            return self.db.get_track_urls_by_bpm(None)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def update_track_rating(self, tags: dict):
        """
        Met à jour le rating d'une piste.
        :param tags: Un dictionnaire ('url', 'rating', 'bpm').
        """
        self.db.update_track(tags['url'], "rating", tags['rating'])
        log.debug("tag updated: %s",tags['rating'])

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def update_track_bpm(self, tags: dict):
        """
        Met à jour le BPM (Beat Per Minute) d'une piste.
        :param tags: Un dictionnaire ('url', 'rating', 'bpm').
        """
        self.db.update_track(tags['url'], "bpm", tags['bpm'])
        log.info("BPM updated for %s: %s",tags['url'], tags['bpm'])

    # --------------------------------------------------------------------- #
    # Retourne des infos sur le clip demandé, en les cherchant dans la
    # base de données.
    # --------------------------------------------------------------------- #
    def get_track_info(self, item_id: str) -> Optional[tuple]:
        """
        Extract metadata from the database.
        :param item_id: The ID of the item to look up. Ex: '2913'.
        :returns:
            Tuple of (title, artist, year, genre).
            `Empty strings` if field is missing.
            `None` if item not found.
        """
        log.debug("get clip info from db for item id: %s", item_id)
        metadata = self.db.get_track_info(item_id)
        if metadata:
            return metadata['title'], metadata['artist'], metadata['year'], metadata['genre']
        else:
            # Not found
            return None

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def close(self):
        """
        Ferme la connexion à la base de données.
        """
        self.db.close()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def drop_db(self):
        """
        Supprime la base de données.
        """
        self.db.drop()


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
