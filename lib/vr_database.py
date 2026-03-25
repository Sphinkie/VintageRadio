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
    
        Schéma de la base de données.
        tracks
        ├── id (INTEGER PRIMARY KEY)
        ├── url (TEXT UNIQUE)
        ├── dlna_id (TEXT UNIQUE)
        ├── file_hash (TEXT)  # Hash 8 chars basé sur le nom
        ├── genre (TEXT)
        ├── year (TEXT)
        ├── rating (INTEGER)  # 0-5 étoiles
        ├── bpm (REAL)        # battements par minute (beat)
        ├── added_at (TIMESTAMP)
        └── updated_at (TIMESTAMP)
    """

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def __init__(self, db_path: str = "data/music_metadata.db"):
        """
        Constructeur
        :param db_path: Le chemin et le nom de la base de données.
        """
        self.db_path = db_path
        self.conn = None
        self._init_db()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def _init_db(self):
        """
        Crée les tables dans la base de données (si besoin).
        Initialise la base de données avec le schéma requis.
        """
        log.debug("self.db_path %s", self.db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                dlna_id TEXT UNIQUE NOT NULL ,
                file_hash TEXT DEFAULT '',
                title  TEXT NOT NULL,
                artist TEXT DEFAULT '',
                genre  TEXT DEFAULT '',
                year   TEXT DEFAULT '',
                rating INTEGER DEFAULT NULL,
                bpm    REAL DEFAULT NULL,
                added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Index pour les requêtes par date et genre
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON tracks(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genre ON tracks(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dlna_id ON tracks(dlna_id)')

        self.conn.commit()
        version = cursor.execute("SELECT sqlite_version();").fetchone()[0]
        log.info(f"BSQLite version: {version}")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def store_tracks(self, tracks: List[dict]):
        """
        Stocke ou met à jour une liste de pistes dans la base de données.
        Chaque track comporte une URL, un ID, et d'autres metadata.
        :param tracks: Liste de dicts avec url, item_id, title, artist, genre, year.
        """
        cursor = self.conn.cursor()
        for track in tracks:
            # Pour faire INSERT IF EXISTS, on utilise la syntaxe particulière du "ON CONFLICT" (UPSERT).
            # Nécessite SQLite en version > 3.24
            query = '''
                INSERT INTO tracks(url, dlna_id, title, artist, genre, year, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(dlna_id) DO UPDATE 
                   SET artist = excluded.artist, genre = excluded.genre
            '''
            # cursor.executemany(query, tracks)
            old_query = '''INSERT INTO tracks(url, dlna_id, title, artist, genre, year, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP) '''
            cursor.execute(query, (
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
    # --------------------------------------------------------------------- #
    def count(self) -> int:
        """
        Retourne le nombre de tracks de la base de données.
        :returns: The number of tracks in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tracks')
        result = cursor.fetchone()
        return result[0] if result else 0

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_track_urls(self) -> List[str]:
        """
        Retourne la liste de toutes les tracks (url)..
        :returns: Une liste d'URLs de tracks.
        """
        cursor = self.conn.cursor()
        query = f"SELECT url FROM tracks ORDER BY id ASC"
        cursor.execute(query)
        result = [row['url'] for row in cursor.fetchall()]
        return result

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_track_urls_by_bpm(self, value: Optional[float], direction: Optional[str]) -> List[str]:
        """
        Retourne liste de tracks (url) correspondant au Beat demandé.
        :param value: Une valeur de BeatPerMinute (pouvant être None).
        :param direction: "asc" ou "desc" ou "None" (= valeur stricte).
        :returns: Une liste d'URLs de tracks.
        """
        cursor = self.conn.cursor()
        if value is None:
            query = f"SELECT url FROM tracks WHERE bpm IS NULL"
        elif direction == "asc":
            query = f"SELECT url FROM tracks WHERE bpm >= {value} ORDER BY bmp ASC"
        elif direction == "desc":
            query = f"SELECT url FROM tracks WHERE bpm <= {value} ORDER BY bmp DESC"
        else: # direction is None:
            query = f"SELECT url FROM tracks WHERE bpm = {value}"
        cursor.execute(query)
        result = [row['url'] for row in cursor.fetchall()]
        # print(result[:5])
        return result

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_track_urls_by_genre(self, value: str) -> List[str]:
        """
        Retourne la liste des tracks correspondant au Genre demandé.
        :return: Une liste d'urls correspondant au Genre demandé.
        """
        cursor = self.conn.cursor()
        query = f"SELECT url FROM tracks WHERE genre='{value}' ORDER BY year ASC"
        cursor.execute(query)
        result = [row['url'] for row in cursor.fetchall()]
        return result

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
        :param target_year: Année de départ (format YYYY)
        :param range_start: Début de la plage (format YYYY)
        :param range_end: Fin de la plage (format YYYY)
        :returns: Liste d'URLs triées selon l'ordre circulaire demandé.
            
        Exemple
         - target_year = "1963"
         - range_start = "1960"
         - range_end = "1969"
         - Donne l'ordre suivant = 1963 → 1964 → ... → 1969 → 1960 → 1961 → 1962 → 1963
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
            ORDER BY year ASC, RANDOM();
        '''
        cursor.execute(part1_query, (target_year, range_end))
        part1 = [row['url'] for row in cursor.fetchall()]

        # Partie 2 : De range_start à target_year (non incluse)
        part2_query = '''
            SELECT url FROM tracks 
            WHERE year >= ? AND year < ?
            ORDER BY year ASC, RANDOM();
        '''
        cursor.execute(part2_query, (range_start, target_year))
        part2 = [row['url'] for row in cursor.fetchall()]

        # Combiner les deux parties
        result = part1 + part2
        log.debug(f"Retourne {len(result)} pistes pour la plage {range_start}-{range_end}, en partant de {target_year}")
        return result

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_track_info(self, item_id: str) -> Optional[dict]:
        """
        Retourne toutes les metadata d'une piste en fonction de son ID.
        :returns:
            A dictionary with keys: title, artist, year, genre, rating, bpm.
            None if item not found.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tracks WHERE dlna_id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def update_track(self, url: str, key: str, value: int):
        """
        Met à jour une valeur pour la track donnée dans la base de données.
        :param url: URL de la track à modifier.
        :param key: Nom de la colonne.
        :param value: Valeur à modifier.
        """
        if value is None: return
        cursor = self.conn.cursor()
        query = f"UPDATE tracks SET {key}={value}, updated_at = CURRENT_TIMESTAMP WHERE url='{url}' "
        cursor.execute(query)
        self.conn.commit()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def drop(self):
        """Supprime la base de données."""
        if self.conn:
            self.conn.close()
        # TODO