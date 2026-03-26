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
        self.db_wrapper = DBWrapper("./data/music_metadata.db")
        self.net_wrapper = DLNAWrapper()
        display = Display('tty')
        display.show("VINTAGE RADIO")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def close(self):
        """ Ferme la base de données à la fermeture de l'application. """
        self.db_wrapper.close()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def drop_database(self):
        """ Supprime la base de données. """
        self.db_wrapper.drop_db()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def ready(self) -> bool:
        """
        On est prêt si on a établi une liaison avec un serveur DLNA.
        :return: True si tout est OK au niveau de la connexion avec le serveur DLNA.
        """
        return self.net_wrapper.server_control_url is not None

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_dlna_server(self):
        """ Cherche un server DLNA. Il est mémorisé dans le network_wrapper. """
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
    # --------------------------------------------------------------------- #
    def scan_all_mp3(self):
        """ Scanne le server DLNA et stockage des metadata des MP3 dans la database. """
        log.debug("Scanning DLNA server for all MP3s...")
        all_tracks = self.net_wrapper.scan_all_mp3()
        # ----------------------------------------------------------------- #
        # On stocke le résultat dans la base de données
        # ----------------------------------------------------------------- #
        self.db_wrapper.store_tracks(all_tracks)
        log.info(f"Scan terminé: {len(all_tracks)} pistes trouvées")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_tracklist_from_db(self, mode: str, value: str) -> List[str]:
        """
        Retourne la liste des tracks MP3 correspondant aux critères demandés.
        :param mode: La classification des musiques demandées par l'utilisateur (genre, year, bpm, rating, alea).
        :param value: La valeur demandée (par exemple "Blues" si le mode est "par Genre").
        :return: Une liste d'URLs.
        """
        if mode == 'genre':
            return self.db_wrapper.get_tracks_for_genre(value)
        if mode == 'year':
            return self.db_wrapper.get_tracks_for_decade(int(value))
        if mode == 'bpm' or mode == "beat":
            return self.db_wrapper.get_tracks_for_beat(float(value))
            pass
        if mode == 'rating':
            # TODO : gestion du mode rating
            pass
        if mode == 'alea':
            # TODO : gestion du mode aleatoire
            pass
        return []

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    async def show_clip_info(self, track_id: str):
        """
        Attend deux secondes et affiche les infos du clip.
        :param track_id: L'identifiant du clip dont on veut afficher les informations détaillées.
        """
        await asyncio.sleep(2)
        # info = self.net_wrapper.get_clip_info(track_id)
        info = self.db_wrapper.get_track_info(track_id)
        if info:
            title, artist, year, genre, bpm = info
            # NOW PLAYING :
            Display.show(title.upper(), f"by {artist}", f"({year})", genre, f"<beat {bpm} >")

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    async def repeat_get_data(self, period: float):
        """
        Récupération du BPM et du RATING du clip.
        Périodiquement, on vérifie s'il nous manque encore des BPM.
        :param period: Attente avant recupération nouveau BPM. Typiquement 1s.
        """
        unrythmed_track_list = self.db_wrapper.get_unrythmed_tracks()
        try:
            for track_url in unrythmed_track_list:
                # track_url = "http://192.168.0.101:50002/m/MP3/3532.mp3"
                await asyncio.sleep(period)
                log.debug(f"get dat for {track_url}")
                self.get_additional_data(track_url)
        except asyncio.CancelledError:
            log.warning("repeat_get_data task cancelled.")

    # --------------------------------------------------------------------- #
    # Récupération du BPM et du RATING du clip.
    # --------------------------------------------------------------------- #
    def get_additional_data(self, track_url: str):
        """
        Récupération d'informations complémentaires sur le clip : BEAT et RATING.
        Ces informations ne sont pas remontées par le DLNA.
        Args :
            track_url : url du clip dont on veut les informations.
        """
        tags = self.net_wrapper.get_track_details(track_url)
        # Enregistre les tags dans la base
        self.db_wrapper.update_track_bpm(tags)
        self.db_wrapper.update_track_rating(tags)
