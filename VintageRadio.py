# coding: UTF-8
# ==================================================================
# VintageRadio.py
# ==================================================================
# VintageRadio - Programme principal
# David de Lorenzo (2026)
# ==================================================================
import asyncio

from lib.dlna_music import DLNAMusic
from lib.dlna_listing import *
from lib.dlna_preferences import *
from lib.dlna_user_request import DLNAUserRequest
from lib.dlna_network_wrapper import DLNAWrapper
from lib.dlna_logger import get_logger
from typing import Optional
import logging


# --------------------------------------------------------------------- #
# Main initialisation
# --------------------------------------------------------------------- #
def setup():
    # -----------------------------------------------------------------
    # Initialisation du logger
    # -----------------------------------------------------------------
    log = get_logger(__name__)
    log.info("Start Setup")
    # -----------------------------------------------------------------
    # On ajoute un callback pour actualiser les modes et genre demandés
    musics.refresh_request_callback = user_request.refresh_user_request

    # -----------------------------------------------------------------
    # 1️⃣ Try to load a previously saved server
    # -----------------------------------------------------------------
    server_control_url: Optional[str] = None
    preferred_server_url = load_preferred_server()
    log.debug("preferred server url: %s", preferred_server_url)
    # -----------------------------------------------------------------
    # If we have a saved description URL, verify that it is still reachable
    # -----------------------------------------------------------------
    if preferred_server_url:
        log.info(f"Trying previously saved server: {preferred_server_url}")
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
            save_preferred(server_control_url)
    # -----------------------------------------------------------------
    # At this point we have a valid control URL
    # -----------------------------------------------------------------
    log.info(f"\nUsing ContentDirectory control URL: {server_control_url}")
    assert server_control_url is not None
    wrapper.set_server(server_control_url)

    # -------------------------------------------------------------
    # Première lecture du fichier de demande
    # -------------------------------------------------------------
    user_request.load_user_request()
    wrapper.find_music_container()
    log.info("End Setup")

# -----------------------------------------------------------------
# Boucle principale
# -----------------------------------------------------------------
async def loop():
    log = logging.getLogger(__name__)
    log.debug(">> Loop")

    if user_request.has_changed():
        # -------------------------------------------------------------
        # 1️⃣ Détermine l'identifiant du container correspondant au mode demandé (ex: "By Genre")
        # -------------------------------------------------------------
        container_id = wrapper.find_child_id(wrapper.music_container_id, user_request.get('mode'))
        if container_id is None:
            log.fatal(f"Could not locate a '{user_request.get('mode')}' container under 'Music'.")
            return

        # -------------------------------------------------------------
        # 2️⃣ Détermine l'identifiant du container correspondant au genre demandé (ex: "Blues")
        # -------------------------------------------------------------
        genre_id = wrapper.find_child_id(container_id, user_request.get('genre'))
        if genre_id is None:
            log.fatal(f"Could not locate a '{user_request.get('genre')}' container under '{user_request.get('mode')}'.")
            return

        # -------------------------------------------------------------
        # 3️⃣ List the MP3 files of the container, and send them to the Music object.
        # -------------------------------------------------------------
        log.info(f"Current genre is '{user_request.get('genre')}'")
        wrapper.get_file_urls(genre_id)
        musics.discover_tracks(wrapper.get_mp3_items())
        musics.shuffle_playlist()
        # musics.list_all()

    # --------------------------------------------------------------------
    # Reload user request (json file)
    # --------------------------------------------------------------------
    asyncio.create_task(musics.delayed_callback())  # fire and forget

    # -------------------------------------------------------------
    # 4️⃣ Play MP3 files
    # -------------------------------------------------------------
    log.debug("- Start playing...")
    # musics.play_random(0.5)
    lecture = asyncio.create_task(musics.play_random_async())

    # --------------------------------------------------------------------
    await lecture
    log.debug("End Loop")

# ---------------------------------------------------------
# Programme Principal
# ---------------------------------------------------------
async def main():
    # On exécute le Setup
    setup()
    # On lance la boucle
    await loop()

# -------------------------------------------------------------
# Launch Main Program
# -------------------------------------------------------------
if __name__ == "__main__":
    # ---------------------------------------------------------
    # Initialisations
    # ---------------------------------------------------------
    wrapper = DLNAWrapper()
    musics = DLNAMusic()
    user_request = DLNAUserRequest()
    # ---------------------------------------------------------
    # Programme
    # ---------------------------------------------------------
    asyncio.run(main())