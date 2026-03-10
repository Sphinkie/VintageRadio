# coding: UTF-8
# ==================================================================
# dlna_network_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_network import DLNANetwork
from lib.dlna_logger import get_logger
from typing import List, Optional

log = get_logger(__name__)


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
        self.didl_container = None
        self.server_control_url = None
        self.music_container_id = None
        self.server_list = None

    # --------------------------------------------------------------------- #
    # On définit le Serveur DLNA à utiliser
    # --------------------------------------------------------------------- #
    def set_server(self, server_ctrl_url: str):
        self.server_control_url = server_ctrl_url

    # --------------------------------------------------------------------- #
    # Find a child container by its title (case‑insensitive)
    # Note : DIDL‑Lite(Digital Item Description Language) is the standard
    # XML schema that DLNA / UPnP servers use to describe the media
    # objects they expose (containers, tracks, images, etc.).
    # --------------------------------------------------------------------- #
    def find_child_id(self, parent_id: str, title: str) -> Optional[str]:
        didl = self.net.browse(self.server_control_url, object_id=parent_id)
        if didl is None:
            return None
        for container in didl.findall('.//{*}container'):
            dc_title = container.find('{*}title')
            if dc_title is not None and dc_title.text and dc_title.text.strip().lower() == title.lower():
                return container.attrib.get('id')
        return None

    # --------------------------------------------------------------------- #
    # Find child Container avec fallback multi-langues
    # --------------------------------------------------------------------- #
    def find_container(self, parent_id, possible_names):
        for name in possible_names:
            print ("test", name)
            child_id = self.find_child_id(parent_id, name)
            if child_id:
                print("found ", name)
                return child_id
        return None

    # --------------------------------------------------------------------- #
    # Détermine l'identifiant du Container MUSIC
    # We assume “Music” is a direct child of the root (Music / Photo / Video).
    # --------------------------------------------------------------------- #
    def find_music_container(self):
        ROOT_ID = "0"
        if self.server_control_url is None: return
        self.music_container_id = self.find_container(ROOT_ID, ["Music", "Musique", "Música", "Musik"])
        if self.music_container_id is None:
            log.fatal("Could not locate a 'Music' container on the server.")

    # --------------------------------------------------------------------- #
    # Demande la liste des infos MP3 d'un container.
    # --------------------------------------------------------------------- #
    def get_file_urls(self, container_id: str):
        self.didl_container = self.net.browse(self.server_control_url, object_id=container_id)
        log.debug("Container content: %s", self.didl_container)
        if self.didl_container is None:
            log.fatal(f"Failed to browse the container {container_id}.")

    # --------------------------------------------------------------------- #
    # Demande la liste des URL des MP3 d'un container.
    # --------------------------------------------------------------------- #
    def get_mp3_items(self) -> List[str]:
        return self.net.extract_mp3_items(self.didl_container)

    # --------------------------------------------------------------------- #
    # Transforme une "Description URL" en "ContentDirectory Control URL"
    # --------------------------------------------------------------------- #
    @staticmethod
    def resolve_control(url: str) -> Optional[str]:
        return DLNANetwork.get_content_directory_control_url(url)

    # --------------------------------------------------------------------- #
    # Demande au reseau de rechercher la liste des serveurs DLNA disponibles.
    # --------------------------------------------------------------------- #
    def discover_servers(self):
        self.server_list = self.net.discover_servers()

    # --------------------------------------------------------------------- #
    # Si le serveur préféré est dans la liste des serveurs découverts, il est sélectionné.
    # Sinon l'utilisateur en choisit un.
    # La fonction retourne l'url du serveur s'il faut le mémoriser dans les nouvelles préférences.
    # --------------------------------------------------------------------- #
    def choose_server(self, preferred_server_url: str):
        server_control_url: Optional[str] = None
        if self.server_list is None:
            print("No DLNA servers were discovered on the LAN.")
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
                print("No server selected – exiting.")
                return
            server_control_url = DLNAWrapper.resolve_control(chosen_server)
            if not server_control_url:
                print("Chosen server does not expose a ContentDirectory service.")
                return
            return chosen_server

    # --------------------------------------------------------------------- #
    # Helper to turn a human‑readable server description into a control URL
    # --------------------------------------------------------------------- #
    def pick_server_interactively(self) -> Optional[str]:
        """
        Show a numbered list of discovered servers (showing just the host part)
        and ask the user to choose one.  Returns the selected *control URL*.
        """
        if not self.server_list:
            print("No DLNA server found on the local network.")
            return None

        print("\nDiscovered DLNA MediaServers:")
        for idx, (desc_url, usn) in enumerate(self.server_list, start=1):
            host = desc_url.split("/", 3)[2]  # crude host extraction
            print(f"[{idx}] {host}")

        while True:
            choice = input(f"Select a server (1‑{len(self.server_list)} or press Enter to abort): ")
            if not choice:
                return None
            if choice.isdigit():
                i = int(choice)
                if 1 <= i <= len(self.server_list):
                    return self.server_list[i - 1][0]  # return the description URL
            print("Invalid selection – try again.")
