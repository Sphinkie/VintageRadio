# coding: UTF-8
# ==================================================================
# lib/dlna_music.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import os
import sys
import time
import random
import signal
from typing import List
from urllib.parse import urlsplit
from lib.vr_logger import get_logger
from lib.user_display import Display

try:
    import vlc
except ImportError:
    sys.exit("python-vlc not found – install with: sudo apt-get install python3-vlc ")

log = get_logger(__name__)


# ----------------------------------------------------------------------- #
# Cette classe gère les musiques situées sur le serveur DLNA.
# ----------------------------------------------------------------------- #
class DLNAMusic:
    """ Interactions with musical files.  """

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructeur. """
        self.tracks = []
        self.shuffled_tracklist = []
        self.current_pos = 0
        # Enable ReplayGain normalization.
        # Note: tous les MP3 ont été normalisés avec mp3gain (ReplayGain)
        # Création d'une instance VLC
        self._instance = vlc.Instance(
            '--quiet',
            # '--verbose', '2',
            '--aout', 'pulse',  # Audio output module
            '--audio-replay-gain-mode', 'track',  # Mode ReplayGain
            '--audio-replay-gain-preamp', '0',  # Replay Mode ReplayGain in dB
            '--no-video'
        )
        self.renderer = self._instance.media_player_new()
        # On ajoute un handler pour le CTR-C
        self.install_signal_handler()
        # Seed avec des octets aléatoires du système
        random.seed(os.urandom(256))

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def install_signal_handler(self):
        """ Installe un Handler qui stoppe VLC proprement en cas de CTRL-C. """

        # ------------------------------------
        def handler(sig, frame):
            """ Le Handler proprement dit. """
            log.info("Stop playing... (exit)")
            self.stop()
            sys.exit(0)

        # ------------------------------------
        signal.signal(signal.SIGINT, handler)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def load_playlist(self, mp3_urls: List[str]):
        """
        Remplissage de la liste des tracks.
        Populate tracks with absolute URLs of MP3 files found under container_url.
        :param mp3_urls: Une liste d'URLs.
        """
        if mp3_urls is None or len(mp3_urls) == 0:
            log.warning("No MP3 files in the playlist.")
            Display.warning("No MP3 files in the playlist.")
        else:
            self.tracks = mp3_urls

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def list_all(self):
        """Affiche la liste des URLs reçues."""
        log.debug("MP3 urls found:")
        for url in self.tracks:
            log.debug(url)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def start_track(self, track_url):
        """
        Démarre un fichier MP3.
        Send a Play request for a single track to the renderer.
        """
        # Create a media player from the instance
        media = self._instance.media_new(track_url)
        self.renderer.set_media(media)  # Link to the existing renderer
        # Start playback (returns immediately)
        self.renderer.play()

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def stop(self):
        """Stoppe le fichier MP3 courant et attend un court délai."""
        # Send a STOP command to the renderer.
        self.renderer.stop()
        # Give the renderer a moment to settle before the next URI
        # Seconds to wait between tracks
        # (useful if the renderer needs a short pause before accepting the next URI)
        delay_between = 0.5
        if delay_between:
            time.sleep(delay_between)

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def is_stopped(self) -> bool:
        """
        Vérifie si une musique  est en cours.
        :return: Retourne True si le renderer VLC est Ended, False si le renderer VLC est playing.
        """
        """ returns False if a file is playing."""
        # log.debug(self.renderer.get_state())
        ended = (self.renderer.get_state() == vlc.State.Ended)
        stopped = (self.renderer.get_state() == vlc.State.Stopped)
        return ended or stopped

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def shuffle_playlist(self):
        """
        Gestion de la randomization.
        It makes a shallow copy of ``self.tracks`` before shuffling so the
        original ordering remains unchanged for later calls.
        """
        if not self.tracks:
            raise RuntimeError("No tracks loaded – call discover_tracks() first.")
        # Create a fresh shuffled copy  (at each iteration if repeat=True)
        log.info("Shuffle playlist")
        self.shuffled_tracklist = self.tracks[:]  # shallow copy
        random.shuffle(self.shuffled_tracklist)  # in‑place randomisation
        self.current_pos = 0

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def clone_playlist(self):
        """
        Clone la playlist, pour obtenir une playlist de travail.
        Makes a shallow copy of ``self.tracks`` as it is the working playlist.
        """
        log.debug("Clone playlist")
        if not self.tracks:
            log.error("Playlist is empty !")
        self.shuffled_tracklist = self.tracks[:]  # shallow copy
        self.current_pos = 0

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def play_sync(self):
        """
        Joue un fichier MP3 et attend la fin.
        Note : La fonction est bloquante : on y reste jusqu'à la fin du morceau.
        """
        track_url = self.shuffled_tracklist[self.current_pos]
        # Send a Play request for a single track to the renderer.
        self.start_track(track_url)
        # Wait until the track ends
        while self.renderer.get_state() != vlc.State.Ended:
            time.sleep(0.5)  # poll every half-second
        # Give the renderer a moment to settle before the next URI
        time.sleep(0.5)
        self.current_pos += 1

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    async def play_async(self):
        """ Démarre la piste suivante de la playlist (en mode asynchrone). """
        if self.current_pos >= len(self.shuffled_tracklist):
            self.current_pos = 0
        if not self.shuffled_tracklist:
            log.error("Playlist is empty: cannot play")
        else:
            uri = self.shuffled_tracklist[self.current_pos]
            # Start the track
            log.debug("[Start playing %d", self.current_pos)
            self.start_track(uri)
            self.current_pos += 1

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def get_playing_id(self) -> str:
        """
        Renvoie l'identifiant du clip en cours (ou une str vide).
        :return: 2913 if the URL is `http://192.168.0.101:50002/m/MP3/2913.mp3`
        """
        pos = max(0, self.current_pos - 1)
        if not self.shuffled_tracklist:
            log.error("Playlist is empty: cannot find curent id")
            return ""
        else:
            current_url = self.shuffled_tracklist[pos]
            u = urlsplit(current_url)
            filename = u.path.split('/').pop()
            return filename.split('.')[0]

    # --------------------------------------------------------------------- #
    # --------------------------------------------------------------------- #
    def rewind(self):
        """Se repositionne sur le clip en cours."""
        self.current_pos -= 1
        if self.current_pos < 0:
            self.current_pos = 0
