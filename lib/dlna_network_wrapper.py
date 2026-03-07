# coding: UTF-8
# ==================================================================
# dlna_network_wrapper.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_network import DLNANetwork
from typing import List, Optional


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

    # --------------------------------------------------------------------- #
    # On définit le Serveur DLNA à utiliser
    # --------------------------------------------------------------------- #
    def set_server(self, server_ctrl_url: str):
        self.server_control_url = server_ctrl_url

    # --------------------------------------------------------------------- #
    # Helper to find a child container by its title (case‑insensitive)
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
    # Demande au reseau de rechercher la liste des serveurs DLNA disponibles.
    # --------------------------------------------------------------------- #
    def discover_servers(self):
        self.net.discover_servers()

    # --------------------------------------------------------------------- #
    # Demande la liste des fichiers MP3 d'un container.
    # --------------------------------------------------------------------- #
    def get_file_urls(self, container_id: str):
        self.didl_container = self.net.browse(self.server_control_url, object_id=container_id)
        print(f"\nContainer content:\n",self.didl_container)
        if self.didl_container is None:
            print(f"Failed to browse the container {container_id}.")

    # --------------------------------------------------------------------- #
    # Demande la liste des fichiers MP3 d'un container.
    # --------------------------------------------------------------------- #
    def get_mp3_items(self) -> List[str]:
        return self.net.extract_mp3_items(self.didl_container)
