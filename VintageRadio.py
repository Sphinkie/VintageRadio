# coding: UTF-8
# ==================================================================
# VintageRadio.py
# ==================================================================
# VintageRadio - Programme principal
# David de Lorenzo (2026)
# ==================================================================
from lib.dlna_music import DLNAMusic
from lib.dlna_listing import *
from lib.dlna_preferences import *
from lib.dlna_user_request import DLNAUserRequest
from lib.dlna_network_wrapper import DLNAWrapper
from typing import Optional


# --------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------- #
def main():
    # -----------------------------------------------------------------
    # Initialisation
    # -----------------------------------------------------------------
    wrapper = DLNAWrapper()
    musics = DLNAMusic()
    user_request = DLNAUserRequest()

    # On ajoute un callback pour actualiser les modes et genre
    musics.after_track_callback = user_request.refresh_user_request

    # -----------------------------------------------------------------
    # 1️⃣ Try to load a previously saved server
    # -----------------------------------------------------------------
    server_control_url: Optional[str] = None
    preferred_server_url = load_preferred_server()
    # print(preferred_desc_url)

    # -----------------------------------------------------------------
    # If we have a saved description URL, verify that it is still reachable
    # -----------------------------------------------------------------
    if preferred_server_url:
        print(f"Trying previously saved server: {preferred_server_url}")
        ctrl = resolve_control(preferred_server_url)
        if ctrl:
            server_control_url = ctrl
            print("Saved server is reachable.")
        else:
            print("Saved server could not be reached or does not expose ContentDirectory.")

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
    print(f"\nUsing ContentDirectory control URL: {server_control_url}")
    assert server_control_url is not None
    wrapper.set_server(server_control_url)

    # Première lecture du fichier de demande
    user_request.load_user_request()
    # -------------------------------------------------------------
    # Détermine l'identifiant du Container MUSIC
    # -------------------------------------------------------------
    ROOT_ID = "0"  # the root container (Music / Photo / Video)
    # “Music” – we assume it is a direct child of the root
    music_container_id = wrapper.find_child_id(ROOT_ID, "Music")
    if music_container_id is None:
        music_container_id = wrapper.find_child_id(ROOT_ID, "Musique")
    if music_container_id is None:
        print("Could not locate a 'Music' container on the server.")
        return

    # -------------------------------------------------------------
    # Boucle principale
    # -------------------------------------------------------------
    while True:
        # print(f"Loop")

        if user_request.has_changed():
            # -------------------------------------------------------------
            # 1️⃣ Détermine l'identifiant du container correspondant au mode demandé (ex: "By Genre")
            # -------------------------------------------------------------
            container_id = wrapper.find_child_id(music_container_id, user_request.get('mode'))
            if container_id is None:
                print(f"Could not locate a '{user_request.get('mode')}' container under 'Music'.")
                return

            # -------------------------------------------------------------
            # 2️⃣ Détermine l'identifiant du container correspondant au genre demandé (ex: "Blues")
            # -------------------------------------------------------------
            genre_id = wrapper.find_child_id(container_id, user_request.get('genre'))
            if genre_id is None:
                print(f"Could not locate a '{user_request.get('genre')}' container under '{user_request.get('mode')}'.")
                return

            # -------------------------------------------------------------
            # 3️⃣ List the MP3 files of the container, and send them to the Music object.
            # -------------------------------------------------------------
            wrapper.get_file_urls(genre_id)
            musics.discover_tracks(wrapper.get_mp3_items())
            musics.shuffle_playlist()
            musics.list_all()

        # -------------------------------------------------------------
        # 4️⃣ Play MP3 files
        # -------------------------------------------------------------
        print("\n--- Start playing...")
        musics.play_random(0.5)

        # --------------------------------------------------------------------
        # Invoke the optional hook – this is where we will reload request.json
        # TODO: A faire au bout de 10 secondes de playout
        # --------------------------------------------------------------------
        if callable(musics.after_track_callback):
            musics.after_track_callback()
        # --------------------------------------------------------------------


# -------------------------------------------------------------
# Launch Main Program
# -------------------------------------------------------------
if __name__ == "__main__":
    main()
