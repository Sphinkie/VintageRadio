# coding: UTF-8
# ==================================================================
# lib.dlna_network_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_network import DLNANetwork
from lib.user_display import Display
from lib.dlna_logger import get_logger
from lib.dlna_db import DLNADatabase
from lib.tag_collector import get_mp3_tags
from typing import List, Optional
import xml.etree.ElementTree as ET

log = get_logger(__name__)
ROOT_ID = "0"


# ----------------------------------------------------------------------- #
# Cette classe encapsule les requetes HTTP au serveur DLNA.
# ----------------------------------------------------------------------- #
class DLNAWrapper:

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.net = DLNANetwork()
        self.db = DLNADatabase()  
        self.didl_container = None
        self.server_control_url = None
        self.music_container_id = None
        self.latest_container_id = None
        self.server_list = None

    # --------------------------------------------------------------------- #
    # On définit le Serveur DLNA à utiliser
    # --------------------------------------------------------------------- #
    def set_server(self, server_ctrl_url: str):
        self.server_control_url = server_ctrl_url

    # --------------------------------------------------------------------- #
    # Détermine l'identifiant du Container MUSIC
    # We assume “Music” is a direct child of the root (Music / Photo / Video).
    # --------------------------------------------------------------------- #
    def find_music_container(self) -> Optional[str]:
        if self.server_control_url is None: return None
        self.music_container_id = self.find_container(ROOT_ID, ["Music", "Musique", "Música", "Musik"])
        if self.music_container_id is None:
            log.fatal("Could not locate a 'Music' container on the server.")
            return None
        return self.music_container_id

    # --------------------------------------------------------------------- #
    # Find child Container avec fallback multi-langues
    # --------------------------------------------------------------------- #
    def find_container(self, parent_id, possible_names):
        for name in possible_names:
            child_id = self.find_child_id(parent_id, name)
            if child_id:
                return child_id
        return None

    # --------------------------------------------------------------------- #
    # Find a child container by its title (case‑insensitive)
    # Note : DIDL‑Lite(Digital Item Description Language) is the standard
    # XML schema that DLNA / UPnP servers use to describe the media
    # objects they expose (containers, tracks, images, etc.).
    # --------------------------------------------------------------------- #
    def find_child_id(self, parent_id: str, title: str) -> Optional[str]:
        didl = self.net.browse(self.server_control_url, object_id=parent_id)
        if didl is None:
            log.warning("didl is none")
            return None
        for container in didl.findall('.//{*}container'):
            dc_title = container.find('{*}title')
            if dc_title is not None and dc_title.text and dc_title.text.strip().lower() == title.lower():
                self.latest_container_id = container.attrib.get('id')
                return self.latest_container_id
        return None

    # --------------------------------------------------------------------- #
    # Demande la liste des infos MP3 d'un container.
    # --------------------------------------------------------------------- #
    def get_file_urls(self, container_id: str):
        self.didl_container = self.net.browse(self.server_control_url, object_id=container_id)
        log.debug("Container content: %s", self.didl_container)
        if self.didl_container is None:
            log.fatal(f"Failed to browse the container {container_id}.")

    # --------------------------------------------------------------------- #
    # Retourne des infos sur le clip demandé.
    # --------------------------------------------------------------------- #
    def get_clip_info(self, item_id: str) -> Optional[tuple]:
        """
        Extract metadata from a DIDL-Lite item element.
        
        Args:
            item_id: The ID of the item to look up
            
        Returns:
            Tuple of (title, artist, date, genre)
            Empty strings if field is missing
            None if item not found
        """    
        item_full_id = self.latest_container_id + "$@" + item_id
        log.debug("Searching for item id: %s", item_full_id)
        for items in self.didl_container.findall('.//{*}item'):
                id = items.attrib.get('id', '')
                if id == item_full_id:
                    # Found the item - extract metadata fields
                    title = self._extract_field(items, '{*}title')
                    artist = self._extract_field(items, '{*}creator')
                    date = self._extract_field(items, '{*}date').split('-')[0]
                    genre = self._extract_field(items, '{*}genre')                   
                    log.debug("Clip found")
                    return (title, artist, date, genre)
        # Not found
        return None

    # --------------------------------------------------------------------- #
    # Demande la liste des URL des MP3 du DIDL container.
    # --------------------------------------------------------------------- #
    def get_mp3_items(self) -> List[str]:
        """
        Walk a DIDL-Lite tree and return the list of URLs
        for items whose `@protocolInfo` indicates an audio/mpeg (MP3) resource.
        """
        mp3_urls: List[str] = []
        # Namespace used by most DLNA servers for DIDL‑Lite
        ns = {"didl": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"}
        for items in self.didl_container.findall('.//{*}item'):
            for res in items.findall('{*}res'):
                protocol = res.attrib.get('protocolInfo', '')
                if 'audio/mpeg' in protocol.lower():
                    if res.text:
                        mp3_urls.append(res.text.strip())
        return mp3_urls

    # --------------------------------------------------------------------- #
    # Helper to extract a field from DIDL-Lite XML
    # --------------------------------------------------------------------- #
    def _extract_field(self, element: ET.Element, tag_name: str) -> str:
        """
        Safely extract text content from an XML element.
        
        Args:
            element: The parent XML element
            tag_name: The tag to search for (supports wildcard namespace {*})
            
        Returns:
            Text content or empty string if not found
        """
        field = element.find(tag_name)
        if field is not None and field.text:
            return field.text.strip()
        return ""
    
    # --------------------------------------------------------------------- #
    # Transforme une "Description URL" en "ContentDirectory Control URL"
    # --------------------------------------------------------------------- #
    @staticmethod
    def resolve_control(url: str) -> Optional[str]:
        return DLNANetwork.get_content_directory_control_url(url)

    # --------------------------------------------------------------------- #
    # Demande au réseau de rechercher la liste des serveurs DLNA disponibles.
    # --------------------------------------------------------------------- #
    def discover_servers(self):
        self.server_list = self.net.discover_servers()
        # Affichage des hostnames dans le log
        for (desc_url, usn) in self.server_list:
            host = desc_url.split("/", 3)[2]  # hostname extraction
            log.info("> %s",host)

    # --------------------------------------------------------------------- #
    # Si le serveur préféré est dans la liste des serveurs découverts, il est sélectionné.
    # Sinon l'utilisateur en choisit un.
    # La fonction retourne la Description URL du serveur pour le mémoriser dans les préférences.
    # --------------------------------------------------------------------- #
    def choose_server(self, preferred_server_url: str):
        server_control_url: Optional[str] = None
        if self.server_list is None:
            Display.warning("No DLNA servers were discovered on the LAN.")
            return

        # If the user answered a server that matches the saved one, reuse it; otherwise ask.
        if preferred_server_url:
            # Look for the same description URL among the fresh results
            matching = [s for s in self.server_list if s[0] == preferred_server_url]
            if matching:
                server_control_url = DLNAWrapper.resolve_control(matching[0][0])
        if not server_control_url:
            # Ask the user which server to use
            chosen_server = self.pick_server_interactively()
            if not chosen_server:
                log.fatal("No server selected – exiting.")
                return
            server_control_url = DLNAWrapper.resolve_control(chosen_server)
            if not server_control_url:
                log.fatal("Chosen server does not expose a ContentDirectory service.")
                return
            return chosen_server

    # --------------------------------------------------------------------- #
    # Affiche le menu de choix du server DLNA parmi ceux qui ont été
    # trouvé, et demande à l'utilisateur d'en choisir un.
    # Retourne l'URL choisie (ou None).
    # --------------------------------------------------------------------- #
    def pick_server_interactively(self) -> Optional[str]:
        """
        Show a numbered list of discovered servers (showing just the host part)
        and ask the user to choose one.  Returns the selected *control URL*.
        """
        if not self.server_list:
            Display.warning("No DLNA server found on the local network.")
            return None

        Display.flush()
        Display.add_line("Discovered DLNA MediaServers:")
        for idx, (desc_url, usn) in enumerate(self.server_list, start=1):
            host = desc_url.split("/", 3)[2]  # crude host extraction
            Display.add_line(f"[{idx}] {host}")

        while True:
            choice = Display.input(f"Select a server (1‑{len(self.server_list)} or press Enter to abort): ")
            if not choice:
                return None
            if choice.isdigit():
                i = int(choice)
                if 1 <= i <= len(self.server_list):
                    return self.server_list[i - 1][0]  # return the Description URL
            Display.warning("Invalid selection – try again.")

    # --------------------------------------------------------------------- #
    # Télécharge le début du MP3 et extrait Beat et Rating
    # --------------------------------------------------------------------- #
    def get_track_details(self, url: str) -> dict:
        """
        Fetches detailed mp3 metadata including BPM and Rating.
        """
        bpm, rating = get_mp3_tags(url)
        return {
            'url': url,
            'bpm': bpm,
            'rating': rating,
        }

    # --------------------------------------------------------------------- #
    # Récupérer TOUS les MP3 et les stocker dans la base.
    # --------------------------------------------------------------------- #
    def scan_all_mp3_to_db(self):
        """
        Scan le serveur DLNA en priorité via "All Music",
        avec fallback récursif si nécessaire.
        """

        if self.server_control_url is None:
            log.fatal("Aucun serveur DLNA défini")
            return 0

        # --------------------------------------------------------------------- #
        # Chercher le contenu du container "All Music"
        # --------------------------------------------------------------------- #
        log.info("Recherche du container 'All Music'...")
        # On cherche le container "All Music"
        all_music_container_id = self.find_container(self.music_container_id, ["All Music", "All Tracks", "Toutes les musiques"])
        # On recupère toutes ses URLs de MP3 dans un XML
        if all_music_container_id:
            log.info(f"Container 'All Music' found : {all_music_container_id}")
            xml_tracks = self.net.browse(self.server_control_url, object_id=all_music_container_id)
            all_tracks = self.extract_all_mp3_from_didl(xml_tracks)
        else:
            # --------------------------------------------------------------------- #
            # Fallback: parcours récursif complet
            # --------------------------------------------------------------------- #
            log.warning("Container 'All Music' non trouvé, utilisation du parcours récursif...")
            xml_tracks = self.net.browse_recursive(self.server_control_url, object_id="0")
            all_tracks = self.extract_all_mp3_from_didl(xml_tracks)

        if not all_tracks:
            log.warning("Aucune piste MP3 trouvée sur le serveur")
            return 0
        # --------------------------------------------------------------------- #
        # On stocke le résultat dans la base de données
        # --------------------------------------------------------------------- #
        self.db.store_tracks(all_tracks)
        log.info(f"Scan terminé: {len(all_tracks)} pistes trouvées")
        return len(all_tracks)


    # --------------------------------------------------------------------- #
    # Retourner une liste d'URLs basée sur la date et la plage
    # --------------------------------------------------------------------- #
    def get_urls_by_date_range(
        self, 
        target_year: int,
        range_start: int,
        range_end: int
    ) -> List[str]:
        """
        Retourne une liste d'URLs filtrée par plage de dates avec ordre circulaire.
        
        Args:
            target_date: Date de départ (ex : 1964)
            range_start: Année de début de plage (ex : 1960)
            range_end: Année de fin de plage (ex : 1969)
            
        Returns:
            Liste d'URLs triées selon l'ordre circulaire
        """
        return self.db.get_tracks_by_date_range(target_year, range_start, range_end)

    # --------------------------------------------------------------------- #
    # Nettoyer la base de données à la fermeture
    # --------------------------------------------------------------------- #
    def close(self):
        """Ferme les ressources (base de données)."""
        self.db.close()

    # --------------------------------------------------------------------- #
    # Extrait tous les MP3 d'une réponse DIDL-Lite (flat list)
    # --------------------------------------------------------------------- #
    def extract_all_mp3_from_didl(self, didl_root: ET.Element) -> List[dict]:
        """
        Extrait toutes les pistes MP3 d'un élément DIDL-Lite avec métadonnées complètes.

        Args:
            didl_root: L'élément racine DIDL-Lite (résultat de self.browse())

        Returns:
            Liste de dicts avec: url, genre, year, filename, title, artist
        """
        mp3_tracks = []

        if didl_root is None:
            return mp3_tracks

        for item in didl_root.findall('.//{*}item'):
            # Extraire l'ID de l'item
            item_id = item.attrib.get('id', '')

            # Extraire les métadonnées de base
            title = self._extract_text(item, '{*}title')
            artist = self._extract_text(item, '{*}creator')
            album = self._extract_text(item, '{*}album')
            genre = self._extract_text(item, '{*}genre')
            date = self._extract_text(item, '{*}date')

            # Extraire l'URL du premier res audio/mpeg
            url = None
            for res in item.findall('{*}res'):
                protocol = res.attrib.get('protocolInfo', '')
                if 'audio/mpeg' in protocol.lower() and res.text:
                    url = res.text.strip()
                    break

            if url:
                # Extraire le nom de fichier de l'URL
                filename = url.split('/')[-1].split('?')[0]

                mp3_tracks.append({
                    'url': url,
                    'filename': filename,
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'genre': genre,
                    'year': date,
                    'item_id': item_id
                })

        log.debug(f"Extrait {len(mp3_tracks)} pistes MP3 du container DIDL")
        return mp3_tracks

    # --------------------------------------------------------------------- #
    # Helper pour extraire du texte d'un élément XML
    # --------------------------------------------------------------------- #
    @staticmethod
    def _extract_text(element: ET.Element, tag_name: str) -> str:
        """Extrait le texte d'un élément XML, retourne chaîne vide si absent."""
        field = element.find(tag_name)
        if field is not None and field.text:
            return field.text.strip()
        return ''


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
if __name__ == "__main__":
    wrapper = DLNAWrapper()
    wrapper.set_server("http://192.168.0.101:50001/ContentDirectory/control")
    # Trouver "All Music"
    music_ctnr_id = wrapper.find_music_container()
    all_music_ctnr_id = wrapper.find_container(music_ctnr_id, ["All music"])
    print("all_music_id: ", all_music_ctnr_id)

    # -------------------------------------------------------------
    # TEST DE SCAN DE 'ALL MUSIC'
    # -------------------------------------------------------------
    if all_music_ctnr_id:
        didl = wrapper.net.browse(wrapper.server_control_url, object_id=all_music_ctnr_id)
        tracks = wrapper.extract_all_mp3_from_didl(didl)
        print(f"Trouvé {len(tracks)} pistes")
        # Afficher les 5 premières pistes
        for t in tracks[:5]:
            print(f"  {t['title']} - {t['artist']} ({t['year'][:4]})")

    # -------------------------------------------------------------
    # TEST DE REMPLISSAGE DE LA BDD (1468 tracks : 2 secondes)
    # -------------------------------------------------------------
    # Scanner tout le serveur et remplir la base de données
    print("Scanning DLNA server for all MP3s...")
    total_tracks = wrapper.scan_all_mp3_to_db()
    print(f"Found {total_tracks} tracks")

    # -------------------------------------------------------------
    # TEST DE LISTE DES FIFTIES
    # -------------------------------------------------------------
    # Récupérer une liste basée sur la date
    urls = wrapper.get_urls_by_date_range(1955, 1950, 1959)
    print(f"Retrieved {len(urls)} URLs for date range {1950}-{1959}")
