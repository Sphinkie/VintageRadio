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
import signal
import sys


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
def sigint_handler(signum, frame):
    print(f"Received SIGINT! (signum={signum} - frame={frame})")
    sys.exit(0)


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
def on_key_press(action):
    """ Callback for the Keyboard and GPIO Listening threads. """
    if action == 'QUIT':
        log.warning("QUIT command received")
    elif action == 'NEXT':
        log.info("PLAY NEXT command received")
        # La musique suivante va commencer automatiquement.
        musics.stop()
    elif action == 'AGAIN':
        log.info("PLAY AGAIN command received")
        musics.rewind()
        # La musique va recommencer automatiquement.
        musics.stop()
    elif action == 'RESET':
        log.info("RESET command received")
        # Supprime la base de données et quitte.
        # Utilisé si la BDD a besoin d'être rafraichie
        engine.drop_database()
        log.warning("Quit application")
        quit_event.set()
    elif action == 'DISCOVER':
        log.info("DISCOVERY command received")
        # Refait un scan du réseau à la recherche de serveurs DLNA
        # Utilisé pour la mise au point
        engine.net_wrapper.discover_servers()
    # TODO : action STAR ME


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    """
    # Helper pour le programme principal.
    # Parsing des arguments en ligne de commande.
    :return: La liste des arguments.
    """
    parser = argparse.ArgumentParser(
        description='VintageRadio - DLNA Music Player for Raspberry Pi'
    )
    # Parse command-line arguments.
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for INFO, -vv for DEBUG)'
    )
    return parser.parse_args()


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
def setup():
    """ Setup() : Main initialisation procedure. """
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


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
async def loop():
    """ loop() : Boucle principale asynchrone. """
    log.debug("Start Loop")
    lecture_task = None
    # ------------------------------------------------------------------------
    # Tache périodique No 1 : Reload user request (json file) every 5 seconds.
    # ------------------------------------------------------------------------
    refresh_task = asyncio.create_task(user_request.repeating_reread(5))  # fire-and-forget
    # ------------------------------------------------------------------------
    # Tache périodique No 2 : Read missing Beat Per Minute and Ratings on server.
    # ------------------------------------------------------------------------
    refresh_bpm = asyncio.create_task(engine.repeat_get_data(6))  # start repeating

    try:
        # --------------------------------------------------------------------
        # Boucle principale
        # --------------------------------------------------------------------
        while True:
            # ----------------------------------------------------------------
            # [1] Check if a QUIT event was received
            # ----------------------------------------------------------------
            if quit_event.is_set():
                log.debug("Exiting loop")
                break

            # ----------------------------------------------------------------
            # [2] A-t-on une nouvelle requete de l'utilisateur ?
            # ----------------------------------------------------------------
            if user_request.has_changed():
                log.info("User request change detected")
                # -------------------------------------------------------------
                # List the MP3 files for the request, and send them to the Music object.
                # -------------------------------------------------------------
                log.info(f"Current requested Mode is 'by {user_request.get('mode')}'")
                log.info(f"Current Request is '{user_request.get('request')}'")
                track_list = engine.get_tracklist_from_db(user_request.get('mode'), user_request.get('request'))
                musics.load_playlist(track_list)
                # En cas de playlist par genre ou par rating, on la met dans un ordre aléatoire
                # (chaque fois différent).
                if user_request.get('mode') == 'genre' or user_request.get('mode') == 'rating':
                    musics.shuffle_playlist()
                else:
                    musics.clone_playlist()
                # musics.list_all()
                # On acquitte la prise en compte du changement.
                user_request.ack_has_changed()

            # -------------------------------------------------------------
            # [3] Play MP3 files
            # -------------------------------------------------------------
            if lecture_task is None:
                log.debug("Start playing a new file")
                lecture_task = asyncio.create_task(musics.play_async())
                # On attend que la lecture ait démarré
                await lecture_task
                # On demande l'affichage du titre
                current_id = musics.get_playing_id()
                display_task = asyncio.create_task(engine.show_clip_info(current_id))
                log.debug(f"Start task {display_task}")
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
        refresh_bpm.cancel()
        # On attend que les tâches s'achèvent
        await refresh_task
        await refresh_bpm
        log.warning("Shutdown complete")


# --------------------------------------------------------------------- #
# --------------------------------------------------------------------- #
async def main():
    """ PROGRAMME PRINCIPAL """
    # -----------------------------
    # On exécute le Setup
    # -----------------------------
    setup()
    # -----------------------------
    # On lance la boucle (si on a un serveur DLNA)
    # -----------------------------
    if engine.ready():
        await loop()
    engine.close()


# --------------------------------------------------------------------- #
# Launch Main Program (EventLoop)
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    args = parse_args()
    # ---------------------------------------------------------
    # Initialisation du logger
    # ---------------------------------------------------------
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
    signal.signal(signal.SIGINT, sigint_handler)
    # Create a Quit Event
    quit_event = asyncio.Event()
    keyboard_ctrl = KeyboardController(on_key_press, quit_event)
    # ---------------------------------------------------------
    # Lancement de l'Event Loop
    # ---------------------------------------------------------
    asyncio.run(main())
