# dlna_music.py
import time
import random
import sys

try:
    import vlc
except ImportError:
    sys.exit("python-vlc not found – install with: sudo apt-get install python3-vlc ")


# ----------------------------------------------------------------------- #
# Cette classe gère les musiques situées sur le serveur DLNA.
# ----------------------------------------------------------------------- #
class DLNAMusic:
    """
    Interactions with musical files.
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self):
        """ Constructor. """
        self.tracks = []
        self._stop_requested = False
        self.renderer = vlc.MediaPlayer()
        #  Optional hook that the caller can set to be notified after each track
        self.after_track_callback = None

    # --------------------------------------------------------------------- #
    # Remplissage de la structure
    # --------------------------------------------------------------------- #
    def discover_tracks(self, mp3_urls):
        """ Populate tracks with absolute URLs of MP3 files found under container_url."""
        if mp3_urls is None:  # DDL
            print("No MP3 files were found in the folder.")
        else:
            self.tracks = mp3_urls
        return

    # --------------------------------------------------------------------- #
    # Affiche la liste des titres reçus
    # --------------------------------------------------------------------- #
    def list_all(self):
        for url in self.tracks:
            print(url)
        return

    # --------------------------------------------------------------------- #
    # Joue un fichier MP3
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
    # Stoppe le fichier MP3
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
    # Play all tracks in a random order
    # ----------------------------------------------------------------------
    def play_random(self, repeat=False, delay_between=0):
        """
        Play all discovered MP3 tracks in a random sequence.

        Parameters
        ----------
        repeat : bool, optional
            If True, the shuffled playlist will restart automatically after the last
            track finishes (continuous shuffle). Default is False.
        delay_between : float, optional
            Seconds to wait between tracks (useful if the renderer needs a short
            pause before accepting the next URI). Default is 0.

        Notes
        ----------
        * The method respects ``self._stop_requested`` – calling ``self.stop()``
          from another thread will break out of the loop promptly.
        * It makes a shallow copy of ``self.tracks`` before shuffling so the
          original ordering remains unchanged for later calls.
        """
        if not self.tracks:
            raise RuntimeError("No tracks loaded – call discover_tracks() first.")

        while True:
            # Create a fresh shuffled copy each iteration (important if repeat=True)
            shuffled_tracklist = self.tracks[:]  # shallow copy
            random.shuffle(shuffled_tracklist)  # in‑place randomisation

            for uri in shuffled_tracklist:
                if self._stop_requested:
                    # Reset flag for possible future playback sessions
                    self._stop_requested = False
                    return

                # Play the track
                self.play_track(uri)

                # Optional: give the renderer a moment to settle before the next URI
                if delay_between:
                    time.sleep(delay_between)

                # --------------------------------------------------------------------
                # Invoke the optional hook – this is where we will reload request.json
                # TODO: A faire au bout de 10 secondes de playout
                # --------------------------------------------------------------------
                if callable(self.after_track_callback):
                    self.after_track_callback()
                # --------------------------------------------------------------------

                # NOTE: If you want to wait until the track actually finishes,
                # you could poll the renderer’s TransportState or listen for an event.
                # For simplicity, this example just fires the next URI
                # after the optional delay.

            if not repeat:
                break  # Exit after one full shuffled run
