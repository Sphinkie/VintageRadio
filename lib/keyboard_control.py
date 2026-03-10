# coding: UTF-8
# ==================================================================
# keyboard_control.py
# ==================================================================
# VintageRadio - Keyboard input handler (cross-platform)
# Lumo (2026)
# ==================================================================
import sys
import asyncio
import threading
from typing import Optional, Callable
from lib.dlna_logger import get_logger

# Detect operating system for conditional imports
IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    # Windows-specific imports
    import msvcrt
else:
    # Unix/Linux/macOS imports
    import termios
    import tty

log = get_logger(__name__)

# ----------------------------------------------------------------------- #
# Cette classe gère les touches du clavier (Windows/Raspberry)
# et simule les boutons GPIO par des touches du clavier.
# ----------------------------------------------------------------------- #
class KeyboardController:
    """
    Cross-platform keyboard input handler.
    Uses termios/tty on Unix-like systems (Raspberry Pi, Linux, macOS)
    and msvcrt on Windows.
    Callback is invoked whenever a recognized key is pressed.
    """

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, callback: Callable[[str], None], quit_event: asyncio.Event):
        """
        Initialize the keyboard controller.
        
        Args:
            callback: Function to call when a key is pressed.
                     Receives the action string ('NEXT', 'AGAIN', 'QUIT').
        """
        self.callback = callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.quit_event = quit_event  # Store the event

    # --------------------------------------------------------------------- #
    # Start listening keyboard.
    # --------------------------------------------------------------------- #
    def start(self):
        """Start listening for keyboard input in a background thread."""
        log.debug("Start keyboard listening thread")
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    # --------------------------------------------------------------------- #
    # Stop listening keyboard.
    # --------------------------------------------------------------------- #
    def stop(self):
        """Stop the listener thread and restore terminal settings."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    # --------------------------------------------------------------------- #
    # Redirige vers le Listener Windows ou Raspberry.
    # --------------------------------------------------------------------- #
    def _listen(self):
        """Route to the appropriate platform-specific listener."""
        if IS_WINDOWS:
            self._listen_windows()
        else:
            self._listen_unix()

    # --------------------------------------------------------------------- #
    # Listener pour Raspberry.
    # --------------------------------------------------------------------- #
    def _listen_unix(self):
        """
        Unix/Linux implementation using termios/tty.
        Reads single characters from stdin in raw mode (no line buffering).
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode (immediate keypress, no echo)
            tty.setraw(fd)
            
            while self.running:
                ch = sys.stdin.read(1)
                if ch:
                    log.debug(f"Keyboard (Unix): {ch}")
                    self._handle_key(ch)
                    
        except Exception as e:
            print(f"Keyboard error (Unix): {e}", file=sys.stderr)
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # --------------------------------------------------------------------- #
    # Listener pour Windows.
    # --------------------------------------------------------------------- #
    def _listen_windows(self):
        """
        Windows implementation using msvcrt.
        Uses kbhit() to check for keypresses without blocking.
        """
        while self.running:
            if msvcrt.kbhit():
                ch = msvcrt.getch().decode('utf-8', errors='ignore')
                log.debug(f"Keyboard (Windows): {ch}")
                self._handle_key(ch)

    # --------------------------------------------------------------------- #
    # Handler commun des touches reçues.
    # --------------------------------------------------------------------- #
    def _handle_key(self, ch: str):
        """
        Common key handling logic across platforms.
        Maps raw keypresses to action strings.
        
        Args:
            ch: Single character from keyboard input.
        """
        ch_lower = ch.lower()
        
        if ch_lower == 'n':
            self.callback('NEXT')
        elif ch_lower == 'a':
            self.callback('AGAIN')
        elif ch_lower == 'q':
            # Set the event to signal the main loop
            self.quit_event.set()
            # C'est alors même inutile d'appeler la callback
            self.callback('QUIT')
