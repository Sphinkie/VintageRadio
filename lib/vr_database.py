# coding: UTF-8
# ==================================================================
# lib/vr_database.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import sqlite3
from typing import List, Optional
from lib.vr_logger import get_logger

log = get_logger(__name__)


# --------------------------------------------------------------------- #
# Gestion de la base de données SQLite pour les métadonnées MP3.
# --------------------------------------------------------------------- #
class VRDatabase:
    """Gestion de la base de données SQLite pour les métadonnées MP3.
    
        Schéma de la base de données:
        tracks
        ├── id (INTEGER PRIMARY KEY)
        ├── url (TEXT UNIQUE)
        ├── dlna_id (TEXT)
        ├── file_hash (TEXT)  # Hash 8 chars basé sur le nom
        ├── genre (TEXT)
        ├── year (TEXT)
        ├── rating (INTEGER)  # Futur: 0-5 étoiles
        ├── bpm (INTEGER)     # Futur: battements par minute
        ├── added_at (TIMESTAMP)
        └── updated_at (TIMESTAMP)
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, db_path: str = "data/music_metadata.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    # --------------------------------------------------------------------- #
    # Crée les tables dans la base de données (si besoin).
    # --------------------------------------------------------------------- #
    def _init_db(self):
        """Initialise la base de données avec le schéma requis."""
        log.debug("self.db_path %s", self.db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                dlna_id TEXT NOT NULL,
                file_hash TEXT DEFAULT '',
                title TEXT NOT NULL,
                artist TEXT DEFAULT '',
                genre TEXT DEFAULT '',
                year TEXT DEFAULT '',
                rating INTEGER DEFAULT NULL,
                bpm INTEGER DEFAULT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Index pour les requêtes par date et genre
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON tracks(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genre ON tracks(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dlna_id ON tracks(dlna_id)')

        self.conn.commit()
        log.info(f"Base de données initialisée: {self.db_path}")

    # --------------------------------------------------------------------- #
    # Stocke (ou met à jour) une liste de pistes dans la base.
    # --------------------------------------------------------------------- #
    def store_tracks(self, tracks: List[dict]):
        """
        Stocke ou met à jour une liste de pistes dans la base de données.
        Chaque track comporte une URL, un ID, et d'autres metadata.
        
        Args:
            tracks: Liste de dicts avec url, item_id, title, artist, genre, year.
        """
        cursor = self.conn.cursor()

        for track in tracks:
            cursor.execute('''
                INSERT OR REPLACE INTO tracks 
                (url, dlna_id, title, artist, genre, year, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                track['url'],
                track['item_id'],
                track.get('title', '***'),
                track.get('artist', 'artiste inconnu'),
                track.get('genre', ''),
                track.get('year', '')
            ))

        self.conn.commit()
        log.info(f"{len(tracks)} pistes stockées dans la base de données")

    # --------------------------------------------------------------------- #
    # Retourne le nombre de tracks de la base.
    # --------------------------------------------------------------------- #
    def count(self) -> int:
        """
        Retourne le nombre de tracks de la base de données.
        Returns:
            The number of tracks in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tracks')
        result = cursor.fetchone()
        return result[0] if result else 0

    # --------------------------------------------------------------------- #
    # Retourne une liste de MP3 (URL) en fonction de la plage de dates demandée.
    # --------------------------------------------------------------------- #
    def get_track_urls_by_date_range(
            self,
            target_year: int,
            range_start: int,
            range_end: int
    ) -> List[str]:
        """
        Retourne une liste d'URLs basée sur une plage de dates avec comportement circulaire.
        Args :
            target_year : Année de départ (format YYYY)
            range_start : Début de la plage (format YYYY)
            range_end : Fin de la plage (format YYYY)
            
        Returns :
            Liste d'URLs triées selon l'ordre circulaire demandé.
            
        Exemple
            target_year = "1963"
            range_start = "1960"
            range_end = "1969"
            
            Ordre= 1963 → 1964 → ... → 1969 → 1960 → 1961 → 1962 → 1963
        """
        log.debug(f" Cherche l'année {target_year} dans la plage {range_start}-{range_end}")
        cursor = self.conn.cursor()

        # Vérifier que l'année de départ est dans la plage
        if target_year < range_start or target_year > range_end:
            log.warning(f"Année {target_year} hors de la plage {range_start}-{range_end}")
            return []

        # Partie 1 : De target_year à range_end
        part1_query = '''
            SELECT url FROM tracks 
            WHERE year >= ? AND year <= ?
            ORDER BY year ASC, url ASC
        '''
        cursor.execute(part1_query, (target_year, range_end))
        part1 = [row['url'] for row in cursor.fetchall()]

        # Partie 2 : De range_start à target_year (exclue)
        part2_query = '''
            SELECT url FROM tracks 
            WHERE year >= ? AND year < ?
            ORDER BY year ASC, url ASC
        '''
        cursor.execute(part2_query, (range_start, target_year))
        part2 = [row['url'] for row in cursor.fetchall()]

        # Combiner les deux parties
        result = part1 + part2
        log.debug(f"Retourne {len(result)} pistes pour la plage {range_start}-{range_end}, en partant de {target_year}")
        return result

    # --------------------------------------------------------------------- #
    # Retourne toutes les metadata d'une piste en fonction de son ID.
    # --------------------------------------------------------------------- #
    def get_track_info(self, item_id: str) -> Optional[dict]:
        """ ---------------------------------------------------------------------
        None if item not found.
        Returns:
            A dictionary with keys: title, artist, year, genre, rating, bpm.
        --------------------------------------------------------------------- """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tracks WHERE dlna_id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # --------------------------------------------------------------------- #
    # Retourne liste de tracks (url) correspondant au genre demandé.
    # --------------------------------------------------------------------- #
    def get_track_urls_by_genre(self, value: str) -> List[str]:
        """ ---------------------------------------------------------------------
        Returns:
            Une liste de tracks (url) correspondant au genre demandé.
        --------------------------------------------------------------------- """
        cursor = self.conn.cursor()
        query = f"SELECT url FROM tracks WHERE genre='{value}' ORDER BY year ASC"
        cursor.execute(query)
        result = [row['url'] for row in cursor.fetchall()]
        return result

    # --------------------------------------------------------------------- #
    # Renseigne une valeur pour la track donnée.
    # --------------------------------------------------------------------- #
    def update_track(self, url: str, key: str, value: int):
        """Met à jour une valeur."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE tracks SET ? = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE url = ? ''', (key, value, url))
        self.conn.commit()

    # --------------------------------------------------------------------- #
    # Ferme la connexion à la base de données.
    # --------------------------------------------------------------------- #
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
