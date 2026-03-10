# coding: UTF-8
# ==================================================================
# VintageRadio.py
# ==================================================================
# VintageRadio - Programme principal
# David de Lorenzo (2026)
# ==================================================================
import asyncio
from lib.keyboard_control import KeyboardController
from lib.dlna_music import DLNAMusic
from lib.dlna_listing import *
from lib.dlna_preferences import *
from lib.dlna_user_request import DLNAUserRequest
from lib.dlna_network_wrapper import DLNAWrapper
from lib.dlna_logger import get_logger
from typing import Optional


# --------------------------------------------------------------------- #
# Attend 2 secondes et affiche les infos du clip.
# TODO : mettre ailleurs
# --------------------------------------------------------------------- #
async def show_clip_info():
    await asyncio.sleep(2)
    id = musics.get_playing_id()
    print(f"NOW PLAYING {id}")


# --------------------------------------------------------------------- #
# Callback for the Keyboard
# --------------------------------------------------------------------- #
def on_key_press(action):
    if action == 'QUIT':
        log.info("QUIT command received")
    elif action == 'NEXT':
        log.info("PLAY NEXT command received")
        # Trigger your skip logic here
        # La musique suivante va commencer automatiquement.
        musics.stop()
    elif action == 'AGAIN':
        log.info("PLAY AGAIN command received")
        musics.rewind()
        musics.stop()
        # La musique va recommencer automatiquement.


# --------------------------------------------------------------------- #
# Main initialisation
# --------------------------------------------------------------------- #
def setup():
    log.info("Start Setup")

    # -----------------------------------------------------------------
    # 1️⃣ Try to load a previously saved server
    # -----------------------------------------------------------------
    server_control_url: Optional[str] = None
    preferred_server_url = load_preferred_server()
    log.info("preferred server url: %s", preferred_server_url)
    # -----------------------------------------------------------------
    # If we have a saved description URL, verify that it is still reachable
    # -----------------------------------------------------------------
    if preferred_server_url:
        log.debug(f"Trying previously saved server: {preferred_server_url}")
        ctrl = resolve_control(preferred_server_url)
        if ctrl:
            server_control_url = ctrl
            log.info("Saved server is reachable.")
        else:
            log.warning("Saved server could not be reached or does not expose ContentDirectory.")
    # -----------------------------------------------------------------
    # If we still have no usable server, discover a new
    # -----------------------------------------------------------------
    if not server_control_url:
        servers = wrapper.discover_servers()
        server_control_url = choose_server(servers, preferred_server_url)
        if server_control_url:
            save_preferred_server(server_control_url)
    # -----------------------------------------------------------------
    # At this point we have a valid control URL
    # -----------------------------------------------------------------
    log.info(f"Using ContentDirectory control URL: {server_control_url}")
    wrapper.set_server(server_control_url)
    # -------------------------------------------------------------
    # Première lecture du fichier de demande
    user_request.load_user_request()
    # Récupération du Container parent : MUSIC
    wrapper.find_music_container()
    # Lance le Listener du clavier dans un thread.
    keyboard_ctrl.start()
    # -------------------------------------------------------------
    log.info("End Setup")


# -----------------------------------------------------------------
# Boucle principale
# -----------------------------------------------------------------
async def loop():
    log.debug("Start Loop")
    lecture_task = None

    # --------------------------------------------------------------------
    # Tache périodique No 1
    # Reload user request (json file) every 5 seconds.
    # --------------------------------------------------------------------
    refresh_task = asyncio.create_task(user_request.repeating_reread(5))  # fire-and-forget

    try:
        while True:
            # ----------------------------------------------------------------- #
            # Check if a QUIT event was received
            # ----------------------------------------------------------------- #
            if quit_event.is_set():
                log.debug("Exiting loop")
                break

            # ----------------------------------------------------------------- #
            # [1] A-t-on une nouvelle requete de l'utilisateur ?
            # ----------------------------------------------------------------- #
            if user_request.has_changed():
                # -------------------------------------------------------------
                # Détermine l'identifiant du container correspondant au mode demandé (ex: "By Genre")
                # -------------------------------------------------------------
                container_id = wrapper.find_child_id(wrapper.music_container_id, user_request.get('mode'))
                if container_id is None:
                    log.fatal(f"Could not locate a '{user_request.get('mode')}' container under 'Music'.")
                    return
                # -------------------------------------------------------------
                # Détermine l'identifiant du container correspondant au genre demandé (ex: "Blues")
                # -------------------------------------------------------------
                genre_id = wrapper.find_child_id(container_id, user_request.get('genre'))
                if genre_id is None:
                    log.fatal(
                        f"Could not locate a '{user_request.get('genre')}' container under '{user_request.get('mode')}'.")
                    return
                # -------------------------------------------------------------
                # List the MP3 files of the container, and send them to the Music object.
                # -------------------------------------------------------------
                log.info(f"Current genre is '{user_request.get('genre')}'")
                wrapper.get_file_urls(genre_id)
                musics.discover_tracks(wrapper.get_mp3_items())
                musics.shuffle_playlist()
                # musics.list_all()
                # On acquitte la prise en compte du changement.
                user_request.ack_has_changed()

            # -------------------------------------------------------------
            # 2: Play MP3 files
            # -------------------------------------------------------------
            if lecture_task is None:
                log.debug("Start playing a new file")
                lecture_task = asyncio.create_task(musics.play_random_async())
                await lecture_task
                display_task = asyncio.create_task(show_clip_info())
            # -------------------------------------------------------------
            # 3: Check if the MP3 file is still playing
            # -------------------------------------------------------------
            else:
                if musics.isStopped():
                    lecture_task = None
                    log.debug("End playing]")
            # --------------------------------------------------------------------
            # Boucle rythmée à 1 seconde.
            # --------------------------------------------------------------------
            await asyncio.sleep(1)
    # --------------------------------------------------------------------
    # Sortie de la boucle
    # --------------------------------------------------------------------
    finally:
        log.warning("End loop")
        refresh_task.cancel()
        await refresh_task
        log.info("Shutdown complete")


# ---------------------------------------------------------
# Programme Principal
# ---------------------------------------------------------
async def main():
    # On exécute le Setup
    setup()
    # On lance la boucle (si on a un serveur DLNA)
    if wrapper.server_control_url:
        await loop()
    keyboard_ctrl.stop()


# -------------------------------------------------------------
# Launch Main Program (EventLoop)
# -------------------------------------------------------------
if __name__ == "__main__":
    # -----------------------------------------------------------------
    # Initialisation du logger
    # -----------------------------------------------------------------
    log = get_logger(__name__)
    # ---------------------------------------------------------
    # Initialisations des objets
    # ---------------------------------------------------------
    wrapper = DLNAWrapper()
    musics = DLNAMusic()
    user_request = DLNAUserRequest()
    # Create a Quit Event
    quit_event = asyncio.Event()
    # Initialise le Keyboard Listener thread
    keyboard_ctrl = KeyboardController(on_key_press, quit_event)
    # ---------------------------------------------------------
    # Lancement de l'Event Loop
    # ---------------------------------------------------------
    asyncio.run(main())
