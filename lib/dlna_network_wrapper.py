# coding: UTF-8
# ==================================================================
# lib.dlna_network_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_network import DLNANetwork
from lib.user_display import Display
from lib.vr_logger import get_logger
from lib.tag_collector import get_track_tags
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
        self.server_list = None
        self.didl_container = None
        self.server_control_url = None
        self.music_container_id = None
        self.latest_container_id = None

    # --------------------------------------------------------------------- #
    # Demande au réseau de rechercher la liste des serveurs DLNA disponibles.
    # --------------------------------------------------------------------- #
    def discover_servers(self):
        """Demande au réseau de rechercher la liste des serveurs DLNA disponibles."""
        self.server_list = self.net.discover_servers()
        # Affichage des hostnames dans le log
        for (desc_url, usn) in self.server_list:
            host = desc_url.split("/", 3)[2]  # hostname extraction
            log.info("> %s", host)

    # --------------------------------------------------------------------- #
    # Définit le Serveur DLNA à utiliser.
    # --------------------------------------------------------------------- #
    def set_server(self, server_ctrl_url: str):
        """Définit le Serveur DLNA à utiliser."""
        self.server_control_url = server_ctrl_url

    # --------------------------------------------------------------------- #
    # Transforme une "Description URL" en "ContentDirectory Control URL"
    # --------------------------------------------------------------------- #
    @staticmethod
    def resolve_control(url: str) -> Optional[str]:
        """        
        Args :
            url : La 'Description URL' du serveur DLNA.
        Returns :
            La 'Control URL' du serveur DLNA (ContentDirectory).
        """
        return DLNANetwork.get_content_directory_control_url(url)

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
    # Cherche un Child-Conteneur parmi une liste de noms (multi-langues).
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
    # Demande au serveur DLNA la liste des fichiers MP3 d'un conteneur.
    # La liste est mise dans le DIDL courant.
    # --------------------------------------------------------------------- #
    def get_container_content(self, container_id: str):
        self.didl_container = self.net.browse(self.server_control_url, object_id=container_id)
        log.debug("Container content: %s", self.didl_container)
        if self.didl_container is None:
            log.fatal(f"Failed to browse the container {container_id}.")

    # --------------------------------------------------------------------- #
    # Retourne des infos sur le clip demandé, en les cherchant dans le DIDL
    # du dernier conteneur mémorisé.
    # --------------------------------------------------------------------- #
    def get_clip_info(self, item_id: str) -> Optional[tuple]:
        """
        Extract metadata from a DIDL-Lite item element.
        
        Args:
            item_id: The ID of the item to look up. Ex:2913
            
        Returns:
            Tuple of (title, artist, year, genre)
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
                year = self._extract_field(items, '{*}date').split('-')[0]
                genre = self._extract_field(items, '{*}genre')
                log.debug("Clip found")
                return title, artist, year, genre
        # Not found
        return None

    # --------------------------------------------------------------------- #
    # Extrait la liste des URL des MP3 du DIDL courant.
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
    # Si le serveur préféré est dans la liste des serveurs découverts, il est sélectionné.
    # Sinon l'utilisateur en choisit un.
    # La fonction retourne la Description URL du serveur pour le mémoriser dans les préférences.
    # --------------------------------------------------------------------- #
    def choose_server(self, preferred_server_url: str) -> Optional[str]:
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
            chosen_server = Display.pick_server_interactively(self.server_list)
            if not chosen_server:
                log.fatal("No server selected – exiting.")
                return
            server_control_url = DLNAWrapper.resolve_control(chosen_server)
            if not server_control_url:
                log.fatal("Chosen server does not expose a ContentDirectory service.")
                return
            return chosen_server

    # --------------------------------------------------------------------- #
    # Télécharge le début du MP3 et extrait Beat et Rating avec le
    # tag_collector.
    # --------------------------------------------------------------------- #
    def get_track_details(self, url: str) -> dict:
        """
        Fetches detailed mp3 metadata including BPM and Rating.
        """
        bpm, rating = get_track_tags(url)
        return {
            'url': url,
            'bpm': bpm,
            'rating': rating,
        }

    # --------------------------------------------------------------------- #
    # Retourne TOUS les MP3 du serveur DLNA.
    # --------------------------------------------------------------------- #
    def scan_all_mp3(self) -> List[dict]:
        """
        Scanne le serveur DLNA en priorité via "All Music",
        puis, en fallback, en mode récursif si nécessaire.
        """

        if self.server_control_url is None:
            log.fatal("Aucun serveur DLNA défini")
            return []

        if self.music_container_id is None:
            self.find_music_container()
        # --------------------------------------------------------------------- #
        # Chercher le contenu du container "All Music"
        # --------------------------------------------------------------------- #
        log.info("Recherche du container 'All Music'...")
        # On cherche le container "All Music"
        all_music_container_id = self.find_container(self.music_container_id,
                                                     ["All Music", "All Tracks", "Toutes les musiques"])
        # On recupère toutes ses URLs de MP3 dans un XML
        if all_music_container_id:
            log.info(f"Container 'All Music' found with id {all_music_container_id}.")
            xml_tracks = self.net.browse(self.server_control_url, object_id=all_music_container_id)
            all_tracks = self.extract_all_mp3_from_didl(xml_tracks)
        else:
            # --------------------------------------------------------------------- #
            # Fallback: parcours récursif complet (40 secondes !)
            # --------------------------------------------------------------------- #
            log.warning("Container 'All Music' non trouvé, utilisation du parcours récursif...")
            xml_tracks = self.net.browse_recursive(self.server_control_url, object_id=self.music_container_id)
            all_tracks = self.extract_all_mp3_from_didl(xml_tracks)

        if not all_tracks:
            log.warning("Aucune piste MP3 trouvée sur le serveur")
            return []

        return all_tracks

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
            full_id = item.attrib.get('id', '')  # ex: id="28$2857$@2913"
            # Extraire les métadonnées de base
            title = self._extract_field(item, '{*}title')
            artist = self._extract_field(item, '{*}creator')
            genre = self._extract_field(item, '{*}genre')
            date = self._extract_field(item, '{*}date')

            # Extraire l'URL du premier res audio/mpeg
            url = None
            for res in item.findall('{*}res'):
                protocol = res.attrib.get('protocolInfo', '')
                if 'audio/mpeg' in protocol.lower() and res.text:
                    url = res.text.strip()
                    break

            if url:
                mp3_tracks.append({
                    'url': url,
                    'item_id': full_id.split('@')[-1],
                    'title': title,
                    'artist': artist,
                    'genre': genre,
                    'year': date.split('-')[0]
                })

        log.debug(f"Extrait {len(mp3_tracks)} pistes MP3 du container DIDL")
        return mp3_tracks

    # --------------------------------------------------------------------- #
    # Helper pour extraire un field du DIDL-Lite XML
    # --------------------------------------------------------------------- #
    @staticmethod
    def _extract_field(element: ET.Element, tag_name: str) -> str:
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
    # TEST DE SCAN du serveur DLNA (1468 tracks : 2 secondes)
    # -------------------------------------------------------------
    # Scanner tout le serveur et remplir la base de données
    print("Scanning DLNA server for all MP3s...")
    tracks = wrapper.scan_all_mp3()
    print(f"Found {len(tracks)} tracks")
