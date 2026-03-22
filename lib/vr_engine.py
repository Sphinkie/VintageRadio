# coding: UTF-8
# ==================================================================
# lib.vr_engine.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import asyncio
from typing import List, Optional
from lib.user_display import Display
from lib.user_preferences import load_preferred_server, save_preferred_server
from lib.vr_logger import get_logger
from lib.vr_database_wrapper import DBWrapper
from lib.dlna_network_wrapper import DLNAWrapper

log = get_logger(__name__)


# ----------------------------------------------------------------------- #
# Cette classe de haut niveau coordonne la gestion de la base de données
# et du serveur DLNA.
# ----------------------------------------------------------------------- #
class VREngine:

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.db_w = DBWrapper("./data/music_metadata.db")
        self.net_wrapper = DLNAWrapper()
        display = Display('tty')
        display.show("VINTAGE RADIO")

    # --------------------------------------------------------------------- #
    # Nettoyer la base de données à la fermeture
    # --------------------------------------------------------------------- #
    def close(self):
        """Ferme les ressources (base de données)."""
        self.db_w.close()

    # --------------------------------------------------------------------- #
    # On est prêt si on a établi une liaison avec un serveur DLNA.
    # --------------------------------------------------------------------- #
    def ready(self) -> bool:
        return self.net_wrapper.server_control_url is not None

    # --------------------------------------------------------------------- #
    # Cherche le server DLNA. Il est mémorisé dans le network_wrapper.
    # --------------------------------------------------------------------- #
    def get_dlna_server(self):
        # -----------------------------------------------------------------
        # Try to load a previously saved server
        # -----------------------------------------------------------------
        server_control_url: Optional[str] = None
        preferred_server_desc_url = load_preferred_server()
        log.info("preferred server url: %s", preferred_server_desc_url)
        # -----------------------------------------------------------------
        # If we have a saved description URL, verify that it is still reachable
        # -----------------------------------------------------------------
        if preferred_server_desc_url:
            log.debug(f"Trying previously saved server: {preferred_server_desc_url}")
            preferred_server_ctrl_url = DLNAWrapper.resolve_control(preferred_server_desc_url)
            if preferred_server_ctrl_url:
                server_control_url = preferred_server_ctrl_url
                log.info("Saved server is reachable.")
            else:
                log.warning("Saved server could not be reached or does not expose ContentDirectory.")
        # -----------------------------------------------------------------
        # If we still have no usable server, discover a new.
        # -----------------------------------------------------------------
        if not server_control_url:
            self.net_wrapper.discover_servers()
            server_desc_url = self.net_wrapper.choose_server(preferred_server_desc_url)
            if server_desc_url:
                save_preferred_server(server_desc_url)
                server_control_url = DLNAWrapper.resolve_control(server_desc_url)
        # -----------------------------------------------------------------
        # At this point we have a valid control URL
        # -----------------------------------------------------------------
        log.info(f"Using ContentDirectory control URL: {server_control_url}")
        self.net_wrapper.set_server(server_control_url)
        # -----------------------------------------------------------------
        # Récupération du Conteneur des Musiques
        # -----------------------------------------------------------------
        self.net_wrapper.find_music_container()

    # --------------------------------------------------------------------- #
    # Scanne le server DLNA et stocke les metadata des MP3 dans la database.
    # --------------------------------------------------------------------- #
    def scan_all_mp3(self):
        log.debug("Scanning DLNA server for all MP3s...")
        all_tracks = self.net_wrapper.scan_all_mp3()
        # ----------------------------------------------------------------- #
        # On stocke le résultat dans la base de données
        # ----------------------------------------------------------------- #
        self.db_w.store_tracks(all_tracks)
        log.info(f"Scan terminé: {len(all_tracks)} pistes trouvées")

    # --------------------------------------------------------------------- #
    # Retourne la liste des tracks MP3 correspondant aux critères demandés.
    # --------------------------------------------------------------------- #
    def get_tracklist_from_db(self, mode: str, value: str) -> List[str]:
        if mode == 'genre':
            return self.db_w.get_tracks_for_genre(value)
        if mode == 'year':
            return self.db_w.get_tracks_for_decade(int(value))
        if mode == 'rating':
            # TODO : A COMPLETER
            pass
        if mode == 'alea':
            # TODO : A COMPLETER
            pass
        if mode == 'bpm':
            # TODO : A COMPLETER
            pass
        return []

    # --------------------------------------------------------------------- #
    # Attend 2 secondes et affiche les infos du clip.
    # --------------------------------------------------------------------- #
    async def show_clip_info(self, track_id: str):
        await asyncio.sleep(2)
        # info = self.net_wrapper.get_clip_info(track_id)
        info = self.db_w.get_track_info(track_id)
        if info:
            title, artist, year, genre = info
            # NOW PLAYING :
            Display.show(title.upper(), f"by {artist}", f"({year})", genre)
