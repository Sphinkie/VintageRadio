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
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.tracks = []
        self.shuffled_tracklist = []
        self.current_pos = 0
        # Enable ReplayGain normalization.
        # Note: tous les MP3 ont été normalisés avec mp3gain (ReplayGain)
        self._instance = vlc.Instance(
            '--quiet',
            '--audio-normalize',  # Enable replaygain
            '--replaygain-mode', 'track',  # 'track' or 'album'
            '--replaygain-preamp', '0',  # Pre-amplification in dB
            '--audio-filter', 'normvol'  # Additional volume normalization
        )
        # Création d'une instance VLC
        self.renderer = vlc.MediaPlayer()
        # On ajoute un handler pour le CTR-C
        self.install_signal_handler()
        # Seed avec des octets aléatoires du système
        random.seed(os.urandom(256))

    # --------------------------------------------------------------------- #
    # Installe un Handler qui stoppe VLC proprement en cas de CTRL-C.
    # --------------------------------------------------------------------- #
    def install_signal_handler(self):
        # -----------------------
        # Handler for CTRL-C
        # -----------------------
        def handler(sig, frame):
            log.info("Stop playing... (exit)")
            self.stop()
            sys.exit(0)

        # -----------------------
        signal.signal(signal.SIGINT, handler)

    # --------------------------------------------------------------------- #
    # Remplissage de la liste des tracks.
    # --------------------------------------------------------------------- #
    def discover_tracks(self, mp3_urls):
        """ Populate tracks with absolute URLs of MP3 files found under container_url."""
        if mp3_urls is None:
            Display.warning("No MP3 files were found in the folder.")
        else:
            self.tracks = mp3_urls
        return

    # --------------------------------------------------------------------- #
    # Affiche la liste des URLs reçues.
    # --------------------------------------------------------------------- #
    def list_all(self):
        log.debug("MP3 url found:")
        for url in self.tracks:
            log.debug(url)
        return

    # --------------------------------------------------------------------- #
    # Démarre un fichier MP3.
    # --------------------------------------------------------------------- #
    def start_track(self, track_url):
        """ Send a Play request for a single track to the renderer."""
        # Create a VLC instance and media player
        self.renderer = vlc.MediaPlayer(track_url)
        # Start playback (returns immediately)
        self.renderer.play()

    # --------------------------------------------------------------------- #
    # Retourne True si un fichier est Ended, False si le fichier est playing.
    # --------------------------------------------------------------------- #
    def is_stopped(self) -> bool:
        """ returns False if a file is playing."""
        # log.debug(self.renderer.get_state())
        ended = (self.renderer.get_state() == vlc.State.Ended)
        stopped = (self.renderer.get_state() == vlc.State.Stopped)
        return ended or stopped

    # --------------------------------------------------------------------- #
    # Stoppe le fichier MP3 courant et attend un court délai.
    # --------------------------------------------------------------------- #
    def stop(self):
        """Stop playback and signal any running shuffle loop to exit."""
        # Send the actual STOP command to the renderer:
        self.renderer.stop()
        # Give the renderer a moment to settle before the next URI
        # Seconds to wait between tracks
        # (useful if the renderer needs a short pause before accepting the next URI)
        delay_between = 0.5
        if delay_between:
            time.sleep(delay_between)

    # --------------------------------------------------------------------- #
    # Joue un fichier MP3 et attend la fin.
    # Note: La fonction est bloquante : on y reste jusqu'à la fin du morceau.
    # --------------------------------------------------------------------- #
    def play_track(self, track_url):
        """Send a Play request for a single track to the renderer."""
        self.start_track(track_url)
        # Wait until the track ends
        while self.renderer.get_state() != vlc.State.Ended:
            time.sleep(0.5)  # poll every half-second
        # Give the renderer a moment to settle before the next URI
        time.sleep(0.5)

    # --------------------------------------------------------------------- #
    # Play All files in DLNA order.
    # --------------------------------------------------------------------- #
    def play_all(self):
        for url in self.tracks:
            self.play_track(url)
        return

    # ----------------------------------------------------------------------
    # Gestion de la randomization.
    # ----------------------------------------------------------------------
    def shuffle_playlist(self):
        """
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
    # Play a track from the shuffled tracklist.
    # Note: La fonction est bloquante: on y reste jusqu'à la fin du morceau.
    # ----------------------------------------------------------------------
    def play_random(self):
        """ Play all discovered MP3 tracks in a random sequence. """
        uri = self.shuffled_tracklist[self.current_pos]
        # Play the track
        self.play_track(uri)
        self.current_pos += 1

    # --------------------------------------------------------------------- #
    # Démarre une piste en mode asynchrone.
    # --------------------------------------------------------------------- #
    async def play_random_async(self):
        if self.current_pos >= len(self.shuffled_tracklist):
            self.shuffle_playlist()
            self.current_pos = 0
        log.debug("[Start playing %d", self.current_pos)
        uri = self.shuffled_tracklist[self.current_pos]
        # Start the track
        self.start_track(uri)
        self.current_pos += 1

    # --------------------------------------------------------------------- #
    # Renvoie l'identifiant du clip en cours
    # Example:
    #   from http://192.168.0.101:50002/m/MP3/2913.mp3 the returned id is 2913
    # --------------------------------------------------------------------- #
    def get_playing_id(self):
        pos = max(0, self.current_pos - 1)
        current_url = self.shuffled_tracklist[pos]
        u = urlsplit(current_url)
        filename = u.path.split('/').pop()
        return filename.split('.')[0]

    # --------------------------------------------------------------------- #
    # Se repositionne sur le clip en cours
    # --------------------------------------------------------------------- #
    def rewind(self):
        self.current_pos -= 1
        if self.current_pos < 0:
            self.current_pos = 0
