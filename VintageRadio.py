# coding: UTF-8
# ==================================================================
# VintageRadio.py
# ==================================================================
# VintageRadio - Programme principal
# David de Lorenzo (2026)
# ==================================================================
import asyncio
import argparse
from lib.vr_logger import get_logger, set_logging
from lib.dlna_music import DLNAMusic
from lib.vr_engine import VREngine
from lib.user_request import UserRequest
from lib.user_keyboard import KeyboardController


# --------------------------------------------------------------------- #
# Callback for the Keyboard
# --------------------------------------------------------------------- #
def on_key_press(action):
    if action == 'QUIT':
        log.warning("QUIT command received")
    elif action == 'NEXT':
        log.info("PLAY NEXT command received")
        # La musique suivante va commencer automatiquement.
        musics.stop()
    elif action == 'AGAIN':
        log.info("PLAY AGAIN command received")
        musics.rewind()
        musics.stop()
        # La musique va recommencer automatiquement.
    elif action == 'DISCOVER':
        log.info("DISCOVERY command received")
        engine.net_wrapper.discover_servers()


# --------------------------------------------------------------------- #
# Helper pour le programme principal.
# Parsing des arguments en ligne de commande.
# --------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='VintageRadio - DLNA Music Player for Raspberry Pi'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for INFO, -vv for DEBUG)'
    )
    return parser.parse_args()


# --------------------------------------------------------------------- #
# Main initialisation
# --------------------------------------------------------------------- #
def setup():
    log.info("Start Setup")
    # -----------------------------------------------------------------
    # Get the DLNA server
    # -----------------------------------------------------------------
    engine.get_dlna_server()
    # -----------------------------------------------------------------
    # Récupère la liste de tous les MP3 du serveur DLNA
    # -----------------------------------------------------------------
    engine.scan_all_mp3()
    # -----------------------------------------------------------------
    # Première lecture du fichier de demande
    user_request.load_user_request()
    # Lance le Listener du clavier dans un thread.
    keyboard_ctrl.start()
    # -------------------------------------------------------------
    log.info("End Setup")


# -----------------------------------------------------------------
# Boucle principale asynchrone
# -----------------------------------------------------------------
async def loop():
    log.debug("Start Loop")
    lecture_task = None
    # -------------------------------------------------------------------------- #
    # Tache périodique No 1 : Reload user request (json file) every 5 seconds.
    # -------------------------------------------------------------------------- #
    refresh_task = asyncio.create_task(user_request.repeating_reread(5))  # fire-and-forget

    try:
        # -------------------------------------------------------------------------- #
        # Boucle principale
        # -------------------------------------------------------------------------- #
        while True:
            # ----------------------------------------------------------------- #
            # [1] Check if a QUIT event was received
            # ----------------------------------------------------------------- #
            if quit_event.is_set():
                log.debug("Exiting loop")
                break

            # ----------------------------------------------------------------- #
            # [2] A-t-on une nouvelle requete de l'utilisateur ?
            # ----------------------------------------------------------------- #
            if user_request.has_changed():
                log.info("User request change detected")
                # -------------------------------------------------------------
                # List the MP3 files for the request, and send them to the Music object.
                # -------------------------------------------------------------
                log.info(f"Current request is by '{user_request.get('mode')}'")
                log.info(f"Requested genre is '{user_request.get('genre')}'")
                track_list = engine.get_track_from_db(user_request.get('mode'), user_request.get('genre'))
                musics.load_playlist(track_list)
                musics.shuffle_playlist()
                # musics.list_all()
                # On acquitte la prise en compte du changement.
                user_request.ack_has_changed()

            # -------------------------------------------------------------
            # [3] Play MP3 files
            # -------------------------------------------------------------
            if lecture_task is None:
                log.debug("Start playing a new file")
                lecture_task = asyncio.create_task(musics.play_random_async())
                # On attend que la lecture ait démarré
                await lecture_task
                # On demande l'affichage du titre
                current_id = musics.get_playing_id()
                display_task = asyncio.create_task(engine.show_clip_info(current_id))
            # -------------------------------------------------------------
            # [4] Check if the MP3 file is still playing
            # -------------------------------------------------------------
            else:
                if musics.is_stopped():
                    lecture_task = None
                    log.debug("End playing]")
            # --------------------------------------------------------------------
            # [5] Boucle rythmée à 1 seconde.
            # --------------------------------------------------------------------
            await asyncio.sleep(1)
    # --------------------------------------------------------------------
    # Sortie de la boucle: on ferme tout.
    # --------------------------------------------------------------------
    finally:
        log.warning("End loop")
        keyboard_ctrl.stop()
        refresh_task.cancel()
        await refresh_task
        log.warning("Shutdown complete")


# ---------------------------------------------------------
# Programme Principal
# ---------------------------------------------------------
async def main():
    # On exécute le Setup
    setup()
    # On lance la boucle (si on a un serveur DLNA)
    if engine.ready():
        await loop()
    engine.close()


# -------------------------------------------------------------
# Launch Main Program (EventLoop)
# -------------------------------------------------------------
if __name__ == "__main__":
    args = parse_args()
    # -----------------------------------------------------------------
    # Initialisation du logger
    # -----------------------------------------------------------------
    set_logging(args.verbose)
    log = get_logger(__name__)
    # ---------------------------------------------------------
    # Initialisations des objets
    # ---------------------------------------------------------
    engine = VREngine()
    musics = DLNAMusic()
    user_request = UserRequest()
    # ---------------------------------------------------------
    # Initialise le Keyboard Listener thread
    # ---------------------------------------------------------
    # Create a Quit Event
    quit_event = asyncio.Event()
    keyboard_ctrl = KeyboardController(on_key_press, quit_event)
    # ---------------------------------------------------------
    # Lancement de l'Event Loop
    # ---------------------------------------------------------
    asyncio.run(main())
