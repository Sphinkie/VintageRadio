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


# --------------------------------------------------------------------- #
# Attend 2 secondes et affiche les infos du clip.
# --------------------------------------------------------------------- #
async def show_clip_info():
    await asyncio.sleep(2)
    id = musics.get_playing_id()
    # info = wrapper.get_clip_info_from_container(id)
    info = net_wrapper.get_clip_info_from_db(id)
    if info:
        title, artist, year, genre = info
        # NOW PLAYING :
        Display.show(title.upper(), f"by {artist}", f"({year})", genre)


# ----------------------------------------------------------------------- #
# Cette classe ....
# ----------------------------------------------------------------------- #
class VREngine:

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.db_w = DBWrapper("./data/mp3_metadata.db")
        self.net_wrapper = DLNAWrapper()

    # --------------------------------------------------------------------- #
    # Nettoyer la base de données à la fermeture
    # --------------------------------------------------------------------- #
    def close(self):
        """Ferme les ressources (base de données)."""
        self.db_w.close()

    # --------------------------------------------------------------------- #
    # On est prêt si on a établi une laison avec un serveur DLNA
    # --------------------------------------------------------------------- #
    def ready(self) -> bool:
        return self.net_wrapper.server_control_url is not None

    # --------------------------------------------------------------------- #
    # Retourne une liste d'URLs basée sur la date et la plage demandées.
    # --------------------------------------------------------------------- #
    def get_urls_by_date_range(
            self,
            target_year: int,
            range_start: int,
            range_end: int
    ) -> List[str]:
        """
        Retourne une liste d'URLs filtrée par plage de dates avec ordre circulaire.

        Args :
            target_date : Date de départ (ex : 1964)
            range_start : Année de début de plage (ex : 1960)
            range_end : Année de fin de plage (ex : 1969)

        Returns :
            Liste d'URLs triées selon l'ordre circulaire
        """
        return self.db_w.get_tracks_by_date_range(target_year, range_start, range_end)

    # --------------------------------------------------------------------- #
    # Callback for the Keyboard
    # --------------------------------------------------------------------- #
    def on_key_press(self, action):
        if action == 'QUIT':
            log.warning("QUIT command received")
        elif action == 'NEXT':
            log.info("PLAY NEXT command received")
            # Trigger your skip logic here
            # La musique suivante va commencer automatiquement.
            musics.stop()
        elif action == 'AGAIN':
            log.info("PLAY AGAIN command received")
            musics.rewind()
            musics.stop()
            # La musique va recommencer automatiquement.
        elif action == 'DISCOVER':
            log.info("DISCOVERY command received")
            self.net_wrapper.discover_servers()

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

