# coding: UTF-8
# ==================================================================
# lib/keyboard_control.py
# ==================================================================
# VintageRadio - Librairie.
# Lumo (2026)
# ==================================================================
import asyncio
from pynput import keyboard
from lib.dlna_logger import get_logger

log = get_logger(__name__)


# ------------------------------------------------------------------------- #
# Cette classe simule les boutons GPIO par des touches du clavier.
# ------------------------------------------------------------------------- #
class KeyboardController:
    """Écoute le clavier et envoie des commandes à l'event loop."""

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, event_queue: asyncio.Queue):
        self.event_queue = event_queue
        self.listener = None
        self.running = False

    # --------------------------------------------------------------------- #
    # Start listening keyboard.
    # --------------------------------------------------------------------- #
    def start(self):
        """Démarrer l'écouteur de clavier dans un thread séparé."""
        self.running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            suppress=False  # laisser les touches passer au terminal
        )
        self.listener.start()
        log.debug("Keyboard listener started")

    # --------------------------------------------------------------------- #
    # Stop listening keyboard.
    # --------------------------------------------------------------------- #
    def stop(self):
        """Arrêter l'écouteur."""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener.join(timeout=1)
        log.debug("Keyboard listener stopped")

    # --------------------------------------------------------------------- #
    # Appui sur une touche: n (play next) | p (pause) | q (quit) | a (again)
    # TODO a tester
    # --------------------------------------------------------------------- #
    def _on_press(self, key):
        """Callback appelé à chaque pression de touche."""
        try:
            if hasattr(key, 'char'):
                char = key.char.lower()
                if char == 'n':  # Touche 'n' pour PlayNext
                    asyncio.run_coroutine_threadsafe(
                        self.event_queue.put('PLAY_NEXT'),
                        asyncio.get_event_loop()
                    )
                    log.debug("Key 'n' pressed → PLAY_NEXT queued")
                elif char == 'p':  # Touche 'p' pour Pause/Play
                    asyncio.run_coroutine_threadsafe(
                        self.event_queue.put('TOGGLE_PAUSE'),
                        asyncio.get_event_loop()
                    )
                    log.debug("Key 'p' pressed → TOGGLE_PAUSE queued")
                elif char == 'q':  # Quitter
                    asyncio.run_coroutine_threadsafe(
                        self.event_queue.put('QUIT'),
                        asyncio.get_event_loop()
                    )
                    log.debug("Key 'q' pressed → QUIT queued")
                elif char == 'a':  # Play Again
                    asyncio.run_coroutine_threadsafe(
                        self.event_queue.put('PLAY_AGAIN'),
                        asyncio.get_event_loop()
                    )
                    log.debug("Key 'a' pressed → PLAY_AGAIN queued")

        except Exception as e:
            log.error("Error processing key press: %s", e)
