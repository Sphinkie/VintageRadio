# coding: UTF-8
# ==================================================================
# lib/dlna_db.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import sqlite3
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime
from lib.dlna_logger import get_logger

log = get_logger(__name__)


# --------------------------------------------------------------------- #
# Gestion de la base de données SQLite pour les métadonnées MP3.
# --------------------------------------------------------------------- #
class DLNADatabase:
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
    def __init__(self, db_path: str = "music_metadata.db"):
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

    # --------------------------------------------------------------------- #
    # Stocke (ou met à jour) une liste de pistes dans la base.
    # --------------------------------------------------------------------- #
    def store_tracks(self, tracks: List[dict]):
        """
        Stocke ou met à jour une liste de pistes dans la base.
        
        Args:
            tracks: Liste de dicts avec url, dlna_id, genre, year
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
    # Retourne une liste de MP3 (URL) en fonction de la plage de dates demandée.
    # --------------------------------------------------------------------- #
    def get_tracks_by_date_range(
            self,
            target_year: int,
            range_start: int,
            range_end: int
    ) -> List[str]:
        """
        Retourne une liste d'URLs basée sur une plage de dates avec comportement circulaire.
        
        Args:
            target_year: Année de départ (format YYYY)
            range_start: Début de la plage (format YYYY)
            range_end: Fin de la plage (format YYYY)
            
        Returns:
            Liste d'URLs triées selon l'ordre circulaire demandé
            
        Exemple
            target_year = "1963"
            range_start = "1960"
            range_end = "1969"
            
            Ordre= 1963 → 1964 → ... → 1969 → 1960 → 1961 → 1962 → 1963
        """
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
        log.debug(f"Retourné {len(result)} pistes pour la plage {range_start}-{range_end}, en partant de {target_year}")
        return result

    # --------------------------------------------------------------------- #
    # Retourne le nombre de clips de la base.
    # --------------------------------------------------------------------- #
    def count(self) -> int:
        """Retourne le nombre de clips de la base."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tracks')
        result = cursor.fetchone()
        return result[0] if result else 0

    # --------------------------------------------------------------------- #
    # Retourne toutes les metadata d'une piste en fonction de son ID.
    # --------------------------------------------------------------------- #
    def get_track_info(self, item_id: str) -> Optional[dict]:
        """
        Retourne les informations complètes d'une piste.
        Returns:
            A dictionnary with keys: title, artist, year, genre, rating, bpm
            None if item not found
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tracks WHERE dlna_id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # --------------------------------------------------------------------- #
    # Retourne une liste de d'url.
    # --------------------------------------------------------------------- #
    def select_url(self, key:str, value:str) -> List[str]:
        cursor = self.conn.cursor()
        query = '''
            SELECT url FROM tracks 
            WHERE ? = ?
            ORDER BY year ASC
        '''
        cursor.execute(query, (key, value))
        return [row['url'] for row in cursor.fetchall()]

    # --------------------------------------------------------------------- #
    # Renseigne une valeur pour la piste donnée.
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


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
if __name__ == "__main__":
    # -------------------------------------------------------------
    # TEST DU HASHAGE
    # -------------------------------------------------------------
    filename = "Aretha Franklin - I will Survive.mp3"
    hash1 = DLNADatabase.calculate_file_hash(filename)  # Ex: "D6DC212A"
    print(hash1)

    filename = "Blue Steel & His Orchestra - Sugar Babe, I'm Leavin'!.mp3"
    hash2 = DLNADatabase.calculate_file_hash(filename)  # Ex: "16B19780"
    print(hash2)
