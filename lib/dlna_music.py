# coding: UTF-8
# ==================================================================
# dlna_music.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import sys
import time
import random
import signal
import asyncio
from urllib.parse import urlsplit
from lib.dlna_logger import get_logger

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
        self._stop_requested = False
        self.renderer = vlc.MediaPlayer()
        #  Optional hook that the caller can set to be notified after each track
        self.refresh_request_callback = None
        # On ajoute un handler pour le CTR-C
        self.install_signal_handler()

    # --------------------------------------------------------------------- #
    # Installe un Handler qui stoppe VLC proprement en cas de CTRL-C.
    # --------------------------------------------------------------------- #
    def install_signal_handler(self):
        # -----------------------
        # Handler
        # -----------------------
        def handler(sig, frame):
            print("\n--- Stop playing... (exit)")
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
            print("No MP3 files were found in the folder.")
        else:
            self.tracks = mp3_urls
        return

    # --------------------------------------------------------------------- #
    # Affiche la liste des URLs reçues.
    # --------------------------------------------------------------------- #
    def list_all(self):
        print(f"\n--- MP3 files found:")
        for url in self.tracks:
            print(url)
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
    def isStopped(self) -> bool:
        """ returns False if a file is playing."""
        return (self.renderer.get_state() == vlc.State.Ended)

    # --------------------------------------------------------------------- #
    # Stoppe le fichier MP3 et attend un court délai.
    # --------------------------------------------------------------------- #
    def stop(self):
        """Stop playback and signal any running shuffle loop to exit."""
        self._stop_requested = True
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
    # Note: La fonction est bloquante: on y reste jusqu'à la fin du morceau.
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
    # TODO : A voir quand appeler
    # ----------------------------------------------------------------------
    def shuffle_playlist(self):
        """
        It makes a shallow copy of ``self.tracks`` before shuffling so the
        original ordering remains unchanged for later calls.
        """
        if not self.tracks:
            raise RuntimeError("No tracks loaded – call discover_tracks() first.")
        # Create a fresh shuffled copy  (at each iteration if repeat=True)
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
        # Si on a atteint la dernier piste on re-shuffle
        if self.current_pos > len(self.shuffled_tracklist):
            self.shuffle_playlist()
            self.current_pos = 0
        log.debug("[Start playing %d", self.current_pos)
        uri = self.shuffled_tracklist[self.current_pos]
        # Start the track
        self.start_track(uri)
        self.current_pos += 1

    # --------------------------------------------------------------------- #
    # Invoque la callback après un délai de 10 secondes.
    # --------------------------------------------------------------------- #
    async def delayed_callback(self):
        log.debug("delayed_callback invoked")
        await asyncio.sleep(10)
        self.refresh_request_callback()

    # --------------------------------------------------------------------- #
    # Renvoie l'identifiant du clip en cours
    # Example:
    #   from http://192.168.0.101:50002/m/MP3/2913.mp3 the returned id is 2913
    # --------------------------------------------------------------------- #
    def get_playing_id(self):
        current_url = self.shuffled_tracklist[self.current_pos]
        u = urlsplit(current_url)
        filename = u.path.split('/').pop()
        return filename.split('.')[0]

    # --------------------------------------------------------------------- #
    # Joue le clip suivant
    # --------------------------------------------------------------------- #
    async def skip_to_next(self):
        """Interrompt le clip en cours et joue le suivant."""
        log.debug("skip_to_next called")
        # Arrêter la lecture en cours
        self._stop_event.set()
        if self._playback_task and not self._playback_task.done():
            self._playback_task.cancel()
            try:
                await self._playback_task
            except asyncio.CancelledError:
                pass
        # Charger et jouer le suivant
        log.info("Skipping to next track: %s", next_track)
        # TODO : pas net
        self._playback_task = asyncio.create_task(self.play_random_async())