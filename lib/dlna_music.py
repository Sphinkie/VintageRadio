# coding: UTF-8
# ==================================================================
# dlna_music.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import time
import random
import sys
import signal

try:
    import vlc
except ImportError:
    sys.exit("python-vlc not found – install with: sudo apt-get install python3-vlc ")


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
        self.after_track_callback = None
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
    # Joue un fichier MP3.
    # Note: La fonction est bloquante: on y reste jusqu'à la fin du morceau.
    # --------------------------------------------------------------------- #
    def play_track(self, track_url):
        """Send a Play request for a single track to the renderer."""
        # Create a VLC instance and media player
        self.renderer = vlc.MediaPlayer(track_url)
        # Start playback (returns immediately)
        self.renderer.play()
        # Wait until the track ends
        while self.renderer.get_state() != vlc.State.Ended:
            time.sleep(0.5)  # poll every half-second

    # --------------------------------------------------------------------- #
    # Stoppe le fichier MP3.
    # --------------------------------------------------------------------- #
    def stop(self):
        """Stop playback and signal any running shuffle loop to exit."""
        self._stop_requested = True
        # Send the actual STOP command to the renderer:
        self.renderer.stop()

    # --------------------------------------------------------------------- #
    # Play All files in DLNA order.
    # --------------------------------------------------------------------- #
    def play_all(self):
        for url in self.tracks:
            # Create a VLC instance and media player
            self.renderer = vlc.MediaPlayer(url)
            # Start playback (returns immediately)
            self.renderer.play()
            # Wait until the track ends
            while self.renderer.get_state() != vlc.State.Ended:
                time.sleep(0.5)  # poll every half-second
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
    def play_random(self, delay_between=0):
        """
        Play all discovered MP3 tracks in a random sequence.

        Parameters
        ----------
        delay_between : float, optional
            Seconds to wait between tracks (useful if the renderer needs a short
            pause before accepting the next URI). Default is 0.

        Notes
        ----------
        * The method respects ``self._stop_requested`` – calling ``self.stop()``
          from another thread will break out of the loop promptly.
        """

        # Utile ici ?
        if self._stop_requested:
            # Reset flag for possible future playback sessions
            self._stop_requested = False
            return

        uri = self.shuffled_tracklist[self.current_pos]
        # Play the track
        self.play_track(uri)
        self.current_pos += 1

        # Give the renderer a moment to settle before the next URI
        if delay_between:
            time.sleep(delay_between)
